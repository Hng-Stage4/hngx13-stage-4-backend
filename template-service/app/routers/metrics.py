from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import prometheus_client

router = APIRouter()

# Define metrics
REQUESTS_TOTAL = prometheus_client.Counter(
    'template_service_requests_total',
    'Total HTTP requests handled',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = prometheus_client.Histogram(
    'template_service_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ERRORS_TOTAL = prometheus_client.Counter(
    'template_service_errors_total',
    'Total failed requests',
    ['method', 'endpoint', 'error_type']
)

UPTIME = prometheus_client.Gauge(
    'template_service_uptime_seconds',
    'Total uptime duration'
)

TEMPLATES_LOADED_TOTAL = prometheus_client.Counter(
    'template_service_templates_loaded_total',
    'Total templates fetched'
)

RENDER_DURATION = prometheus_client.Histogram(
    'template_service_render_duration_seconds',
    'Time to render templates'
)

VERSION_COUNT_TOTAL = prometheus_client.Gauge(
    'template_service_version_count_total',
    'Total template versions stored'
)

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
