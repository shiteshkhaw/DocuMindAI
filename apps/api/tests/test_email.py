import pytest
from unittest.mock import MagicMock, patch

from services.email import email_service, EmailResult
from services.email.service import LoggingEmailProvider, EmailService
from services.email.templates import (
    get_welcome_template,
    get_password_reset_template,
    get_org_invitation_template,
    get_analysis_completed_template,
    get_processing_completed_template,
)


def test_email_templates_render() -> None:
    """Validate all HTML and text templates render with variables included."""
    # 1. Welcome
    html, text = get_welcome_template("Alice")
    assert "Alice" in html
    assert "Alice" in text

    # 2. Password Reset
    html, text = get_password_reset_template("http://localhost:3000/reset?token=123")
    assert "http://localhost:3000/reset?token=123" in html
    assert "http://localhost:3000/reset?token=123" in text

    # 3. Org invite
    html, text = get_org_invitation_template("Acme", "Bob", "http://localhost:3000/invite")
    assert "Acme" in html
    assert "Bob" in html
    assert "http://localhost:3000/invite" in text

    # 4. Analysis Complete
    html, text = get_analysis_completed_template("contract.pdf", 87.5, "http://localhost:3000/doc/1")
    assert "contract.pdf" in html
    assert "87.5%" in html
    assert "http://localhost:3000/doc/1" in text

    # 5. Processing Complete
    html, text = get_processing_completed_template("rules.docx", "http://localhost:3000/doc/2")
    assert "rules.docx" in html
    assert "http://localhost:3000/doc/2" in text


@pytest.mark.asyncio
async def test_logging_email_provider() -> None:
    """Validate LoggingEmailProvider emulates success correctly."""
    provider = LoggingEmailProvider()
    result = await provider.send("test@example.com", "Test Subject", "<p>Hello</p>", "Hello")
    assert isinstance(result, EmailResult)
    assert result.success is True
    assert result.recipient == "test@example.com"
    assert result.message_id == "fallback-local-msg"


@pytest.mark.asyncio
@patch("resend.Emails.send")
async def test_resend_email_provider(mock_resend_send) -> None:
    """Validate ResendProvider uses the resend SDK and handles responses."""
    mock_resend_send.return_value = {"id": "resend-msg-123"}

    # Mock settings to return an API Key
    with patch("config.settings.RESEND_API_KEY", "re_123456789"):
        from services.email.resend_provider import ResendProvider

        provider = ResendProvider()
        result = await provider.send("user@domain.com", "Subject", "<h1>Hi</h1>", "Hi")

        assert result.success is True
        assert result.message_id == "resend-msg-123"
        mock_resend_send.assert_called_once()
