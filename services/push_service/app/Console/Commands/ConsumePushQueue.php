<?php

namespace App\Console\Commands;

use App\Services\MetricsService;
use Illuminate\Console\Command;
use App\Services\RabbitMQConsumerService;
use App\Services\PushNotificationService;
use App\Traits\JsonLogging;
use Exception;

/**
 * ConsumePushQueue
 *
 * Console command to consume messages from RabbitMQ and process push notifications.
 * Logs all events in JSON format.
 */
class ConsumePushQueue extends Command
{
    use JsonLogging;

    protected $signature = 'queue:consume-push';
    protected $description = 'Consume push notification messages from RabbitMQ';

    private string $serviceName = 'push_notification_consumer';

    /**
     * Execute the console command.
     *
     * @param PushNotificationService $pushService
     * @param MetricsService $metrics
     * @return int
     */
    public function handle(PushNotificationService $pushService, MetricsService $metrics): int
    {
        $this->info('Starting Push Notification Consumer...');
        $this->logJson(
            'info',
            $this->serviceName,
            'consumer_started',
            'Push Notification Consumer started'
        );

        try {
            $consumer = new RabbitMQConsumerService($pushService, $metrics);
            $consumer->consume();

            $this->logJson(
                'info',
                $this->serviceName,
                'consumer_completed',
                'Push Notification Consumer finished processing messages successfully'
            );

        } catch (Exception $e) {
            $this->logJson(
                'error',
                $this->serviceName,
                'consumer_error',
                'Push Notification Consumer encountered an error: ' . $e->getMessage()
            );

            $this->error('Consumer error: ' . $e->getMessage());
            return Command::FAILURE;
        }

        return Command::SUCCESS;
    }
}
