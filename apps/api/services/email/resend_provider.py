import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from services.email.base import BaseEmailProvider, EmailResult

logger = logging.getLogger("documind.services.email.resend")


class ResendProvider(BaseEmailProvider):
    """
    Concrete Resend provider implementing email delivery.
    Wraps the Resend client inside asyncio.to_thread to maintain non-blocking execution.
    """

    def __init__(self) -> None:
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM
        
        # Instantiate Resend client
        import resend
        resend.api_key = self.api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def send(
        self, to: str, subject: str, html: str, text: str | None = None
    ) -> EmailResult:
        logger.info(f"[EmailResend] Sending email to {to} | Subject: {subject}")
        import resend

        params = {
            "from": self.from_email,
            "to": to,
            "subject": subject,
            "html": html,
        }
        if text:
            params["text"] = text

        try:
            # Wrap SDK call in thread to avoid blocking FastAPI event loop
            response = await asyncio.to_thread(resend.Emails.send, params)
            message_id = response.get("id") or "unknown-msg-id"
            return EmailResult(message_id=message_id, recipient=to, success=True)
        except Exception as exc:
            logger.error(f"[EmailResend] Failed to send email to {to}: {exc}")
            return EmailResult(
                message_id="failed", recipient=to, success=False, error=str(exc)
            )
