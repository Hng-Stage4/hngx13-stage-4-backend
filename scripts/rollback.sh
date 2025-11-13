#!/bin/bash

set -e

echo "🔄 Rolling back deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_DIR="/opt/distributed-notification-system"
BACKUP_DIR="/backup"

# Navigate to project directory
cd $PROJECT_DIR || exit 1

# Stop current containers
echo -e "${YELLOW}Stopping current containers...${NC}"
docker-compose -f $COMPOSE_FILE down

# Rollback code
echo -e "${YELLOW}Rolling back code to previous commit...${NC}"
git reset --hard HEAD~1

# Find latest database backup
LATEST_BACKUP=$(ls -t $BACKUP_DIR/db_*.sql 2>/dev/null | head -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo -e "${YELLOW}Restoring database from: $LATEST_BACKUP${NC}"
    
    # Start PostgreSQL only
    docker-compose -f $COMPOSE_FILE up -d postgres
    sleep 10
    
    # Restore database
    docker exec -i postgres psql -U postgres notification_db < "$LATEST_BACKUP"
    echo -e "${GREEN}✅ Database restored${NC}"
else
    echo -e "${YELLOW}⚠️  No database backup found, skipping restore${NC}"
fi

# Start all services with previous version
echo -e "${YELLOW}Starting services with previous version...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for services
sleep 15

# Health check
echo -e "${YELLOW}Running health check...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Rollback successful!${NC}"
    echo -e "${GREEN}Services are healthy${NC}"
else
    echo -e "${RED}❌ Rollback failed - services unhealthy${NC}"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

echo -e "${GREEN}✅ Rollback completed successfully!${NC}"