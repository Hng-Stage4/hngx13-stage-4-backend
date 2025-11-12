<?php

namespace App\Services;

use Prometheus\CollectorRegistry;
use Prometheus\Storage\Redis;
use Prometheus\RenderTextFormat;
use GuzzleHttp\Client;
use App\Traits\JsonLogging;
use Exception;

/**
 * MetricsService
 *
 * Collects and exposes metrics for monitoring the Push Notification Service.
 * Integrates structured JSON logging for observability.
 */
class MetricsService
{
    use JsonLogging;

    private CollectorRegistry $registry;
    private string $namespace = 'push_service';
    private ?Client $httpClient = null;
    private string $serviceName = 'push_metrics_service';

    /**
     * Constructor
     *
     * Initializes Prometheus Redis storage and RabbitMQ HTTP client for queue metrics.
     */
    public function __construct()
    {
        Redis::setDefaultOptions([
            'host' => config('database.redis.default.host'),
            'port' => config('database.redis.default.port'),
            'timeout' => 0.1,
        ]);

        $this->registry = CollectorRegistry::getDefault();
        $this->httpClient = new Client([
            'auth' => [
                config('rabbitmq.management_user'),
                config('rabbitmq.management_password'),
            ],
            'base_uri' => sprintf(
                'http://%s:%d/api/',
                config('rabbitmq.management_host'),
                config('rabbitmq.management_port')
            ),
            'timeout' => 2.0,
        ]);
    }

    /**
     * Increment total messages consumed from RabbitMQ
     */
    public function incrementMessagesConsumed(): void
    {
        $counter = $this->registry->getOrRegisterCounter(
            $this->namespace,
            'messages_consumed_total',
            'Total messages consumed from RabbitMQ'
        );
        $counter->inc();

        $this->logJson(
            'info',
            $this->serviceName,
            'messages_consumed_incremented',
            'Incremented messages_consumed_total counter'
        );
    }

    /**
     * Increment total notifications sent by status
     *
     * @param string $status Notification send status (e.g., success, failed)
     */
    public function incrementNotificationsSent(string $status): void
    {
        $counter = $this->registry->getOrRegisterCounter(
            $this->namespace,
            'notifications_sent_total',
            'Total notifications sent by status',
            ['status']
        );
        $counter->inc([$status]);

        $this->logJson(
            'info',
            $this->serviceName,
            'notifications_sent_incremented',
            "Incremented notifications_sent_total counter with status: {$status}"
        );
    }

    /**
     * Increment total notification retries
     */
    public function incrementRetries(): void
    {
        $counter = $this->registry->getOrRegisterCounter(
            $this->namespace,
            'notification_retries_total',
            'Total number of notification retry attempts'
        );
        $counter->inc();

        $this->logJson(
            'info',
            $this->serviceName,
            'notification_retries_incremented',
            'Incremented notification_retries_total counter'
        );
    }

    /**
     * Record notification processing duration
     *
     * @param float $seconds Duration in seconds
     */
    public function recordDuration(float $seconds): void
    {
        $histogram = $this->registry->getOrRegisterHistogram(
            $this->namespace,
            'notification_duration_seconds',
            'Notification processing duration in seconds',
            [],
            [0.1, 0.5, 1, 2, 5, 10]
        );
        $histogram->observe($seconds);

        $this->logJson(
            'info',
            $this->serviceName,
            'notification_duration_recorded',
            "Recorded notification duration: {$seconds} seconds"
        );
    }

    /**
     * Update queue metrics (messages ready, unacknowledged, and lag)
     */
    public function updateQueueMetrics(): void
    {
        try {
            $response = $this->httpClient->get(
                'queues/' .
                urlencode(config('rabbitmq.vhost')) . '/' .
                urlencode(config('rabbitmq.queues.push'))
            );

            $data = json_decode($response->getBody(), true);
            $messagesReady = $data['messages_ready'] ?? 0;
            $messagesUnacked = $data['messages_unacknowledged'] ?? 0;
            $lagSeconds = $this->estimateQueueLag($data);

            $this->setGauge('queue_messages_ready', 'Messages waiting in queue', $messagesReady);
            $this->setGauge('queue_messages_unacknowledged', 'Unacknowledged messages (being processed)', $messagesUnacked);
            $this->setGauge('queue_message_lag_seconds', 'Estimated queue message lag in seconds', $lagSeconds);

            $this->logJson(
                'info',
                $this->serviceName,
                'queue_metrics_updated',
                "Queue metrics updated: ready={$messagesReady}, unacked={$messagesUnacked}, lag={$lagSeconds}s"
            );

        } catch (Exception $e) {
            $this->logJson(
                'error',
                $this->serviceName,
                'queue_metrics_error',
                "Failed to update queue metrics: {$e->getMessage()}"
            );
        }
    }

    /**
     * Helper to set a gauge metric
     *
     * @param string $name Gauge name
     * @param string $help Description
     * @param float $value Value to set
     */
    private function setGauge(string $name, string $help, float $value): void
    {
        $gauge = $this->registry->getOrRegisterGauge(
            $this->namespace,
            $name,
            $help
        );
        $gauge->set($value);
    }

    /**
     * Estimate lag using RabbitMQ timestamps (if available)
     *
     * @param array $data Queue data from RabbitMQ API
     * @return float Lag in seconds
     */
    private function estimateQueueLag(array $data): float
    {
        $now = microtime(true);
        if (!empty($data['message_stats']['publish_details']['last_event'])) {
            $lastPublished = strtotime($data['message_stats']['publish_details']['last_event']);
            if ($lastPublished) {
                return max(0, $now - $lastPublished);
            }
        }
        return 0.0;
    }

    /**
     * Render metrics in Prometheus text format
     *
     * @return string
     */
    public function render(): string
    {
        $this->updateQueueMetrics();
        $renderer = new RenderTextFormat();
        return $renderer->render($this->registry->getMetricFamilySamples());
    }
}
