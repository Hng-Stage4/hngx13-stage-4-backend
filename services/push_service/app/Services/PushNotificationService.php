<?php

namespace App\Services;

use App\Models\NotificationLog;
use App\DTOs\PushNotificationDTO;
use App\Enums\NotificationStatus;
use Illuminate\Support\Facades\Http;
use App\Traits\JsonLogging;
use Illuminate\Support\Facades\Crypt;

/**
 * PushNotificationService
 *
 * Handles processing and sending push notifications with retry logic.
 * Responsible for recording all notification-level metrics:
 *   - notifications_sent_total (success, failed, error)
 *   - notification_retries_total
 *   - notification_duration_seconds
 *
 * Logs are recorded in structured JSON for observability.
 */
class PushNotificationService
{
    use JsonLogging;

    private FirebaseService $firebaseService;
    private MetricsService $metricsService;
    private int $maxRetries;
    private int $retryDelay;
    private string $serviceName = 'push_notification_service';

    /**
     * Constructor
     *
     * @param FirebaseService $firebaseService Service handling Firebase notification sending
     * @param MetricsService $metricsService Service handling Prometheus metrics
     */
    public function __construct(FirebaseService $firebaseService, MetricsService $metricsService)
    {
        $this->firebaseService = $firebaseService;
        $this->metricsService = $metricsService;
        $this->maxRetries = config('services.max_retry_attempts');
        $this->retryDelay = config('services.retry_delay_seconds');
    }

    /**
     * Process a single push notification
     *
     * Performs idempotency check, creates or updates NotificationLog,
     * sends the notification with retry logic, and records metrics.
     *
     * @param array $data Notification data payload
     * @return array Result of processing, including success, error message, and retryable flag
     */
    public function processNotification(array $data): array
    {
        $startTime = microtime(true);

        try {
            $dto = PushNotificationDTO::fromArray($data);

            $log = NotificationLog::where('notification_id', $dto->notification_id)->first();

            if ($log && $log->status === NotificationStatus::DELIVERED->value) {
                $this->logJson('info', $this->serviceName, 'notification_already_delivered', 'Notification has already been delivered', $dto->notification_id);
                return ['success' => true, 'message' => 'Already delivered'];
            }

            if (!$log) {
                $log = NotificationLog::create([
                    'notification_id' => $dto->notification_id,
                    'notification_type' => 'push',
                    'user_id' => $dto->user_id,
                    'push_token' => Crypt::encryptString($dto->push_token),
                    'status' => NotificationStatus::PENDING->value,
                    'metadata' => Crypt::encryptString(json_encode($data)),
                ]);
            }

            $result = $this->sendWithRetry($dto, $log);

            $duration = microtime(true) - $startTime;
            $this->metricsService->recordDuration($duration);

            return $result;

        } catch (\Exception $e) {
            $duration = microtime(true) - $startTime;
            $this->metricsService->recordDuration($duration);
            $this->metricsService->incrementNotificationsSent('error');

            $this->logJson('error', $this->serviceName, 'notification_processing_failed', "Failed to process notification: {$e->getMessage()}", $data['notification_id'] ?? null);

            return [
                'success' => false,
                'error' => $e->getMessage(),
                'retryable' => true,
            ];
        }
    }

    /**
     * Send notification with retry logic
     *
     * Implements exponential backoff and increments retries metrics.
     * Marks notifications as DELIVERED or FAILED in NotificationLog.
     *
     * @param PushNotificationDTO $dto
     * @param NotificationLog $log
     * @return array Result including success, error message, retryable flag
     */
    private function sendWithRetry(PushNotificationDTO $dto, NotificationLog $log): array
    {
        $attempt = $log->retry_count ?? 0;

        while ($attempt < $this->maxRetries) {
            $result = $this->firebaseService->sendNotification($dto);

            if ($result['success']) {
                $log->update([
                    'status' => NotificationStatus::DELIVERED->value,
                    'sent_at' => now(),
                    'delivered_at' => now(),
                    'retry_count' => $attempt,
                ]);

                $this->sendStatusUpdate($dto->notification_id, NotificationStatus::DELIVERED);
                $this->metricsService->incrementNotificationsSent('success');
                $this->logJson('info', $this->serviceName, 'notification_delivered', 'Notification delivered', $dto->notification_id);

                return ['success' => true];
            }

            if (!($result['retryable'] ?? true)) {
                $log->update([
                    'status' => NotificationStatus::FAILED->value,
                    'error_message' => $result['error'],
                    'retry_count' => $attempt,
                ]);

                $this->sendStatusUpdate($dto->notification_id, NotificationStatus::FAILED, $result['error']);
                $this->metricsService->incrementNotificationsSent('failed');
                $this->logJson('error', $this->serviceName, 'notification_failed', "Failed: {$result['error']}", $dto->notification_id);

                return ['success' => false, 'error' => $result['error'], 'retryable' => false];
            }

            $attempt++;
            $delay = $this->retryDelay * pow(2, $attempt - 1);
            $log->update(['retry_count' => $attempt]);

            $this->metricsService->incrementRetries();
            $this->logJson('warning', $this->serviceName, 'notification_retry', "Retry attempt {$attempt}, delay {$delay}s", $dto->notification_id);
            sleep($delay);
        }

        $log->update([
            'status' => NotificationStatus::FAILED->value,
            'error_message' => 'Max retry attempts exceeded',
        ]);

        $this->sendStatusUpdate($dto->notification_id, NotificationStatus::FAILED, 'Max retries exceeded');
        $this->metricsService->incrementNotificationsSent('failed');
        $this->logJson('error', $this->serviceName, 'notification_max_retries_exceeded', 'Notification failed after max retries', $dto->notification_id);

        return ['success' => false, 'error' => 'Max retries exceeded', 'retryable' => false];
    }

    /**
     * Send status update to API Gateway
     *
     * @param string $notificationId
     * @param NotificationStatus $status
     * @param string|null $error Optional error message
     * @return void
     */
    private function sendStatusUpdate(string $notificationId, NotificationStatus $status, ?string $error = null): void
    {
        try {
            $apiGatewayUrl = config('services.api_gateway.url');

            $payload = [
                'notification_id' => $notificationId,
                'status' => $status->value,
                'timestamp' => now()->toIso8601String(),
            ];

            if ($error) $payload['error'] = $error;

            Http::timeout(5)->post("{$apiGatewayUrl}/api/v1/push/status/", $payload);

            $this->logJson('info', $this->serviceName, 'status_update_sent', 'Status update sent to API Gateway', $notificationId);

        } catch (\Exception $e) {
            $this->logJson('error', $this->serviceName, 'status_update_failed', "Failed to send status update: {$e->getMessage()}", $notificationId);
        }
    }
}
