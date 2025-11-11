"""
RabbitMQ Connection Manager
"""
import aio_pika
from aio_pika import Connection, Channel
from typing import Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global connection and channel
rabbitmq_connection: Optional[Connection] = None
rabbitmq_channel: Optional[Channel] = None

async def init_rabbitmq():
    """
    Initialize RabbitMQ connection and channel
    """
    global rabbitmq_connection, rabbitmq_channel
    
    try:
        logger.info(f"Connecting to RabbitMQ at {settings.rabbitmq_url}")
        
        # Create connection
        rabbitmq_connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            timeout=10
        )
        
        # Create channel
        rabbitmq_channel = await rabbitmq_connection.channel()
        
        # Set QoS
        await rabbitmq_channel.set_qos(prefetch_count=10)
        
        # Declare exchanges and queues
        await setup_queues()
        
        logger.info("✅ RabbitMQ connection established")
    
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}")
        raise

async def setup_queues():
    """
    Setup RabbitMQ exchanges and queues
    """
    global rabbitmq_channel
    
    if not rabbitmq_channel:
        raise RuntimeError("RabbitMQ channel not initialized")
    
    # Declare exchange
    exchange = await rabbitmq_channel.declare_exchange(
        "notifications.direct",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )
    
    # Declare queues
    queues = ["email.queue", "push.queue", "failed.queue"]
    
    for queue_name in queues:
        queue = await rabbitmq_channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-message-ttl": 86400000,  # 24 hours
                "x-max-length": 10000
            }
        )
        
        # Bind queue to exchange
        await queue.bind(exchange, routing_key=queue_name)
        logger.info(f"✅ Queue '{queue_name}' declared and bound")

async def close_rabbitmq():
    """
    Close RabbitMQ connection
    """
    global rabbitmq_connection, rabbitmq_channel
    
    try:
        if rabbitmq_channel:
            await rabbitmq_channel.close()
            logger.info("RabbitMQ channel closed")
        
        if rabbitmq_connection:
            await rabbitmq_connection.close()
            logger.info("RabbitMQ connection closed")
    
    except Exception as e:
        logger.error(f"Error closing RabbitMQ connection: {str(e)}")

async def get_channel() -> Channel:
    """
    Get RabbitMQ channel
    """
    global rabbitmq_channel
    
    if not rabbitmq_channel or rabbitmq_channel.is_closed:
        await init_rabbitmq()
    
    return rabbitmq_channel