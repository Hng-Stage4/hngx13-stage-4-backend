<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Facades\DB;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use App\Traits\JsonLogging;

class HealthController extends Controller
{
    use JsonLogging;

    private string $serviceName = 'push_notification_service';

    /**
     * Health and readiness check
     * Combines DB, Redis, RabbitMQ checks
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function health()
    {
        $status = 'healthy';
        $checks = [];

        // Database check
        try {
            DB::connection()->getPdo();
            $checks['database'] = 'healthy';
        } catch (\Exception $e) {
            $checks['database'] = 'unhealthy';
            $status = 'degraded';
            $this->logJson(
                'error',
                $this->serviceName,
                'database_unhealthy',
                $e->getMessage()
            );
        }

        // Redis check
        try {
            Redis::ping();
            $checks['redis'] = 'healthy';
        } catch (\Exception $e) {
            $checks['redis'] = 'unhealthy';
            $status = 'degraded';
            $this->logJson(
                'error',
                $this->serviceName,
                'redis_unhealthy',
                $e->getMessage()
            );
        }

        // RabbitMQ check
        try {
            $config = config('rabbitmq');
            $connection = new AMQPStreamConnection(
                $config['host'],
                $config['port'],
                $config['user'],
                $config['password'],
                $config['vhost']
            );
            $connection->close();
            $checks['rabbitmq'] = 'healthy';
        } catch (\Exception $e) {
            $checks['rabbitmq'] = 'unhealthy';
            $status = 'degraded';
            $this->logJson(
                'error',
                $this->serviceName,
                'rabbitmq_unhealthy',
                $e->getMessage()
            );
        }

        $response = [
            'status' => $status,
            'service' => 'push-notification-service',
            'timestamp' => now()->toIso8601String(),
            'checks' => $checks,
        ];

        $statusCode = $status === 'healthy' ? 200 : 503;

        if ($status === 'degraded') {
            $this->logJson(
                'warning',
                $this->serviceName,
                'service_degraded',
                'Health check returned degraded status',
                null
            );
        }

        return response()->json($response, $statusCode);
    }
}
