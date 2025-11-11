"""
API Gateway - Main Application
Handles routing, authentication, and message queuing
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.routes import auth, notifications, health, status as status_routes
from app.queue.rabbitmq import init_rabbitmq, close_rabbitmq
from app.utils.logger import setup_logging
from app.utils.exceptions import APIException
from app.config import get_settings

# Setup logging
logger = setup_logging()
settings = get_settings()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting API Gateway...")
    await init_rabbitmq()
    logger.info("✅ RabbitMQ connection established")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API Gateway...")
    await close_rabbitmq()
    logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="Notification System API Gateway",
    description="API Gateway for distributed notification system",
    version="1.0.0",
    docs_url="/api/v1/docs" if settings.debug else None,
    redoc_url="/api/v1/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (security)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", settings.production_host]
    )

# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.error,
            "message": exc.message,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "data": None
        }
    )

# Include routers
app.include_router(health.router, prefix="", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(status_routes.router, prefix="/api/v1/status", tags=["Status"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "message": "Notification System API Gateway",
        "version": "1.0.0",
        "docs": "/api/v1/docs" if settings.debug else None
    }

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response