from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from app.config.settings import settings
from app.routers.health import router as health_router
from app.routers.metrics import router as metrics_router
from app.routers.webhooks import router as webhooks_router
from app.consumers.email_queue_consumer import EmailQueueConsumer
from app.consumers.retry_queue_consumer import RetryQueueConsumer
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Email Service", extra={"service_name": "email-service", "event": "service_startup"})
    # Start consumers
    email_consumer = EmailQueueConsumer()
    retry_consumer = RetryQueueConsumer()
    consumer_tasks = [
        asyncio.create_task(email_consumer.start_consuming()),
        asyncio.create_task(retry_consumer.start_consuming())
    ]
    yield
    # Shutdown
    logger.info("Shutting down Email Service", extra={"service_name": "email-service", "event": "service_shutdown"})
    for task in consumer_tasks:
        task.cancel()
    try:
        await asyncio.gather(*consumer_tasks, return_exceptions=True)
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Email Service",
    description="Microservice for sending emails asynchronously",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(metrics_router, prefix="/api", tags=["metrics"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "Email Service is running"}
