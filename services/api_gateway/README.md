# ============================================
# README.md
# ============================================
# Notification System - API Gateway

Distributed notification system built with microservices architecture.

## Architecture

- **API Gateway**: Entry point for all requests
- **User Service**: Manages users and preferences
- **Email Service**: Processes email notifications
- **Push Service**: Processes push notifications
- **Template Service**: Manages notification templates

## Tech Stack

- **Framework**: FastAPI
- **Message Queue**: RabbitMQ
- **Cache**: Redis
- **Database**: PostgreSQL
- **Containerization**: Docker

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Running Locally

```bash
# Clone repository
git clone <repo-url>
cd notification-system

# Start all services
make up

# View logs
make logs

# Run tests
make test
```

### API Documentation

Once running, visit:
- API Docs: http://localhost:3000/api/docs
- RabbitMQ Management: http://localhost:15672 (guest/guest)

## Development

### Project Structure

```
api-gateway/
├── app/
│   ├── config/         # Configuration
│   ├── controllers/    # Request handlers
│   ├── middleware/     # Custom middleware
│   ├── routers/        # API routes
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic
│   └── utils/          # Utilities
├── tests/              # Test suite
└── Dockerfile
```

### Running Tests

```bash
cd api-gateway
pytest tests/ -v --cov=app
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/
```

## Deployment

### Using Docker Compose (Production)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD

GitHub Actions workflows handle:
- Linting and testing
- Docker image building
- Deployment to server
- Health checks

## API Endpoints

### Notifications

- `POST /api/v1/notifications/` - Create notification
- `GET /api/v1/notifications/{id}` - Get notification status

### Health

- `GET /api/v1/health` - Health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## Environment Variables

See `.env.example` for all configuration options.

## License

MIT