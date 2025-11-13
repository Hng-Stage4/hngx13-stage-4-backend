from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import prometheus_client

router = APIRouter()

# Define metrics
REQUESTS_TOTAL = prometheus_client.Counter(
    'email_service_requests_total',
    'Total HTTP requests handled',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = prometheus_client.Histogram(
    'email_service_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ERRORS_TOTAL = prometheus_client.Counter(
    'email_service_errors_total',
    'Total failed requests',
    ['method', 'endpoint', 'error_type']
)

UPTIME = prometheus_client.Gauge(
    'email_service_uptime_seconds',
    'Total uptime duration'
)

QUEUE_MESSAGES_PROCESSED = prometheus_client.Counter(
    'email_service_queue_messages_processed_total',
    'Total messages consumed'
)

EMAILS_SENT = prometheus_client.Counter(
    'email_service_emails_sent_total',
    'Total emails successfully sent'
)

EMAILS_FAILED = prometheus_client.Counter(
    'email_service_emails_failed_total',
    'Total failed sends'
)

DELIVERY_TIME = prometheus_client.Histogram(
    'email_service_delivery_time_seconds',
    'Time from enqueue to delivery'
)

QUEUE_LENGTH = prometheus_client.Gauge(
    'email_service_queue_length',
    'Current queue length'
)

WEBHOOK_EVENTS_RECEIVED = prometheus_client.Counter(
    'email_service_webhook_events_received_total',
    'Total webhook events received from providers'
)

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
