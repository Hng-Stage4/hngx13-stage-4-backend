# Email Service

A microservice for asynchronous email sending with multiple provider support, circuit breaker pattern, and comprehensive monitoring.

## Features

- **Asynchronous Processing**: RabbitMQ-based message queuing for reliable email delivery
- **Multiple Email Providers**: SMTP, SendGrid, Mailgun, and Gmail API support with automatic failover
- **Circuit Breaker**: Prevents cascade failures when providers are down
- **Retry Mechanism**: Exponential backoff retry with dead letter queue
- **Template Integration**: Fetches and renders templates from Template Service
- **Health Monitoring**: Comprehensive health checks for all dependencies
- **Metrics**: Prometheus-compatible metrics for monitoring
- **Structured Logging**: JSON logging with correlation IDs

## Architecture

```
API Gateway → RabbitMQ → Email Service → Template Service
                      ↓
                 Status Updates
```

## Quick Start

### Prerequisites

- Python 3.9+
- RabbitMQ
- Redis
- PostgreSQL (for Template Service)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd email-service
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the service:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ hostname | localhost |
| `RABBITMQ_PORT` | RabbitMQ port | 5672 |
| `RABBITMQ_USER` | RabbitMQ username | guest |
| `RABBITMQ_PASSWORD` | RabbitMQ password | guest |
| `REDIS_HOST` | Redis hostname | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `SMTP_HOST` | SMTP server hostname | - |
| `SMTP_PORT` | SMTP server port | 587 |
| `SMTP_USER` | SMTP username | - |
| `SMTP_PASSWORD` | SMTP password | - |
| `SENDGRID_API_KEY` | SendGrid API key | - |
| `MAILGUN_API_KEY` | Mailgun API key | - |
| `TEMPLATE_SERVICE_URL` | Template service URL | <http://template-service:8003> |

## API Endpoints

### Health Check

```
GET /api/health
```

Returns service health status including database, Redis, and RabbitMQ connectivity.

### Metrics

```
GET /api/metrics
```

Returns Prometheus-formatted metrics.

## Message Format

Email messages are sent via RabbitMQ with the following JSON structure:

```json
{
  "correlation_id": "unique-request-id",
  "to_email": "recipient@example.com",
  "template_id": "welcome_template",
  "variables": {
    "user_name": "John Doe",
    "company": "Example Corp"
  },
  "priority": "normal",
  "scheduled_at": null,
  "retry_count": 0
}
```

## Email Providers

The service supports multiple email providers with automatic failover:

1. **SMTP**: Direct SMTP server connection
2. **SendGrid**: Cloud email service
3. **Mailgun**: Transactional email service
4. **Gmail API**: Google Gmail API (requires OAuth setup)

Configure at least one provider for the service to function.

## Circuit Breaker

- **Failure Threshold**: 5 consecutive failures
- **Recovery Timeout**: 60 seconds
- Automatically opens when threshold is reached
- Half-open state allows testing recovery

## Retry Logic

- **Max Retries**: 3 attempts
- **Base Delay**: 5 seconds
- **Exponential Backoff**: delay × (2 ^ (retry_count - 1))
- **Jitter**: ±50% randomization
- Failed messages go to dead letter queue

## Monitoring

### Metrics Tracked

- `email_service_requests_total`: HTTP request count
- `email_service_request_duration_seconds`: Request latency
- `email_service_errors_total`: Error count
- `email_service_emails_sent_total`: Successful sends
- `email_service_emails_failed_total`: Failed sends
- `email_service_delivery_time_seconds`: End-to-end delivery time
- `email_service_queue_messages_processed_total`: Messages processed

### Health Checks

- **Database**: PostgreSQL connectivity (Template Service)
- **Redis**: Cache connectivity
- **RabbitMQ**: Message queue connectivity

## Logging

All logs are structured JSON with the following fields:

```json
{
  "timestamp": "2025-11-12T08:00:00.000Z",
  "level": "INFO",
  "service_name": "email-service",
  "correlation_id": "unique-id",
  "event": "email_sent",
  "message": "Email sent successfully"
}
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Linting
flake8 app/

# Type checking
mypy app/

# Formatting
black app/
```

## Docker

Build and run with Docker:

```bash
docker build -t email-service .
docker run -p 8001:8001 email-service
```

## Production Deployment

- Use environment-specific configuration
- Set up proper monitoring with Prometheus/Grafana
- Configure log aggregation
- Set up RabbitMQ clustering for high availability
- Use Redis cluster for caching
- Implement proper secrets management

## Troubleshooting

### Common Issues

1. **Connection refused to RabbitMQ/Redis**
   - Check service availability
   - Verify connection settings
   - Check network connectivity

2. **Email delivery failures**
   - Verify provider credentials
   - Check provider rate limits
   - Review circuit breaker status

3. **Template rendering errors**
   - Ensure Template Service is running
   - Check template ID exists
   - Verify variable names match

### Logs Location

- Application logs: `logs/email-service.log`
- Structured JSON logs for all events

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.
