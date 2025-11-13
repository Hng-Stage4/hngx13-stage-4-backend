# Email Service

A microservice for sending emails asynchronously with support for multiple email providers and delivery tracking.

## Features

- Asynchronous email sending via RabbitMQ queues
- Multiple email providers (SMTP, SendGrid, Mailgun, Gmail)
- Template rendering with variable substitution
- Delivery confirmations and bounce handling via webhooks
- Circuit breaker pattern for provider failover
- Metrics and monitoring with Prometheus
- Health checks

## Quick Start

### Running with Docker (Recommended)

1. **Standalone Mode** (with its own dependencies):
   ```bash
   cd services/email_service
   docker-compose up -d
   ```

2. **As part of the full system**:
   ```bash
   # From project root
   docker-compose up -d
   ```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (copy and modify `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. Run the service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

## API Endpoints

### Webhook Endpoints (for email providers)
- `POST /api/webhooks/sendgrid` - SendGrid delivery events
- `POST /api/webhooks/mailgun` - Mailgun delivery events
- `POST /api/webhooks/smtp/bounce` - SMTP bounce notifications

### Health & Monitoring
- `GET /api/health` - Health check
- `GET /api/metrics` - Prometheus metrics

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ hostname | `localhost` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `TEMPLATE_SERVICE_URL` | Template service URL | `http://template-service:8003` |
| `SMTP_HOST` | SMTP server hostname | - |
| `SENDGRID_API_KEY` | SendGrid API key | - |
| `MAILGUN_API_KEY` | Mailgun API key | - |

## Architecture

The service consumes messages from the `email.queue` and processes them asynchronously:

1. **Queue Consumer**: Reads email requests from RabbitMQ
2. **Template Rendering**: Calls template service to render email content
3. **Email Sending**: Attempts sending via available providers with circuit breaker
4. **Status Tracking**: Publishes delivery status updates to status queue
5. **Webhook Handling**: Receives delivery confirmations from email providers

## Development

### Running Tests
```bash
python -m pytest tests/ -v
```

### Code Structure
```
app/
├── consumers/          # RabbitMQ consumers
├── services/           # Business logic
├── routers/            # API endpoints
├── models/             # Data models
├── config/             # Configuration
└── utils/              # Utilities
