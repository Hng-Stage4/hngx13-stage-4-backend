#!/bin/bash

set -e

echo "🔧 Setting up Traefik..."

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

# Create directories
echo -e "${YELLOW}Creating Traefik directories...${NC}"
mkdir -p traefik/{certs,logs}

# Set permissions
chmod 600 traefik/certs
chmod 755 traefik/logs

# Create acme.json for Let's Encrypt
touch traefik/certs/acme.json
chmod 600 traefik/certs/acme.json

echo -e "${GREEN}✅ Traefik directories created${NC}"

# Check if Traefik config files exist
if [ ! -f "traefik/traefik.yml" ]; then
    echo -e "${RED}❌ traefik.yml not found!${NC}"
    exit 1
fi

if [ ! -f "traefik/dynamic_conf.yml" ]; then
    echo -e "${RED}❌ dynamic_conf.yml not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Traefik configuration files found${NC}"

# Validate Traefik configuration
echo -e "${YELLOW}Validating Traefik configuration...${NC}"
docker run --rm -v "$(pwd)/traefik:/etc/traefik:ro" traefik:v2.10 version

# Start Traefik
echo -e "${YELLOW}Starting Traefik...${NC}"
docker-compose up -d traefik

# Wait for Traefik to start
echo -e "${YELLOW}Waiting for Traefik to start...${NC}"
sleep 5

# Check if Traefik is running
if docker ps | grep -q traefik; then
    echo -e "${GREEN}✅ Traefik is running${NC}"
    echo -e "${GREEN}📊 Dashboard: http://localhost:8080${NC}"
else
    echo -e "${RED}❌ Traefik failed to start${NC}"
    docker logs traefik
    exit 1
fi

echo -e "${GREEN}✅ Traefik setup complete!${NC}"