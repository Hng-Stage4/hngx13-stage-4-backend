"""
RabbitMQ Message Producer
"""
import json
import aio_pika
from typing import Dict, Any
import logging

from app.queue.rabbitmq import get_channel
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def publish_notification(notification_type: str, message: Dict[str, Any]) -> bool:
    """
    Publish notification message to RabbitMQ
    
    Args:
        notification_type: Type of notification (email, push, sms)
        message: Message payload
    
    Returns:
        True if successful
    """
    try:
        channel = await get_channel()
        
        # Determine routing key
        routing_key = f"{notification_type}.queue"
        
        # Create message
        message_body = json.dumps(message).encode()
        
        # Publish message
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={
                    "notification_type": notification_type,
                    "priority": message.get("priority", 1)
                }
            ),
            routing_key=routing_key
        )
        
        logger.info(f"📤 Published message to '{routing_key}': {message.get('notification_id')}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to publish message: {str(e)}")
        raise

async def publish_to_dlq(message: Dict[str, Any], error: str) -> bool:
    """
    Publish failed message to Dead Letter Queue
    """
    try:
        channel = await get_channel()
        
        message["error"] = error
        message_body = json.dumps(message).encode()
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json"
            ),
            routing_key="failed.queue"
        )
        
        logger.info(f"📤 Published to DLQ: {message.get('notification_id')}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to publish to DLQ: {str(e)}")
        return False