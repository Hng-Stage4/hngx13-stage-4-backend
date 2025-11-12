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

class EmailQueueConsumer:
    def __init__(self):
        self.email_service = EmailService()
        self.template_client = TemplateServiceClient()
        self.retry_service = RetryService()
        self.status_updater = StatusUpdater()
        self.queue_name = 'email.queue'

    async def start_consuming(self):
        """Start consuming messages from email queue"""
        def callback(ch, method, properties, body):
            asyncio.create_task(self._process_message(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel = get_rabbitmq_channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_consume(queue=self.queue_name, on_message_callback=callback)

        logger.info("Email queue consumer started", extra={"event": "consumer_started", "queue": self.queue_name})

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
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
                    "correlation_id": message.correlation_id,
                    "event": "message_received",
                    "template_id": message.template_id
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
                    provider="email_service"
                )
                self.status_updater.update_status(status)

                processing_time = time.time() - start_time
                DELIVERY_TIME.observe(processing_time)

                logger.info(
                    "Email sent successfully",
                    extra={
                        "correlation_id": message.correlation_id,
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
                    "correlation_id": message.correlation_id if 'message' in locals() else "unknown",
                    "event": "message_processing_failed",
                    "error": error_str
                }
            )

            # Retry or dead letter
            if 'message' in locals():
                self.retry_service.retry_message(message, error_str)
