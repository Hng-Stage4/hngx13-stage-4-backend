import json
import time
import pika
from app.config.settings import settings
from app.config.rabbitmq import get_rabbitmq_channel
from app.models.email_message import EmailMessage
from app.utils.logger import logger
from app.utils.exponential_backoff import exponential_backoff

class RetryService:
    def __init__(self):
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay

    def retry_message(self, message: EmailMessage, error: str):
        """Retry sending message with exponential backoff"""
        if message.retry_count >= self.max_retries:
            self._move_to_dead_letter(message, error)
            return

        message.retry_count += 1
        delay = exponential_backoff(message.retry_count, self.retry_delay)

        # Publish to retry queue with delay
        channel = get_rabbitmq_channel()
        channel.queue_declare(queue='email.retry', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='email.retry',
            body=json.dumps(message.dict()),
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                headers={'x-delay': int(delay * 1000)}  # delay in ms
            )
        )
        channel.close()

        logger.info(
            f"Message scheduled for retry {message.retry_count}/{self.max_retries} in {delay}s",
            extra={
                "correlation_id": message.correlation_id,
                "event": "message_retry_scheduled",
                "retry_count": message.retry_count
            }
        )

    def _move_to_dead_letter(self, message: EmailMessage, error: str):
        """Move failed message to dead letter queue"""
        channel = get_rabbitmq_channel()
        channel.queue_declare(queue='failed.queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='failed.queue',
            body=json.dumps({
                "message": message.dict(),
                "error": error,
                "failed_at": time.time()
            }),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        channel.close()

        logger.error(
            f"Message moved to dead letter queue after {self.max_retries} retries",
            extra={
                "correlation_id": message.correlation_id,
                "event": "message_dead_lettered",
                "error": error
            }
        )
