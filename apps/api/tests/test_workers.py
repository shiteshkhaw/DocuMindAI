import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from workers import (
    ingest_document_worker,
    send_email_notification,
    run_background_cleanup,
    is_stub_broker,
)


def test_dramatiq_broker_configured() -> None:
    """Validate broker is loaded (either StubBroker in test mode or RedisBroker)."""
    assert is_stub_broker() is True


@pytest.mark.asyncio
@patch("orchestration.service.IngestionOrchestrator.ingest_document", new_callable=AsyncMock)
@patch("services.analysis.AnalysisService.get_or_create_analysis", new_callable=AsyncMock)
@patch("workers.email.send_email_notification.send")
async def test_ingest_document_worker_execution(
    mock_send_email, mock_get_analysis, mock_ingest
) -> None:
    """Validate worker task successfully runs ingestion, pre-computes analysis, and triggers email."""
    # Mock return model structures for analysis
    mock_analysis = MagicMock()
    mock_analysis.trust_score_json = {"score": 92.5}
    mock_get_analysis.return_value = mock_analysis

    # Setup database mocks
    mock_doc = MagicMock()
    mock_doc.id = "doc-123"
    mock_doc.name = "agreement.pdf"
    mock_doc.user_id = "user-123"
    mock_doc.workspace_id = "ws-123"

    mock_user = MagicMock()
    mock_user.email = "owner@domain.com"

    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_doc
    mock_result.scalar_one_or_none.return_value = mock_user

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    # Mock DB factory and storage download
    mock_storage = AsyncMock()
    mock_storage.download_file.return_value = b"content bytes"

    with patch("workers.document_ingestion.async_session_factory") as mock_factory, \
         patch("storage.get_storage_provider") as mock_storage_factory:
        mock_factory.return_value.__aenter__.return_value = mock_session
        mock_storage_factory.return_value = mock_storage

        # Run worker function
        ingest_document_worker(
            document_id="doc-123",
            storage_key="documents/doc-123/agreement.pdf",
            filename="agreement.pdf",
            mime_type="application/pdf",
            user_id="user-123",
            workspace_id="ws-123",
        )

        # Assert correct components were called in sequence
        mock_ingest.assert_called_once()
        mock_get_analysis.assert_called_once()
        mock_send_email.assert_called_once_with(
            email_type="analysis_completed",
            recipient="owner@domain.com",
            params={
                "doc_name": "agreement.pdf",
                "score": 92.5,
                "dashboard_url": "http://localhost:3000/workspaces/ws-123",
            },
        )


@pytest.mark.asyncio
@patch("services.email.email_service.send_welcome", new_callable=AsyncMock)
async def test_email_worker_execution(mock_send_welcome) -> None:
    """Validate email worker maps events to EmailService methods."""
    send_email_notification(
        email_type="welcome",
        recipient="user@domain.com",
        params={"name": "Bob"},
    )
    mock_send_welcome.assert_called_once_with(to="user@domain.com", name="Bob")


@pytest.mark.asyncio
async def test_cleanup_worker_execution() -> None:
    """Validate cleanup worker executes without errors."""
    run_background_cleanup()
    # If no exception is raised, it's successful
