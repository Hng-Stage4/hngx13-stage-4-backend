# ============================================
# api-gateway/app/config/rabbitmq.py
# ============================================
import json
import aio_pika
from typing import Optional
from app.config.settings import settings

from app.utils.logger import logger



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
                "notifications.direct", aio_pika.ExchangeType.DIRECT, durable=True
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

    async def publish_message(self, queue_name: str, message: dict):  # dict, not string
        if not self.channel:
            raise Exception("RabbitMQ channel not initialized")

        try:
            exchange = await self.channel.declare_exchange(
                "notifications.direct", aio_pika.ExchangeType.DIRECT, durable=True
            )

            queue = await self.channel.declare_queue(queue_name, durable=True)
            
            # Derive routing key from queue name
            routing_key = queue_name.split('.')[0]
            
            await queue.bind(exchange, routing_key=routing_key)

            # json.dumps() happens HERE, only once
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),  # This is the ONLY json.dumps
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type='application/json',
                ),
                routing_key=routing_key,
            )
            logger.info(f"Published to queue='{queue_name}', routing_key='{routing_key}'")
        except Exception as e:
            logger.error(f"Failed to publish message to {queue_name}: {e}")
            raise

rabbitmq_manager = RabbitMQManager()
