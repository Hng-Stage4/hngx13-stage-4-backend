from fastapi import APIRouter, Request, HTTPException, Depends
from app.services.webhook_service import WebhookService
from app.utils.logger import logger
from app.routers.metrics import WEBHOOK_EVENTS_RECEIVED

router = APIRouter()

@router.post("/sendgrid")
async def sendgrid_webhook(request: Request, webhook_service: WebhookService = Depends()):
    """Handle SendGrid webhook events for delivery confirmations and bounces"""
    try:
        # SendGrid sends events as JSON array
        events = await request.json()
        if not isinstance(events, list):
            events = [events]

        processed_count = 0
        for event in events:
            await webhook_service.process_sendgrid_event(event)
            processed_count += 1

        WEBHOOK_EVENTS_RECEIVED.inc(processed_count)
        logger.info(f"Processed {processed_count} SendGrid events")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"SendGrid webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/mailgun")
async def mailgun_webhook(request: Request, webhook_service: WebhookService = Depends()):
    """Handle Mailgun webhook events for delivery confirmations and bounces"""
    try:
        # Mailgun sends events as form data
        form_data = await request.form()
        event_data = dict(form_data)

        await webhook_service.process_mailgun_event(event_data)
        WEBHOOK_EVENTS_RECEIVED.inc()
        logger.info("Processed Mailgun event")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Mailgun webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/smtp/bounce")
async def smtp_bounce_webhook(request: Request, webhook_service: WebhookService = Depends()):
    """Handle SMTP bounce notifications (would be called by SMTP server callbacks)"""
    try:
        bounce_data = await request.json()
        await webhook_service.process_smtp_bounce(bounce_data)
        WEBHOOK_EVENTS_RECEIVED.inc()
        logger.info("Processed SMTP bounce event")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"SMTP bounce webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/zoho")
async def zoho_webhook(request: Request, webhook_service: WebhookService = Depends()):
    """Handle Zoho Mail webhook events for delivery confirmations and bounces"""
    try:
        event_data = await request.json()
        await webhook_service.process_zoho_event(event_data)
        WEBHOOK_EVENTS_RECEIVED.inc()
        logger.info("Processed Zoho event")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Zoho webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
