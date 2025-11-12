#!/bin/bash

set -e  # Exit on error

echo "🚀 Starting deployment to production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_DIR="/opt/distributed-notification-system"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root or with sudo"
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR || exit 1

# Pull latest code
log_info "Pulling latest code from Git..."
git pull origin main

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    log_error ".env file not found!"
    exit 1
fi

# Pull latest Docker images
log_info "Pulling latest Docker images..."
docker-compose -f $COMPOSE_FILE pull

# Stop old containers (graceful shutdown)
log_info "Stopping old containers..."
docker-compose -f $COMPOSE_FILE stop

# Start new containers
log_info "Starting new containers..."
docker-compose -f $COMPOSE_FILE up -d --remove-orphans

# Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 15

# Health check
log_info "Running health checks..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    log_info "✅ API Gateway is healthy"
else
    log_error "❌ API Gateway health check failed!"
    exit 1
fi

# Clean up old images and containers
log_info "Cleaning up old Docker resources..."
docker system prune -af --volumes

log_info "✅ Deployment completed successfully!"
log_info "📊 Check Traefik dashboard: http://localhost:8080"
log_info "🐰 Check RabbitMQ dashboard: http://localhost:15672"

exit 0