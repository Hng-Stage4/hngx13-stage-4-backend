import json
import asyncio
import time
import threading
from app.config.rabbitmq import get_rabbitmq_channel
from app.models.email_message import EmailMessage
from app.services.retry_service import RetryService
from app.utils.logger import logger

class RetryQueueConsumer:
    def __init__(self):
        self.retry_service = RetryService()
        self.queue_name = 'email.retry.queue'
        self.channel = None
        self._thread = None
        self._stop_flag = False

    async def start_consuming(self):
        """Start consuming messages from retry queue in a separate thread"""
        self._thread = threading.Thread(target=self._blocking_consume, daemon=True)
        self._thread.start()
        
        # Give it a moment to start up
        await asyncio.sleep(0.1)
        logger.info("Retry queue consumer thread started", extra={"event": "consumer_thread_started"})

    def _blocking_consume(self):
        """Blocking consume method that runs in a separate thread"""
        try:
            self.channel = get_rabbitmq_channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            def callback(ch, method, properties, body):
                try:
                    # Process message synchronously (create new event loop for this thread)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._process_message(body))
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"Error processing retry message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.channel.basic_consume(
                queue=self.queue_name, 
                on_message_callback=callback,
                auto_ack=False
            )

            logger.info(
                "Retry queue consumer started", 
                extra={"event": "consumer_started", "queue": self.queue_name}
            )

            # This blocks, but it's okay because it's in a separate thread
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(
                f"Error in retry queue consumer: {str(e)}", 
                extra={"event": "consumer_error", "error": str(e)}
            )

    def stop(self):
        """Stop consuming messages"""
        self._stop_flag = True
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
            self.channel.close()
            logger.info("Retry queue consumer stopped", extra={"event": "consumer_stopped"})

    async def _process_message(self, body: bytes):
        """Process individual retry message"""
        try:
            data = json.loads(body)
            message = EmailMessage(**data)
            
            logger.info(
                "Processing retry message",
                extra={
                    "correlation_id": message.correlation_id,
                    "event": "retry_message_received"
                }
            )
            
            # Re-publish to main queue for retry
            self.retry_service.republish_message(message)
            
        except Exception as e:
            logger.error(f"Failed to process retry message: {str(e)}")