<?php

namespace App\Traits;

use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

trait JsonLogging
{
    /**
     * Log an event in JSON format
     *
     * @param string $level Log level: info, warning, error
     * @param string $serviceName Name of the service
     * @param string $event Event name
     * @param string $message Message description
     * @param string|null $correlationId Optional correlation ID
     */
    public function logJson(
        string $level,
        string $serviceName,
        string $event,
        string $message,
        ?string $correlationId = null
    ): void {
        $log = [
            'timestamp' => now()->toIso8601String(),
            'level' => $level,
            'service_name' => $serviceName,
            'correlation_id' => $correlationId ?? request()->header('X-Correlation-ID', Str::uuid()->toString()),
            'event' => $event,
            'message' => $message,
        ];

        Log::{$level}(json_encode($log));
    }
}
