# Template Service

A microservice for managing notification templates with versioning, caching, and variable substitution.

## Features

- **Template Management**: CRUD operations for email/notification templates
- **Version Control**: Automatic versioning on template updates
- **Variable Substitution**: Dynamic content rendering with {{variable}} syntax
- **Caching**: Redis-based caching for improved performance
- **Multi-language Support**: Template localization capabilities
- **Health Monitoring**: Comprehensive health checks
- **Metrics**: Prometheus-compatible metrics
- **Structured Logging**: JSON logging with correlation IDs

## Architecture

```
Template Service
├── PostgreSQL (Templates & Versions)
├── Redis (Caching)
└── REST API
```

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd template-service
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

4. Run database migrations:

```bash
alembic upgrade head
```

5. Run the service:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | PostgreSQL hostname | localhost |
| `DATABASE_PORT` | PostgreSQL port | 5432 |
| `DATABASE_USER` | PostgreSQL username | postgres |
| `DATABASE_PASSWORD` | PostgreSQL password | password |
| `DATABASE_NAME` | PostgreSQL database name | template_db |
| `REDIS_HOST` | Redis hostname | localhost |
| `REDIS_PORT` | Redis port | 6379 |

## API Endpoints

### Templates

#### Create Template

```
POST /api/templates
```

**Request Body:**

```json
{
  "name": "Welcome Email",
  "subject": "Welcome {{user_name}}!",
  "body": "<h1>Hello {{user_name}}!</h1><p>Welcome to {{company}}</p>",
  "language": "en"
}
```

#### Get Template

```
GET /api/templates/{template_id}
```

#### Update Template

```
PUT /api/templates/{template_id}
```

#### Render Template

```
POST /api/templates/{template_id}/render
```

**Request Body:**

```json
{
  "variables": {
    "user_name": "John Doe",
    "company": "Example Corp"
  },
  "language": "en"
}
```

### Versions

#### Get Template Versions

```
GET /api/templates/{template_id}/versions
```

#### Get Version

```
GET /api/versions/{version_id}
```

### Health Check

```
GET /api/health
```

Returns service health status including database and Redis connectivity.

### Metrics

```
GET /api/metrics
```

Returns Prometheus-formatted metrics.

## Template Format

Templates use {{variable}} syntax for dynamic content:

```html
<h1>Welcome {{user_name}}!</h1>
<p>Thank you for joining {{company}}.</p>
<p>Your account ID is: {{account_id}}</p>
```

## Version Control

- Templates are automatically versioned on updates
- Each version tracks changes and creation timestamp
- Previous versions remain accessible
- Version history helps with rollback and auditing

## Caching

- Templates are cached in Redis for improved performance
- Cache TTL: 3600 seconds (configurable)
- Cache invalidation on template updates
- Cache keys: `template:{template_id}`

## Monitoring

### Metrics Tracked

- `template_service_requests_total`: HTTP request count
- `template_service_request_duration_seconds`: Request latency
- `template_service_errors_total`: Error count
- `template_service_templates_loaded_total`: Templates retrieved
- `template_service_render_duration_seconds`: Template rendering time
- `template_service_version_count_total`: Total template versions

### Health Checks

- **Database**: PostgreSQL connectivity
- **Redis**: Cache connectivity

## Logging

All logs are structured JSON:

```json
{
  "timestamp": "2025-11-12T08:00:00.000Z",
  "level": "INFO",
  "service_name": "template-service",
  "correlation_id": "unique-id",
  "event": "template_created",
  "message": "Template created successfully"
}
```

## Database Schema

### Templates Table

- `id`: Primary key (string)
- `name`: Template name
- `subject`: Email subject (optional)
- `body`: Template content
- `language`: Language code
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Versions Table

- `id`: Primary key (auto-increment)
- `template_id`: Foreign key to templates
- `version_number`: Version number
- `subject`: Version subject
- `body`: Version content
- `changes`: Change description
- `created_at`: Version creation timestamp

### Languages Table

- `code`: Language code (primary key)
- `name`: Language name
- `direction`: Text direction (ltr/rtl)

## Development

### Running Tests

```bash
pytest tests/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "migration message"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
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
docker build -t template-service .
docker run -p 8003:8003 template-service
```

## Production Deployment

- Use connection pooling for database connections
- Set up Redis cluster for high availability
- Configure proper monitoring with Prometheus/Grafana
- Implement database backups and replication
- Use environment-specific configurations
- Set up log aggregation and monitoring

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Verify PostgreSQL is running
   - Check connection string and credentials
   - Ensure database exists

2. **Cache misses**
   - Check Redis connectivity
   - Verify cache TTL settings
   - Monitor cache hit rates

3. **Template rendering errors**
   - Validate variable names in templates
   - Check variable data types
   - Review template syntax

### Logs Location

- Application logs: `logs/template-service.log`
- Database logs: PostgreSQL logs
- Cache logs: Redis logs

## API Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "message": "Operation successful",
  "meta": { ... }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License.
