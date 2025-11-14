# api-gateway/app/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Total API requests received
REQUESTS_TOTAL = Counter(
    "api_gateway_requests_total",
    "Total API Gateway requests",
    ["endpoint", "method"]
)

# Total failed requests
REQUESTS_FAILED_TOTAL = Counter(
    "api_gateway_requests_failed_total",
    "Total failed requests in API Gateway",
    ["endpoint", "method"]
)

# Request latency
REQUEST_DURATION_SECONDS = Histogram(
    "api_gateway_request_duration_seconds",
    "API Gateway request duration in seconds",
    ["endpoint", "method"]
)

# Notifications routed by type (email/push)
NOTIFICATION_TYPE_TOTAL = Counter(
    "api_gateway_notification_type_total",
    "Total notifications routed by type",
    ["type"]
)

# Optional: Service health (1 = healthy, 0 = unhealthy)
SERVICE_HEALTH = Gauge(
    "api_gateway_up",
    "API Gateway service health"
)

def prometheus_metrics():
    """Return Prometheus metrics as HTTP response"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
