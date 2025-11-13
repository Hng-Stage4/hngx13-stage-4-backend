# DISTRIBUTED NOTIFICATION SYSTEM

## DESIGN

<img width="1531" height="1634" alt="Distributed-Notification-System-Design" src="https://github.com/user-attachments/assets/e586c420-c9ea-4698-818d-bd2b8815a7bc" /> v001



<img width="1154" height="829" alt="Distributed Notification Service drawio" src="https://github.com/user-attachments/assets/f78355b9-48d2-4a7e-a0ec-3ed4a9b0fa7b" /> v002



# 📬 Distributed Notification System

A scalable, fault-tolerant microservices-based notification system built with Python FastAPI, RabbitMQ, and Redis. Supports email and push notifications with advanced features like circuit breakers, idempotency, and rate limiting.

[![CI/CD](https://github.com/Hng-Stage4/hngx13-stage-4-backend/actions/workflows/microservices-ci-cd.yml/badge.svg)](https://github.com/Hng-Stage4/hngx13-stage-4-backend/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Services](#services)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [Team](#team)
- [License](#license)

---

## 🎯 Overview

This project implements a distributed notification system as part of **HNG Stage 4 Backend Challenge**. The system handles email and push notifications through separate microservices that communicate asynchronously via RabbitMQ message queues.

### Key Highlights

- ✅ **Microservices Architecture** - Independent, scalable services
- ✅ **Message Queue Integration** - Async communication via RabbitMQ
- ✅ **Fault Tolerance** - Circuit breakers and retry mechanisms
- ✅ **High Performance** - Handles 1,000+ notifications per minute
- ✅ **Production Ready** - Docker containerization and CI/CD pipeline

---

## ✨ Features

### Core Features

- 📧 **Email Notifications** - SMTP, SendGrid, Mailgun support
- 📱 **Push Notifications** - Firebase FCM, OneSignal, Web Push
- 🔐 **Authentication** - JWT-based secure access
- 🎨 **Template Management** - Dynamic templates with variable substitution
- 👥 **User Preferences** - Customizable notification settings
- 📊 **Status Tracking** - Real-time delivery status monitoring

### Advanced Features

- 🔄 **Circuit Breaker** - Prevents cascading failures
- 🔁 **Retry Logic** - Exponential backoff with dead-letter queue
- 🚫 **Idempotency** - Prevents duplicate notifications
- ⚡ **Rate Limiting** - Request throttling per client
- 🔍 **Distributed Tracing** - Correlation IDs across services
- 💾 **Caching** - Redis-based performance optimization
- 🏥 **Health Checks** - Kubernetes-ready probes
- 📈 **Horizontal Scaling** - All services support scaling

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│              (Web, Mobile, External APIs)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Requests
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (Port 3000)                       │
│  • Authentication (JWT)                                          │
│  • Request Validation                                            │
│  • Rate Limiting                                                 │
│  • Queue Routing                                                 │
│  • Status Tracking                                               │
└──────────┬──────────────────────────────┬───────────────────────┘
           │                              │
           │ REST API                     │ Publishes Messages
           ↓                              ↓
┌──────────────────┐            ┌────────────────────┐
│  USER SERVICE    │            │     RABBITMQ       │
│  (Port 8001)     │            │  Message Queues    │
│                  │            │  • email.queue     │
│  • User CRUD     │            │  • push.queue      │
│  • Preferences   │            │  • failed.queue    │
│  • Auth          │            └────────┬───────────┘
└──────────────────┘                     │
                                         │ Consumers
                              ┌──────────┴──────────┐
                              ↓                     ↓
                    ┌──────────────────┐  ┌──────────────────┐
                    │  EMAIL SERVICE   │  │  PUSH SERVICE    │
                    │                  │  │                  │
                    │  • Template      │  │  • FCM           │
                    │  • SMTP          │  │  • OneSignal     │
                    │  • SendGrid      │  │  • Web Push      │
                    │  • Retry Logic   │  │  • Token Valid   │
                    └──────────────────┘  └──────────────────┘
                              │                     │
                              ↓                     ↓
                    ┌──────────────────────────────────────┐
                    │      TEMPLATE SERVICE (Port 8003)    │
                    │  • Template Storage                  │
                    │  • Variable Substitution             │
                    │  • Multi-language Support            │
                    │  • Version History                   │
                    └──────────────────────────────────────┘
```

### Data Flow

1. **Client Request** → API Gateway
2. **Authentication** → JWT validation
3. **User Lookup** → User Service (cached in Redis)
4. **Queue Message** → RabbitMQ (email.queue or push.queue)
5. **Worker Consumes** → Email/Push Service
6. **Template Fetch** → Template Service
7. **Send Notification** → SMTP/FCM/OneSignal
8. **Update Status** → Redis tracking
9. **Response** → Client receives notification ID

---

## 🔧 Services

### 1. API Gateway Service

**Port:** 3000 | **Type:** Synchronous REST API

**Responsibilities:**
- Entry point for all notification requests
- JWT authentication and request validation
- Routes messages to appropriate queues
- Tracks notification status in Redis
- Implements rate limiting and circuit breakers

**Endpoints:**
```
POST   /api/v1/notifications/     - Create notification
GET    /api/v1/notifications/{id} - Get status
GET    /api/v1/health             - Health check
GET    /api/docs                  - API documentation
```

---

### 2. User Service

**Port:** 8001 | **Type:** Synchronous REST API | **Database:** PostgreSQL

**Responsibilities:**
- User CRUD operations
- Authentication and authorization
- Notification preference management
- Push token storage

**Endpoints:**
```
POST   /api/v1/users/             - Create user
GET    /api/v1/users/{id}         - Get user
PUT    /api/v1/users/{id}         - Update user
POST   /api/v1/auth/login         - Login
GET    /api/v1/preferences/{id}   - Get preferences
```

---

### 3. Email Service

**Type:** Asynchronous Queue Consumer

**Responsibilities:**
- Consumes messages from `email.queue`
- Fetches templates from Template Service
- Sends emails via SMTP/SendGrid/Mailgun
- Handles delivery confirmations and bounces
- Implements retry logic with exponential backoff

**Supported Providers:**
- ✅ SMTP (Gmail, Office365, etc.)
- ✅ SendGrid
- ✅ Mailgun
- ✅ AWS SES (configurable)

---

### 4. Push Notification Service

**Type:** Asynchronous Queue Consumer

**Responsibilities:**
- Consumes messages from `push.queue`
- Sends mobile/web push notifications
- Validates device tokens
- Supports rich notifications (title, text, image, link)

**Supported Providers:**
- ✅ Firebase Cloud Messaging (FCM)
- ✅ OneSignal
- ✅ Web Push (VAPID)

---

### 5. Template Service

**Port:** 8003 | **Type:** Synchronous REST API | **Database:** PostgreSQL

**Responsibilities:**
- Stores notification templates
- Variable substitution (e.g., `{{name}}`, `{{link}}`)
- Multi-language support
- Template version history

**Endpoints:**
```
POST   /api/v1/templates/         - Create template
GET    /api/v1/templates/{code}   - Get template
PUT    /api/v1/templates/{id}     - Update template
GET    /api/v1/templates/versions - Get versions
```

---

## 🛠️ Tech Stack

### Languages & Frameworks
- **Python 3.10+** - Primary language
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation using Python type hints

### Message Queue & Cache
- **RabbitMQ 3.12** - Message broker for async communication
- **Redis 7** - In-memory cache and rate limiting

### Databases
- **PostgreSQL 15** - Primary database for User and Template services
- **Redis** - Caching, rate limiting, idempotency

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Nginx** - Reverse proxy (optional)

### Monitoring & Logging
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **ELK Stack** - Log aggregation (optional)

### Email Providers
- SMTP (Gmail, Office365)
- SendGrid
- Mailgun

### Push Providers
- Firebase Cloud Messaging (FCM)
- OneSignal
- Web Push (VAPID)

---

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.10+** (for local development)
- **Git**

### Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/Hng-Stage4/hngx13-stage-4-backend.git
cd hngx13-stage-4-backend

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env with your credentials
nano .env

# 4. Start all services
docker-compose up -d

# 5. Check service status
docker-compose ps

# 6. View logs
docker-compose logs -f api-gateway

# 7. Test API
curl http://localhost:3000/api/v1/health
```

### Access Services

- **API Gateway:** http://localhost:3000
- **API Documentation:** http://localhost:3000/api/docs
- **User Service:** http://localhost:8001
- **Template Service:** http://localhost:8003
- **RabbitMQ Management:** http://localhost:15672 (guest/guest)

---

## 📚 API Documentation

### Create Notification

**Endpoint:** `POST /api/v1/notifications/`

**Request:**
```json
{
  "notification_type": "email",
  "user_id": "user-123",
  "template_code": "welcome",
  "variables": {
    "name": "John Doe",
    "link": "https://example.com"
  },
  "request_id": "req-unique-123",
  "priority": 1,
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "notification_id": "notif-456",
    "status": "pending",
    "message": "Notification queued successfully"
  },
  "error": null,
  "message": "Notification queued successfully",
  "meta": null
}
```

### Get Notification Status

**Endpoint:** `GET /api/v1/notifications/{notification_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "notification_id": "notif-456",
    "status": "delivered",
    "message": "Notification delivered successfully"
  },
  "error": null,
  "message": "Status retrieved",
  "meta": null
}
```

**Interactive Documentation:** Visit `/api/docs` for full Swagger UI

---

## 🚢 Deployment

### Docker Compose (Production)

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale email-service=3
```

### Kubernetes Deployment

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n notification-system

# View logs
kubectl logs -f deployment/api-gateway -n notification-system
```

### CI/CD Pipeline

The project uses GitHub Actions for automated deployment:

1. **On Push:** Runs tests and linting
2. **On PR:** Runs integration tests
3. **On Main Merge:** Builds Docker images and deploys

**Setup Required Secrets:**
- `SSH_PRIVATE_KEY` - For deployment
- `SERVER_HOST` - Target server
- `SERVER_USER` - SSH username
- `DEPLOY_PATH` - Deployment directory

---

## 💻 Development

### Local Development Setup

```bash
# 1. Create virtual environment
cd services/api_gateway
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run service
uvicorn app.main:app --reload --port 8000

# 4. Run with all dependencies (Docker)
docker-compose -f docker-compose.dev.yml up
```

### Code Quality

```bash
# Format code
black services/api_gateway/app/

# Sort imports
isort services/api_gateway/app/

# Lint
flake8 services/api_gateway/app/
```

### Project Structure

```
hngx13-stage-4-backend/
├── services/
│   ├── api_gateway/        # API Gateway service
│   ├── user_service/       # User management
│   ├── email_service/      # Email notifications
│   ├── push_service/       # Push notifications
│   └── template_service/   # Template management
├── docker-compose.yml      # Development setup
├── docker-compose.prod.yml # Production setup
├── .github/workflows/      # CI/CD pipelines
└── docs/                   # Additional documentation
```

---

## 🧪 Testing

### Run All Tests

```bash
# Unit tests
pytest services/api_gateway/tests/unit/ -v

# Integration tests
pytest services/api_gateway/tests/integration/ -v

# End-to-end tests
pytest services/api_gateway/tests/e2e/ -v

# Coverage report
pytest --cov=app --cov-report=html
```

### Manual Testing

```bash
# Health check
curl http://localhost:3000/api/v1/health

# Create notification (requires auth)
curl -X POST http://localhost:3000/api/v1/notifications/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "email",
    "user_id": "test-user",
    "template_code": "welcome",
    "variables": {"name": "Test", "link": "https://example.com"},
    "request_id": "test-123",
    "priority": 1
  }'
```

---

## 📊 Performance Targets

- ✅ Handle **1,000+ notifications per minute**
- ✅ API Gateway response time: **<100ms**
- ✅ Delivery success rate: **99.5%**
- ✅ All services support **horizontal scaling**
- ✅ Zero-downtime deployments

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting, missing semi colons, etc
refactor: code restructuring
test: adding tests
chore: maintenance tasks
```

---

## 👥 Team

**Team Members:**
- [@ursulaonyi](https://github.com/ursulaonyi) - API Gateway & CI/CD
- [@Peliah] (https://github.com/Peliah) - User Service
- [@idowuseyi] (https://github.com/idowuseyi) - Email Service & Template Service
- [ @EmmyAnieDev] (https://github.com/EmmyAnieDev)_ - Push & Monitoring

**Project Duration:** November 2025

**Organization:** [HNG Internship Stage 4](https://hng.tech)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **HNG Internship** - For the amazing learning opportunity
- **FastAPI Team** - For the excellent framework
- **Community Contributors** - For bug reports and suggestions

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Hng-Stage4/hngx13-stage-4-backend/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Hng-Stage4/hngx13-stage-4-backend/discussions)
- **Documentation:** [Wiki](https://github.com/Hng-Stage4/hngx13-stage-4-backend/wiki)

---

## 🔗 Links

- [API Documentation](http://localhost:3000/api/docs)
- [Architecture Diagram](docs/architecture/)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guide](CONTRIBUTING.md)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by Team HNG13 Stage 4

</div>