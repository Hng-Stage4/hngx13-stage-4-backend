import time
from functools import wraps
from fastapi import Request
from app.services.metrics import NOTIFICATION_TYPE_TOTAL, REQUEST_DURATION_SECONDS, REQUESTS_FAILED_TOTAL, REQUESTS_TOTAL


def monitor_endpoint(notification_type: str = None):
    """
    Decorator to monitor API Gateway endpoints
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object
            request: Request = kwargs.get("request")
            endpoint = request.url.path if request else "unknown"
            method = request.method if request else "unknown"
            
            REQUESTS_TOTAL.labels(endpoint=endpoint, method=method).inc()
            start_time = time.time()
            
            try:
                response = await func(*args, **kwargs)
                # Increment notification type counter if applicable
                if notification_type:
                    NOTIFICATION_TYPE_TOTAL.labels(type=notification_type).inc()
                return response
            except Exception:
                REQUESTS_FAILED_TOTAL.labels(endpoint=endpoint, method=method).inc()
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_DURATION_SECONDS.labels(endpoint=endpoint, method=method).observe(duration)
        return wrapper
    return decorator
