# ============================================
# Makefile
# ============================================
.PHONY: help build up down logs test lint format clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linters"
	@echo "  make format   - Format code"
	@echo "  make clean    - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services are up! API Gateway: http://localhost:3000/api/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f api-gateway

test:
	cd api-gateway && pytest tests/ -v

lint:
	cd api-gateway && flake8 app/

format:
	cd api-gateway && black app/

clean:
	docker-compose down -v
	docker system prune -f