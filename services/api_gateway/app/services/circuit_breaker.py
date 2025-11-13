# ============================================
# api-gateway/app/services/circuit_breaker.py
# ============================================
import time
import logging
from enum import Enum
from app.config.settings import settings

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self):
        self.failure_count = 0
        self.failure_threshold = settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.timeout = settings.CIRCUIT_BREAKER_TIMEOUT
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func):
        """
        Execute function with circuit breaker protection
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker CLOSED")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker OPENED")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.timeout
        )
