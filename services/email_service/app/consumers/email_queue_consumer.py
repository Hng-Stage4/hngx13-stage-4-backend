from datetime import datetime
import json
import asyncio
import time
import threading
from app.config.rabbitmq import get_rabbitmq_channel
from app.models.email_message import EmailMessage
from app.models.delivery_status import DeliveryStatus, DeliveryStatusEnum
from app.services.email_service import EmailService
from app.services.template_service import TemplateServiceClient
from app.services.retry_service import RetryService
from app.services.status_updater import StatusUpdater
from app.utils.logger import logger
from app.routers.metrics import QUEUE_MESSAGES_PROCESSED, DELIVERY_TIME

class EmailQueueConsumer:
    def __init__(self):
        self.email_service = EmailService()
        self.template_client = TemplateServiceClient()
        self.retry_service = RetryService()
        self.status_updater = StatusUpdater()
        self.queue_name = 'email.queue'
        self.channel = None
        self._thread = None
        self._stop_flag = False

    async def start_consuming(self):
        """Start consuming messages from email queue in a separate thread"""
        self._thread = threading.Thread(target=self._blocking_consume, daemon=True)
        self._thread.start()
        
        # Give it a moment to start up
        await asyncio.sleep(0.1)
        logger.info("Email queue consumer thread started", extra={"event": "consumer_thread_started"})

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
                    logger.error(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            self.channel.basic_consume(
                queue=self.queue_name, 
                on_message_callback=callback,
                auto_ack=False
            )

            logger.info(
                "Email queue consumer started", 
                extra={"event": "consumer_started", "queue": self.queue_name}
            )

            # This blocks, but it's okay because it's in a separate thread
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(
                f"Error in email queue consumer: {str(e)}", 
                extra={"event": "consumer_error", "error": str(e)}
            )

    def stop(self):
        """Stop consuming messages"""
        self._stop_flag = True
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
            self.channel.close()
            logger.info("Email queue consumer stopped", extra={"event": "consumer_stopped"})

    async def _process_message(self, body: bytes):
        """Process individual email message"""
        try:
            data = json.loads(body)
            message = EmailMessage(**data)
            start_time = time.time()

            logger.info(
                "Processing email message",
                extra={
                    "notification_id": message.notification_id,
                    "event": "message_received",
                    "template_id": message.template_id
                }
            )

            # Get rendered template
            template_data = await self.template_client.get_rendered_template(
                message.template_id,
                message.variables,
                message.language
            )

            if not template_data:
                raise Exception("Failed to get template")

            rendered_body = template_data.get("body", "")
            subject = template_data.get("subject", "Notification")

            # Send email
            success = await self.email_service.send_email(message, rendered_body, subject)

            if success:
                # Update status
                status = DeliveryStatus(
                    notification_id=message.notification_id,
                    status=DeliveryStatusEnum.sent,
                    provider="email_service",
                    timestamp=datetime.utcnow()
                )
                await self.status_updater.update_status(status)

                processing_time = time.time() - start_time
                DELIVERY_TIME.observe(processing_time)

                logger.info(
                    "Email sent successfully",
                    extra={
                        "notification_id": message.notification_id,
                        "event": "email_sent",
                        "processing_time": processing_time
                    }
                )
            else:
                raise Exception("Failed to send email")

            QUEUE_MESSAGES_PROCESSED.inc()

        except Exception as e:
            error_str = str(e)
            logger.error(
                f"Failed to process email message: {error_str}",
                extra={
                    "notification_id": message.notification_id if 'message' in locals() else "unknown",
                    "event": "message_processing_failed",
                    "error": error_str
                }
            )

            # Retry or dead letter
            if 'message' in locals():
                self.retry_service.retry_message(message, error_str)