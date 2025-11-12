from fastapi import FastAPI
from app.config.database import init_db
from app.routers.health import router as health_router
from app.routers.metrics import router as metrics_router
from app.routers.template import router as template_router
from app.routers.version import router as version_router
from app.utils.logger import logger
from app.seeds.default_templates import seed_default_data

app = FastAPI(
    title="Template Service",
    description="Microservice for managing notification templates",
    version="1.0.0"
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(metrics_router, prefix="/api", tags=["metrics"])
app.include_router(template_router, prefix="/api", tags=["templates"])
app.include_router(version_router, prefix="/api", tags=["versions"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Template Service", extra={"service_name": "template-service", "event": "service_startup"})
    # Run database migrations
    import subprocess
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True, cwd="/app")
        logger.info("Database migrations completed")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run migrations: {e}")
        raise

    init_db()
    seed_default_data()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Template Service", extra={"service_name": "template-service", "event": "service_shutdown"})

@app.get("/")
async def root():
    return {"message": "Template Service is running"}
