# API Gateway Documentation

## Overview

The API Gateway is the entry point for all client requests in the distributed notification system. It handles:
- Request routing
- Authentication & authorization
- Rate limiting
- Message queuing to RabbitMQ

## Architecture
```
Client → Traefik → API Gateway → RabbitMQ → Workers
                              → Redis (cache)
                              → PostgreSQL (persistence)
```

## Endpoints

### Authentication

#### POST `/api/v1/auth/register`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

#### POST `/api/v1/auth/login`
Login and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### GET `/api/v1/auth/me`
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

### Notifications

#### POST `/api/v1/notifications/`
Create a new notification (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "notification_type": "email",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "template_code": "welcome_email",
  "variables": {
    "name": "John Doe",
    "link": "https://example.com/verify"
  },
  "request_id": "req-12345",
  "priority": 5,
  "metadata": {
    "campaign_id": "camp-001"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification queued successfully",
  "data": {
    "notification_id": "notif-abc123",
    "status": "queued",
    "notification_type": "email",
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

#### POST `/api/v1/notifications/bulk`
Create multiple notifications (max 100 per request).

**Request:**
```json
[
  {
    "notification_type": "email",
    "user_id": "...",
    "template_code": "welcome_email",
    "variables": {...}
  },
  ...
]
```

#### GET `/api/v1/notifications/{notification_id}`
Get notification status.

**Response:**
```json
{
  "success": true,
  "message": "Notification status retrieved",
  "data": {
    "notification_id": "notif-abc123",
    "status": "delivered",
    "notification_type": "email",
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### Health Checks

#### GET `/health`
Basic health check.

#### GET `/health/detailed`
Detailed health check with dependencies.

#### GET `/ready`
Kubernetes readiness probe.

#### GET `/live`
Kubernetes liveness probe.

## Authentication

All endpoints except `/health`, `/api/v1/auth/login`, and `/api/v1/auth/register` require a valid JWT token.

Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

Tokens expire after 30 minutes by default.

## Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error message",
  "data": null
}
```

### Common Error Codes

- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

- 100 requests per minute per user
- Burst limit: 50 requests

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699999999
```

## Testing

### Using cURL
```bash
# Register
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!"
  }'

# Login
TOKEN=$(curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' | jq -r '.data.access_token')

# Create notification
curl -X POST http://localhost/api/v1/notifications/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "email",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "template_code": "welcome_email",
    "variables": {
      "name": "Test User",
      "link": "https://example.com"
    }
  }'
```

## Development

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=app
```

### Environment Variables

See `.env.example` for all configuration options.

## Monitoring

- Health check: `GET /health`
- Metrics endpoint (for Prometheus): `GET /metrics`
- Logs: JSON format to stdout