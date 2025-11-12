import json
import pika
from app.config.rabbitmq import get_rabbitmq_channel
from app.models.delivery_status import DeliveryStatus
from app.utils.logger import logger

class StatusUpdater:
    def __init__(self):
        pass

    def update_status(self, status: DeliveryStatus):
        """Publish status update to status queue"""
        try:
            channel = get_rabbitmq_channel()
            channel.exchange_declare(exchange='notifications.direct', exchange_type='direct', durable=True)
            channel.basic_publish(
                exchange='notifications.direct',
                routing_key='status',
                body=json.dumps(status.dict()),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            channel.close()

            logger.info(
                f"Status update published: {status.status}",
                extra={
                    "correlation_id": status.correlation_id,
                    "event": "status_updated",
                    "status": status.status
                }
            )
        except Exception as e:
            logger.error(f"Failed to publish status update: {str(e)}")
