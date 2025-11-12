# Template Service

A microservice for managing notification templates with multi-language support and version history.

## Features

- Template storage and management with PostgreSQL
- Multi-language template support (logical_id + language)
- Variable substitution in templates
- Version history tracking with Alembic migrations
- Caching with Redis
- RESTful API for template operations
- Health checks and metrics

## Quick Start

### Running with Docker (Recommended)

1. **Standalone Mode** (with its own dependencies):
   ```bash
   cd services/template_service
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

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Run the service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
   ```

## API Endpoints

### Template Management
- `POST /api/templates` - Create a new template
- `GET /api/templates/{id}` - Get template by ID
- `PUT /api/templates/{id}` - Update template
- `POST /api/templates/{logical_id}/render` - Render template with variables

### Version History
- `GET /api/templates/{template_id}/versions` - Get template version history
- `GET /api/versions/{version_id}` - Get specific version

### Health & Monitoring
- `GET /api/health` - Health check
- `GET /api/metrics` - Prometheus metrics

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | PostgreSQL hostname | `localhost` |
| `DATABASE_USER` | Database username | `postgres` |
| `DATABASE_PASSWORD` | Database password | `password` |
| `DATABASE_NAME` | Database name | `template_db` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `CACHE_TTL` | Cache TTL in seconds | `3600` |

## Template Structure

Templates support variable substitution using `{{variable_name}}` syntax:

```json
{
  "logical_id": "welcome_email",
  "name": "Welcome Email",
  "subject": "Welcome {{user_name}}!",
  "body": "<h1>Hello {{user_name}}</h1><p>Welcome to {{company_name}}!</p>",
  "language": "en"
}
```

### Multi-Language Support

Create multiple language variants using the same `logical_id`:

```json
// English version
{
  "logical_id": "welcome_email",
  "language": "en",
  "subject": "Welcome {{user_name}}!",
  "body": "<h1>Hello {{user_name}}</h1>"
}

// Spanish version
{
  "logical_id": "welcome_email",
  "language": "es",
  "subject": "¡Bienvenido {{user_name}}!",
  "body": "<h1>Hola {{user_name}}</h1>"
}
```

## Architecture

### Database Schema
- **templates**: Stores template data with logical_id and language
- **versions**: Tracks template changes over time
- **languages**: Supported languages (future extension)

### Key Components
1. **Template Repository**: Database operations
2. **Template Service**: Business logic and caching
3. **Version Service**: Version history management
4. **Variable Substitution**: Template rendering engine

## Development

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "migration description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### Code Structure
```
app/
├── models/             # SQLAlchemy models
├── repositories/       # Data access layer
├── services/           # Business logic
├── routers/            # API endpoints
├── schemas/            # Pydantic schemas
├── config/             # Configuration
├── migrations/         # Alembic migrations
├── seeds/              # Default data
└── utils/              # Utilities
