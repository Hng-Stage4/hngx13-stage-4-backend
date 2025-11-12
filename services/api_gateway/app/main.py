# ============================================
# api-gateway/app/main.py
# ============================================
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.config.settings import settings
from app.routers import notification, health, status
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Notification API Gateway",
    description="Distributed Notification System - API Gateway",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(notification.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(status.router, prefix="/api/v1", tags=["Status"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting API Gateway...")
    # Initialize RabbitMQ connection
    from app.config.rabbitmq import rabbitmq_manager
    await rabbitmq_manager.connect()
    
    # Initialize Redis connection
    from app.config.redis import redis_manager
    await redis_manager.connect()
    
    logger.info("API Gateway started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API Gateway...")
    from app.config.rabbitmq import rabbitmq_manager
    await rabbitmq_manager.disconnect()
    
    from app.config.redis import redis_manager
    await redis_manager.disconnect()
    
    logger.info("API Gateway shutdown complete")


@app.get("/")
async def root():
    return {
        "service": "Notification API Gateway",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )