from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import init_db
from app.routers.health import router as health_router
from app.routers.metrics import router as metrics_router
from app.routers.template import router as template_router
from app.routers.version import router as version_router
from app.utils.logger import logger
from seeds.default_templates import seed_default_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Template Service", extra={"service_name": "template-service", "event": "service_startup"})
    try:
        init_db()
        seed_default_data()
        logger.info("Template Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Template Service: {e}")
        raise
    yield
    # Shutdown
    logger.info("Shutting down Template Service", extra={"service_name": "template-service", "event": "service_shutdown"})

app = FastAPI(
    title="Template Service",
    description="Microservice for managing notification templates",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(metrics_router, prefix="/api", tags=["metrics"])
app.include_router(template_router, prefix="/api", tags=["templates"])
app.include_router(version_router, prefix="/api", tags=["versions"])

@app.get("/")
async def root():
    return {"message": "Template Service is running"}
