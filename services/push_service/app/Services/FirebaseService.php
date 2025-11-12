<?php

namespace App\Services;

use Kreait\Firebase\Factory;
use Kreait\Firebase\Messaging\CloudMessage;
use Kreait\Firebase\Messaging\Notification;
use App\DTOs\PushNotificationDTO;
use App\Traits\JsonLogging;
use Exception;

/**
 * FirebaseService
 *
 * Handles sending push notifications via Firebase Cloud Messaging (FCM).
 * Integrates with Circuit Breaker to manage service reliability.
 *
 * @package App\Services
 */
class FirebaseService
{
    use JsonLogging;

    private $messaging;
    private CircuitBreaker $circuitBreaker;
    private string $serviceName = 'push_notification_service';

    /**
     * Constructor
     *
     * Initializes Firebase Messaging and Circuit Breaker.
     */
    public function __construct()
    {
        $factory = (new Factory)->withServiceAccount(config('firebase.credentials'));
        $this->messaging = $factory->createMessaging();
        $this->circuitBreaker = new CircuitBreaker($this->serviceName);
    }

    /**
     * Send Push Notification
     *
     * Checks circuit breaker state before sending the notification.
     * Records success or failure to the circuit breaker.
     * All events are logged in JSON format using the JsonLogging trait.
     *
     * @param PushNotificationDTO $dto Data Transfer Object containing notification details
     * @return array Result of the send operation
     * @throws Exception If the circuit breaker is open
     */
    public function sendNotification(PushNotificationDTO $dto): array
    {
        // Check if the circuit breaker is open
        if ($this->circuitBreaker->isOpen()) {
            $this->logJson(
                'warning',
                $this->serviceName,
                'fcm_circuit_open',
                "FCM circuit breaker is open for notification {$dto->notification_id}"
            );

            throw new Exception('FCM service temporarily unavailable');
        }

        try {
            // Create notification object
            $notification = Notification::create($dto->title, $dto->body);
            if ($dto->image) {
                $notification = $notification->withImageUrl($dto->image);
            }

            // Prepare additional message data
            $messageData = array_filter([
                'notification_id' => $dto->notification_id,
                'link' => $dto->link,
                ...(is_array($dto->data) ? $dto->data : []),
            ]);

            // Build CloudMessage
            $message = CloudMessage::withTarget('token', $dto->push_token)
                ->withNotification($notification)
                ->withData($messageData);

            // Send notification
            $result = $this->messaging->send($message);

            // Record successful delivery
            $this->circuitBreaker->recordSuccess();

            // Log success
            $this->logJson(
                'info',
                $this->serviceName,
                'push_sent',
                "Push notification sent successfully for notification {$dto->notification_id}"
            );

            return [
                'success' => true,
                'message_id' => $result,
            ];

        } catch (\Kreait\Firebase\Exception\Messaging\InvalidMessage $e) {
            $this->logJson(
                'error',
                $this->serviceName,
                'invalid_message',
                "Invalid FCM message for notification {$dto->notification_id}: {$e->getMessage()}"
            );

            return [
                'success' => false,
                'error' => 'Invalid message format: ' . $e->getMessage(),
                'retryable' => false,
            ];

        } catch (\Kreait\Firebase\Exception\Messaging\NotFound $e) {
            $this->logJson(
                'warning',
                $this->serviceName,
                'token_not_found',
                "FCM token not found for notification {$dto->notification_id}"
            );

            return [
                'success' => false,
                'error' => 'Push token not found or expired',
                'retryable' => false,
            ];

        } catch (Exception $e) {
            $this->circuitBreaker->recordFailure();

            $this->logJson(
                'error',
                $this->serviceName,
                'fcm_service_error',
                "FCM service error for notification {$dto->notification_id}: {$e->getMessage()}"
            );

            return [
                'success' => false,
                'error' => $e->getMessage(),
                'retryable' => true,
            ];
        }
    }
}
