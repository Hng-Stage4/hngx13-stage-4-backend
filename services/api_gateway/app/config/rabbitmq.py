# ============================================
# api-gateway/app/config/rabbitmq.py
# ============================================
import aio_pika
import logging
from typing import Optional
from app.config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQManager:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        
    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            connection_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VHOST}"
            self.connection = await aio_pika.connect_robust(connection_url)
            self.channel = await self.connection.channel()
            
            # Declare exchanges
            await self.channel.declare_exchange(
                "notifications.direct",
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )
            
            # Declare queues
            await self.channel.declare_queue("email.queue", durable=True)
            await self.channel.declare_queue("push.queue", durable=True)
            await self.channel.declare_queue("failed.queue", durable=True)
            
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Close RabbitMQ connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    async def publish_message(self, queue_name: str, message: dict):
        """Publish message to queue"""
        if not self.channel:
            raise Exception("RabbitMQ channel not initialized")
        
        try:
            exchange = await self.channel.get_exchange("notifications.direct")
            
            await exchange.publish(
                aio_pika.Message(
                    body=str(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue_name
            )
            logger.info(f"Published message to {queue_name}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise


rabbitmq_manager = RabbitMQManager()