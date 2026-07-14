import logging

from config import settings
from services.email.base import BaseEmailProvider, EmailResult
from services.email.resend_provider import ResendProvider
from services.email.templates import (
    get_welcome_template,
    get_password_reset_template,
    get_org_invitation_template,
    get_analysis_completed_template,
    get_processing_completed_template,
)

logger = logging.getLogger("documind.services.email.service")


class LoggingEmailProvider(BaseEmailProvider):
    """
    Fallback logging email provider used when RESEND_API_KEY is not configured.
    Prints rendered email fields to logs for local development.
    """

    async def send(
        self, to: str, subject: str, html: str, text: str | None = None
    ) -> EmailResult:
        logger.info(
            f"[EmailFallback] SIMULATING email delivery to: {to}\n"
            f"Subject: {subject}\n"
            f"Text snippet: {text[:200] if text else ''}..."
        )
        return EmailResult(message_id="fallback-local-msg", recipient=to, success=True)


class EmailService:
    """
    High-level email service handling template compilation and delivery.
    """

    def __init__(self, provider: BaseEmailProvider | None = None) -> None:
        if provider is not None:
            self.provider = provider
        elif settings.RESEND_API_KEY:
            self.provider = ResendProvider()
        else:
            self.provider = LoggingEmailProvider()

    async def send_welcome(self, to: str, name: str) -> EmailResult:
        html, text = get_welcome_template(name)
        return await self.provider.send(to, "Welcome to DocuMind AI", html, text)

    async def send_password_reset(self, to: str, reset_url: str) -> EmailResult:
        html, text = get_password_reset_template(reset_url)
        return await self.provider.send(to, "Reset your DocuMind AI password", html, text)

    async def send_org_invite(
        self, to: str, org_name: str, inviter_name: str, invite_url: str
    ) -> EmailResult:
        html, text = get_org_invitation_template(org_name, inviter_name, invite_url)
        return await self.provider.send(
            to, f"Invitation to join organization {org_name}", html, text
        )

    async def send_analysis_completed(
        self, to: str, doc_name: str, score: float, dashboard_url: str
    ) -> EmailResult:
        html, text = get_analysis_completed_template(doc_name, score, dashboard_url)
        return await self.provider.send(
            to, f"Analysis complete: {doc_name} (Trust Score: {score}%)", html, text
        )

    async def send_processing_completed(
        self, to: str, doc_name: str, dashboard_url: str
    ) -> EmailResult:
        html, text = get_processing_completed_template(doc_name, dashboard_url)
        return await self.provider.send(
            to, f"Document processing complete: {doc_name}", html, text
        )


# ── Module-level singleton ────────────────────────────────────────────────
email_service = EmailService()
