#!/bin/bash

set -e

echo "🧪 Testing CI/CD pipeline locally..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# 1. Run linting
echo -e "${YELLOW}Running linting checks...${NC}"
pip install flake8 black isort > /dev/null 2>&1

black --check services/api_gateway/app
print_status $? "Black formatting check"

isort --check-only services/api_gateway/app
print_status $? "Import sorting check"

flake8 services/api_gateway/app --max-line-length=100 --exclude=__pycache__
print_status $? "Flake8 linting"

# 2. Run tests
echo -e "${YELLOW}Running tests...${NC}"
pip install -r services/api_gateway/requirements.txt > /dev/null 2>&1
pip install pytest pytest-cov pytest-asyncio > /dev/null 2>&1

pytest services/api_gateway/tests/ -v --cov=services/api_gateway/app
print_status $? "Unit tests"

# 3. Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t api_gateway:test services/api_gateway
print_status $? "Docker build"

# 4. Test Docker image
echo -e "${YELLOW}Testing Docker image...${NC}"
docker run -d --name api_gateway_test -p 8001:8000 api_gateway:test
sleep 5

curl -f http://localhost:8001/health > /dev/null 2>&1
HEALTH_CHECK=$?

docker stop api_gateway_test > /dev/null 2>&1
docker rm api_gateway_test > /dev/null 2>&1

print_status $HEALTH_CHECK "Docker health check"

# 5. Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
docker rmi api_gateway:test > /dev/null 2>&1

echo -e "${GREEN}✅ All CI/CD tests passed!${NC}"
echo -e "${GREEN}🚀 Ready to push to production${NC}"