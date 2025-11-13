# ============================================
# api-gateway/app/main.py
# ============================================
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.routers import notification, health, status
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Starting API Gateway...")

    # Try to connect to RabbitMQ
    try:
        from app.config.rabbitmq import rabbitmq_manager

        await rabbitmq_manager.connect()
        logger.info("RabbitMQ connected successfully")
    except Exception as e:
        logger.warning(f"RabbitMQ connection failed: {e}. Running in standalone mode.")

    # Try to connect to Redis
    try:
        from app.config.redis import redis_manager

        await redis_manager.connect()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running in standalone mode.")

    logger.info("API Gateway started successfully")

    yield

    # Shutdown
    logger.info("Shutting down API Gateway...")

    try:
        from app.config.rabbitmq import rabbitmq_manager

        await rabbitmq_manager.disconnect()
    except Exception:  # ✅ Fixed: Changed from bare except to Exception
        pass

    try:
        from app.config.redis import redis_manager

        await redis_manager.disconnect()
    except Exception:  # ✅ Fixed: Changed from bare except to Exception
        pass

    logger.info("API Gateway shutdown complete")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Notification API Gateway",
    description="Distributed Notification System - API Gateway",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,  # Use new lifespan handler
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Use the CORS_ORIGINS setting defined in app.config.settings (uppercase)
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
# Temporarily disable rate limiter for testing
# app.add_middleware(RateLimiterMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(notification.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(status.router, prefix="/api/v1", tags=["Status"])


@app.get("/")
async def root():
    return {
        "service": "Notification API Gateway",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.GATEWAY_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )