import json
import asyncio
import time
from app.config.rabbitmq import get_rabbitmq_channel
from app.models.email_message import EmailMessage
from app.models.delivery_status import DeliveryStatus
from app.services.email_service import EmailService
from app.services.template_service import TemplateServiceClient
from app.services.retry_service import RetryService
from app.services.status_updater import StatusUpdater
from app.utils.logger import logger
from app.routers.metrics import QUEUE_MESSAGES_PROCESSED, DELIVERY_TIME

class RetryQueueConsumer:
    def __init__(self):
        self.email_service = EmailService()
        self.template_client = TemplateServiceClient()
        self.retry_service = RetryService()
        self.status_updater = StatusUpdater()
        self.queue_name = 'email.retry'

    async def start_consuming(self):
        """Start consuming messages from retry queue"""
        def callback(ch, method, properties, body):
            asyncio.create_task(self._process_message(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel = get_rabbitmq_channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_consume(queue=self.queue_name, on_message_callback=callback)

        logger.info("Retry queue consumer started", extra={"event": "consumer_started", "queue": self.queue_name})

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            logger.info("Retry queue consumer stopped", extra={"event": "consumer_stopped"})

    async def _process_message(self, body: bytes):
        """Process retry message"""
        try:
            data = json.loads(body)
            message = EmailMessage(**data)
            start_time = time.time()

            logger.info(
                f"Retrying email message (attempt {message.retry_count})",
                extra={
                    "correlation_id": message.correlation_id,
                    "event": "message_retry_processing",
                    "retry_count": message.retry_count
                }
            )

            # Get rendered template
            template_data = await self.template_client.get_rendered_template(
                message.template_id,
                message.variables
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
                    correlation_id=message.correlation_id,
                    status="sent",
                    provider="email_service",
                    retry_count=message.retry_count
                )
                self.status_updater.update_status(status)

                processing_time = time.time() - start_time
                DELIVERY_TIME.observe(processing_time)

                logger.info(
                    f"Email sent successfully on retry {message.retry_count}",
                    extra={
                        "correlation_id": message.correlation_id,
                        "event": "email_retry_success",
                        "retry_count": message.retry_count,
                        "processing_time": processing_time
                    }
                )
            else:
                raise Exception("Failed to send email on retry")

            QUEUE_MESSAGES_PROCESSED.inc()

        except Exception as e:
            error_str = str(e)
            logger.error(
                f"Failed to process retry message: {error_str}",
                extra={
                    "correlation_id": message.correlation_id if 'message' in locals() else "unknown",
                    "event": "retry_processing_failed",
                    "error": error_str
                }
            )

            # Retry again or dead letter
            if 'message' in locals():
                self.retry_service.retry_message(message, error_str)
