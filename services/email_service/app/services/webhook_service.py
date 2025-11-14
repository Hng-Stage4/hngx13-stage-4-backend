import json
from typing import Dict, Any
from app.services.status_updater import StatusUpdater
from app.models.delivery_status import DeliveryStatus
from app.utils.logger import logger

class WebhookService:
    def __init__(self):
        self.status_updater = StatusUpdater()

    async def process_sendgrid_event(self, event: Dict[str, Any]):
        """Process SendGrid webhook event"""
        event_type = event.get('event')
        correlation_id = event.get('correlation_id') or event.get('custom_args', {}).get('correlation_id')

        if not correlation_id:
            logger.warning(f"SendGrid event missing correlation_id: {event}")
            return

        status_mapping = {
            'delivered': 'delivered',
            'bounce': 'bounced',
            'dropped': 'dropped',
            'spamreport': 'spam',
            'unsubscribe': 'unsubscribed',
            'group_unsubscribe': 'unsubscribed',
            'group_resubscribe': 'resubscribed'
        }

        status = status_mapping.get(event_type, 'unknown')

        delivery_status = DeliveryStatus(
            correlation_id=correlation_id,
            status=status,
            provider="sendgrid",
            details=event
        )

        self.status_updater.update_status(delivery_status)
        logger.info(f"Processed SendGrid event: {event_type} for {correlation_id}")

    async def process_mailgun_event(self, event_data: Dict[str, Any]):
        """Process Mailgun webhook event"""
        event_type = event_data.get('event')
        correlation_id = event_data.get('correlation_id') or event_data.get('custom_args', {}).get('correlation_id')

        if not correlation_id:
            logger.warning(f"Mailgun event missing correlation_id: {event_data}")
            return

        status_mapping = {
            'delivered': 'delivered',
            'failed': 'failed',
            'bounced': 'bounced',
            'unsubscribed': 'unsubscribed',
            'complained': 'spam'
        }

        status = status_mapping.get(event_type, 'unknown')

        delivery_status = DeliveryStatus(
            correlation_id=correlation_id,
            status=status,
            provider="mailgun",
            details=event_data
        )

        self.status_updater.update_status(delivery_status)
        logger.info(f"Processed Mailgun event: {event_type} for {correlation_id}")

    async def process_smtp_bounce(self, bounce_data: Dict[str, Any]):
        """Process SMTP bounce notification"""
        correlation_id = bounce_data.get('correlation_id')

        if not correlation_id:
            logger.warning(f"SMTP bounce missing correlation_id: {bounce_data}")
            return

        delivery_status = DeliveryStatus(
            correlation_id=correlation_id,
            status="bounced",
            provider="smtp",
            details=bounce_data
        )

        self.status_updater.update_status(delivery_status)
        logger.info(f"Processed SMTP bounce for {correlation_id}")

    async def process_zoho_event(self, event_data: Dict[str, Any]):
        """Process Zoho Mail webhook event"""
        event_type = event_data.get('event') or event_data.get('type')
        correlation_id = event_data.get('correlation_id') or event_data.get('messageId')

        if not correlation_id:
            logger.warning(f"Zoho event missing correlation_id: {event_data}")
            return

        status_mapping = {
            'delivered': 'delivered',
            'bounced': 'bounced',
            'rejected': 'rejected',
            'failed': 'failed',
            'opened': 'opened',
            'clicked': 'clicked',
            'unsubscribed': 'unsubscribed',
            'spam': 'spam'
        }

        status = status_mapping.get(event_type, 'unknown')

        delivery_status = DeliveryStatus(
            correlation_id=correlation_id,
            status=status,
            provider="zoho",
            details=event_data
        )

        self.status_updater.update_status(delivery_status)
        logger.info(f"Processed Zoho event: {event_type} for {correlation_id}")
