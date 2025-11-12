import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Optional
from app.config.settings import settings
from app.models.email_message import EmailMessage
from app.utils.logger import logger
from app.services.circuit_breaker import CircuitBreaker
from app.routers.metrics import EMAILS_SENT, EMAILS_FAILED

class EmailService:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()

    async def send_email(self, message: EmailMessage, rendered_template: str, subject: str) -> bool:
        """Send email using available providers with circuit breaker"""
        providers = [
            self._send_via_smtp,
            self._send_via_sendgrid,
            self._send_via_mailgun,
            self._send_via_gmail
        ]

        for provider in providers:
            if await self.circuit_breaker.call(provider, message, rendered_template, subject):
                EMAILS_SENT.inc()
                logger.info(
                    f"Email sent successfully via {provider.__name__}",
                    extra={
                        "correlation_id": message.correlation_id,
                        "event": "email_sent",
                        "provider": provider.__name__
                    }
                )
                return True

        EMAILS_FAILED.inc()
        logger.error(
            "Failed to send email through all providers",
            extra={
                "correlation_id": message.correlation_id,
                "event": "email_send_failed"
            }
        )
        return False

    async def _send_via_smtp(self, message: EmailMessage, rendered_template: str, subject: str) -> bool:
        if not settings.smtp_host:
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = settings.smtp_user or "noreply@example.com"
            msg['To'] = message.to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(rendered_template, 'html'))

            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            raise e

    async def _send_via_sendgrid(self, message: EmailMessage, rendered_template: str, subject: str) -> bool:
        if not settings.sendgrid_api_key:
            return False

        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {settings.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "personalizations": [{
                    "to": [{"email": message.to_email}]
                }],
                "from": {"email": "noreply@example.com"},
                "subject": subject,
                "content": [{"type": "text/html", "value": rendered_template}]
            }
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"SendGrid send failed: {str(e)}")
            raise e

    async def _send_via_mailgun(self, message: EmailMessage, rendered_template: str, subject: str) -> bool:
        if not settings.mailgun_api_key or not settings.mailgun_domain:
            return False

        try:
            url = f"https://api.mailgun.net/v3/{settings.mailgun_domain}/messages"
            auth = ("api", settings.mailgun_api_key)
            data = {
                "from": f"noreply@{settings.mailgun_domain}",
                "to": message.to_email,
                "subject": subject,
                "html": rendered_template
            }
            response = requests.post(url, auth=auth, data=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Mailgun send failed: {str(e)}")
            raise e

    async def _send_via_gmail(self, message: EmailMessage, rendered_template: str, subject: str) -> bool:
        if not all([settings.gmail_client_id, settings.gmail_client_secret, settings.gmail_refresh_token]):
            return False

        # Implement Gmail API sending
        # This would require google-api-python-client
        # For now, return False
        return False
