<?php

namespace App\Services;

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;
use App\Traits\JsonLogging;

/**
 * RabbitMQConsumerService
 *
 * Consumes messages from RabbitMQ and triggers PushNotificationService.
 * Responsible for queue-level metrics:
 *   - messages_consumed_total
 *   - queue gauges (messages_ready, unacknowledged, lag)
 *
 * Notification-level metrics are managed by PushNotificationService.
 */
class RabbitMQConsumerService
{
    use JsonLogging;

    private $connection;
    private $channel;
    private PushNotificationService $pushService;
    private MetricsService $metrics;
    private string $serviceName = 'rabbitmq_consumer_service';

    public function __construct(PushNotificationService $pushService, MetricsService $metrics)
    {
        $this->pushService = $pushService;
        $this->metrics = $metrics;
        $this->connect();
    }

    /**
     * Establish RabbitMQ connection, declare exchange/queues, and set QoS.
     *
     * @return void
     */
    private function connect(): void
    {
        $config = config('rabbitmq');

        $this->connection = new AMQPStreamConnection(
            $config['host'], $config['port'], $config['user'], $config['password'], $config['vhost']
        );

        $this->channel = $this->connection->channel();
        $this->channel->exchange_declare($config['exchange'], 'direct', false, true, false);
        $this->channel->queue_declare($config['queues']['push'], false, true, false, false);
        $this->channel->queue_declare($config['queues']['failed'], false, true, false, false);
        $this->channel->queue_bind($config['queues']['push'], $config['exchange'], 'push');

        $this->channel->basic_qos(null, 1, null);

        $this->logJson('info', $this->serviceName, 'rabbitmq_connected', 'RabbitMQ connection and queues established');
    }

    /**
     * Start consuming messages from the push queue.
     *
     * Processes messages using PushNotificationService and handles retries/failures.
     *
     * @return void
     */
    public function consume(): void
    {
        $callback = function (AMQPMessage $msg) {
            $this->metrics->incrementMessagesConsumed();
            $start = microtime(true);

            try {
                $data = json_decode($msg->body, true);
                if (json_last_error() !== JSON_ERROR_NONE) throw new \Exception('Invalid JSON payload');

                $result = $this->pushService->processNotification($data);

                if ($result['success']) {
                    $msg->ack();
                    $this->logJson('info', $this->serviceName, 'message_processed', 'Notification processed', $data['notification_id'] ?? null);
                } else {
                    if ($result['retryable'] ?? true) $msg->nack(true);
                    else {
                        $this->moveToFailedQueue($msg);
                        $msg->ack();
                        $this->logJson('error', $this->serviceName, 'message_failed', 'Notification moved to failed queue', $data['notification_id'] ?? null);
                    }
                }

            } catch (\Throwable $e) {
                $this->logJson('error', $this->serviceName, 'processing_error', "Error processing message: {$e->getMessage()}", $data['notification_id'] ?? null);
                $this->moveToFailedQueue($msg);
                $msg->ack();
            } finally {
                $duration = microtime(true) - $start;
                $this->metrics->recordDuration($duration); // Optional queue processing duration
            }
        };

        $this->channel->basic_consume(config('rabbitmq.queues.push'), '', false, false, false, false, $callback);

        $this->logJson('info', $this->serviceName, 'waiting_for_messages', 'Waiting for messages from RabbitMQ...');

        while ($this->channel->is_consuming()) $this->channel->wait();
    }

    /**
     * Move a failed message to the dead-letter queue.
     *
     * @param AMQPMessage $msg
     * @return void
     */
    private function moveToFailedQueue(AMQPMessage $msg): void
    {
        $failedMessage = new AMQPMessage(
            $msg->body,
            array_merge($msg->get_properties(), [
                'headers' => [
                    'x-failed-at' => time(),
                    'x-original-queue' => config('rabbitmq.queues.push'),
                ]
            ])
        );

        $this->channel->basic_publish($failedMessage, '', config('rabbitmq.queues.failed'));

        $this->logJson('info', $this->serviceName, 'message_moved_failed_queue', 'Message moved to failed queue', null);
    }

    public function __destruct()
    {
        if ($this->channel) $this->channel->close();
        if ($this->connection) $this->connection->close();
    }
}
