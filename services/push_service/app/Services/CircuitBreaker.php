<?php

namespace App\Services;

use Illuminate\Support\Facades\Redis;
use App\Traits\JsonLogging;

/**
 * CircuitBreaker
 *
 * Manages the state of external service calls to prevent cascading failures.
 * Tracks failure count and transitions between CLOSED, OPEN, and HALF-OPEN states.
 * Logs all state changes using structured JSON logs.
 *
 * States:
 * - CLOSED: Normal operation
 * - OPEN: Calls are blocked
 * - HALF-OPEN: Limited calls allowed to test recovery
 *
 * Configuration is loaded from config/services.php
 */
class CircuitBreaker
{
    use JsonLogging;

    private string $serviceName;
    private int $failureThreshold;
    private int $timeout;
    private int $retryTimeout;

    /**
     * Constructor
     *
     * Initializes circuit breaker configuration.
     *
     * @param string $serviceName Name of the external service
     */
    public function __construct(string $serviceName)
    {
        $this->serviceName = $serviceName;
        $config = config('services.circuit_breaker');
        $this->failureThreshold = $config['failure_threshold'];
        $this->timeout = $config['timeout'];
        $this->retryTimeout = $config['retry_timeout'];
    }

    /**
     * Check if the circuit is open
     *
     * @return bool True if the circuit is open, false otherwise
     */
    public function isOpen(): bool
    {
        $state = Redis::get($this->getStateKey());

        if ($state === 'open') {
            $openedAt = Redis::get($this->getOpenedAtKey());

            if ($openedAt && (time() - $openedAt) > $this->retryTimeout) {
                $this->halfOpen();
                return false;
            }

            return true;
        }

        return false;
    }

    /**
     * Record a successful call
     *
     * Resets failure count and closes the circuit if necessary
     */
    public function recordSuccess(): void
    {
        Redis::del($this->getFailureCountKey());
        $this->close();
    }

    /**
     * Record a failed call
     *
     * Increments failure count and opens circuit if threshold is reached
     */
    public function recordFailure(): void
    {
        $failures = Redis::incr($this->getFailureCountKey());
        Redis::expire($this->getFailureCountKey(), $this->timeout);

        if ($failures >= $this->failureThreshold) {
            $this->open();
        }
    }

    /**
     * Open the circuit breaker
     *
     * Sets state to OPEN and logs the event
     */
    private function open(): void
    {
        Redis::setex($this->getStateKey(), $this->timeout, 'open');
        Redis::set($this->getOpenedAtKey(), time());

        $this->logJson(
            'error',
            $this->serviceName,
            'circuit_opened',
            "Circuit breaker OPENED for service {$this->serviceName}"
        );
    }

    /**
     * Close the circuit breaker
     *
     * Sets state to CLOSED and logs the event
     */
    private function close(): void
    {
        Redis::set($this->getStateKey(), 'closed');
        Redis::del($this->getOpenedAtKey());

        $this->logJson(
            'info',
            $this->serviceName,
            'circuit_closed',
            "Circuit breaker CLOSED for service {$this->serviceName}"
        );
    }

    /**
     * Set the circuit breaker to HALF-OPEN state
     *
     * Allows limited calls to test service recovery
     */
    private function halfOpen(): void
    {
        Redis::set($this->getStateKey(), 'half-open');

        $this->logJson(
            'warning',
            $this->serviceName,
            'circuit_half_open',
            "Circuit breaker HALF-OPEN for service {$this->serviceName}"
        );
    }

    /**
     * Get the Redis key for the circuit breaker state
     *
     * @return string
     */
    private function getStateKey(): string
    {
        return "circuit_breaker:{$this->serviceName}:state";
    }

    /**
     * Get the Redis key for the failure count
     *
     * @return string
     */
    private function getFailureCountKey(): string
    {
        return "circuit_breaker:{$this->serviceName}:failures";
    }

    /**
     * Get the Redis key for the timestamp when circuit was opened
     *
     * @return string
     */
    private function getOpenedAtKey(): string
    {
        return "circuit_breaker:{$this->serviceName}:opened_at";
    }
}
