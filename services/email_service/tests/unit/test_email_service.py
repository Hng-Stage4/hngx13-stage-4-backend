import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.email_service import EmailService
from app.models.email_message import EmailMessage


class TestEmailService:
    @pytest.fixture
    def email_service(self):
        return EmailService()

    @pytest.fixture
    def sample_message(self):
        return EmailMessage(
            correlation_id="test-123",
            to_email="test@example.com",
            template_id="welcome",
            variables={"name": "John", "company": "TestCo"}
        )

    @pytest.mark.asyncio
    async def test_send_email_success_smtp(self, email_service, sample_message):
        """Test successful email sending via SMTP"""
        with patch.object(email_service, '_send_via_smtp', new_callable=AsyncMock) as mock_smtp:
            mock_smtp.return_value = True

            result = await email_service.send_email(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is True
            mock_smtp.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_smtp_failure_fallback(self, email_service, sample_message):
        """Test SMTP failure with fallback to other providers"""
        with patch.object(email_service, '_send_via_smtp', new_callable=AsyncMock) as mock_smtp, \
             patch.object(email_service, '_send_via_sendgrid', new_callable=AsyncMock) as mock_sendgrid:

            mock_smtp.return_value = False
            mock_sendgrid.return_value = True

            result = await email_service.send_email(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is True
            mock_smtp.assert_called_once()
            mock_sendgrid.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_all_providers_fail(self, email_service, sample_message):
        """Test when all email providers fail"""
        with patch.object(email_service, '_send_via_smtp', new_callable=AsyncMock) as mock_smtp, \
             patch.object(email_service, '_send_via_sendgrid', new_callable=AsyncMock) as mock_sendgrid, \
             patch.object(email_service, '_send_via_mailgun', new_callable=AsyncMock) as mock_mailgun, \
             patch.object(email_service, '_send_via_gmail', new_callable=AsyncMock) as mock_gmail, \
             patch.object(email_service, '_send_via_zoho', new_callable=AsyncMock) as mock_zoho:

            mock_smtp.return_value = False
            mock_sendgrid.return_value = False
            mock_mailgun.return_value = False
            mock_gmail.return_value = False
            mock_zoho.return_value = False

            result = await email_service.send_email(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_send_via_smtp_success(self, email_service, sample_message):
        """Test SMTP provider success"""
        with patch('smtplib.SMTP') as mock_smtp_class:
            mock_smtp_instance = Mock()
            mock_smtp_class.return_value = mock_smtp_instance

            result = await email_service._send_via_smtp(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is True
            mock_smtp_class.assert_called_once()
            mock_smtp_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_via_smtp_no_config(self, email_service, sample_message):
        """Test SMTP provider when not configured"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.smtp_host = None

            result = await email_service._send_via_smtp(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_send_via_zoho_success(self, email_service, sample_message):
        """Test Zoho provider success"""
        with patch('app.services.email_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = await email_service._send_via_zoho(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_via_zoho_no_config(self, email_service, sample_message):
        """Test Zoho provider when not configured"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.zoho_api_key = None

            result = await email_service._send_via_zoho(
                sample_message,
                "<h1>Welcome John!</h1>",
                "Welcome to TestCo"
            )

            assert result is False
