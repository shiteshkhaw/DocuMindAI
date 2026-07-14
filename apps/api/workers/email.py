import asyncio
import logging
import dramatiq

from services.email import email_service
from workers.broker import broker

logger = logging.getLogger("documind.workers.email")


async def _run_async_email(email_type: str, recipient: str, params: dict) -> None:
    """Async execution wrapper for sending emails."""
    logger.info(f"[EmailWorker] Dispatching {email_type} email to {recipient}")

    if email_type == "welcome":
        await email_service.send_welcome(
            to=recipient,
            name=params.get("name", "User"),
        )
    elif email_type == "password_reset":
        await email_service.send_password_reset(
            to=recipient,
            reset_url=params.get("reset_url", ""),
        )
    elif email_type == "org_invite":
        await email_service.send_org_invite(
            to=recipient,
            org_name=params.get("org_name", ""),
            inviter_name=params.get("inviter_name", ""),
            invite_url=params.get("invite_url", ""),
        )
    elif email_type == "analysis_completed":
        await email_service.send_analysis_completed(
            to=recipient,
            doc_name=params.get("doc_name", "Document"),
            score=params.get("score", 100.0),
            dashboard_url=params.get("dashboard_url", "http://localhost:3000"),
        )
    elif email_type == "processing_completed":
        await email_service.send_processing_completed(
            to=recipient,
            doc_name=params.get("doc_name", "Document"),
            dashboard_url=params.get("dashboard_url", "http://localhost:3000"),
        )
    else:
        logger.error(f"[EmailWorker] Unknown email type: {email_type}")


@dramatiq.actor(max_retries=5, min_backoff=5000, max_backoff=120000)
def send_email_notification(email_type: str, recipient: str, params: dict) -> None:
    """Dramatiq actor for async email delivery."""
    from workers.broker import run_async
    run_async(_run_async_email(email_type, recipient, params))
