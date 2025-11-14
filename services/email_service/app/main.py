from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
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
    
    # Store consumer instances
    consumer_instances = []
    
    try:
        email_consumer = EmailQueueConsumer()
        retry_consumer = RetryQueueConsumer()
        
        consumer_instances = [email_consumer, retry_consumer]
        
        # Start consumers (they run in daemon threads, so just await the startup)
        await email_consumer.start_consuming()
        await retry_consumer.start_consuming()
        
        logger.info("Consumers started successfully", extra={"event": "consumers_started"})
    except Exception as e:
        logger.warning(f"Failed to start consumers: {e}. Service will run without queue processing.", extra={"event": "consumer_startup_failed"})
    
    yield  # <-- This should now be reached!
    
    # Shutdown
    logger.info("Shutting down Email Service", extra={"service_name": "email-service", "event": "service_shutdown"})
    
    # Stop consumers
    for consumer in consumer_instances:
        consumer.stop()

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