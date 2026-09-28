import io
import pytest
from unittest.mock import MagicMock, patch
from reportlab.pdfgen import canvas  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped]
from reportlab.lib.utils import ImageReader  # type: ignore[import-untyped]
from PIL import Image

from parsers.pdf import PDFParser
from parsers.docx import DocxParser
from parsers.markdown import MarkdownParser
from parsers.txt import TxtParser
from parsers.resolver import DocumentParserResolver
from ocr.base import BaseOCRProvider
from ocr.mock import MockOCRProvider
from ocr.tesseract import TesseractOCRProvider
from ocr.factory import get_ocr_provider, set_ocr_provider
from ocr.exceptions import OCRUnavailableError, OCRTimeoutError, OCRProcessingError
from chunking.engine import SemanticBoundaryChunker
from citations.attribution import AttributionEngine
from retrieval.models import RetrievalItem


# ── PDF Test Fixture Generators ─────────────────────────────────────────────

def generate_text_pdf(text: str = "This is a standard text PDF with rich readable content for DocuMind.") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, text)
    c.showPage()
    c.save()
    return buf.getvalue()


def generate_scanned_image_pdf() -> bytes:
    img = Image.new("RGB", (150, 100), color="blue")
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    img_buf.seek(0)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawImage(ImageReader(img_buf), 100, 500, width=150, height=100)
    c.showPage()
    c.save()
    return buf.getvalue()


def generate_mixed_pdf() -> bytes:
    img = Image.new("RGB", (150, 100), color="green")
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    img_buf.seek(0)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    # Page 1: Native text
    c.drawString(100, 700, "Native Page One Content: Enterprise DocuMind intelligence report intro.")
    c.showPage()

    # Page 2: Scanned image
    c.drawImage(ImageReader(img_buf), 100, 500, width=150, height=100)
    c.showPage()

    # Page 3: Native text
    c.drawString(100, 700, "Native Page Three Content: Concluding observations and enterprise metrics.")
    c.showPage()

    c.save()
    return buf.getvalue()


# ── Test 1: Normal Text PDF (Zero OCR Overhead) ─────────────────────────────

@pytest.mark.asyncio
async def test_normal_text_pdf_zero_ocr():
    mock_ocr = MockOCRProvider()
    parser = PDFParser(ocr_provider=mock_ocr)

    pdf_bytes = generate_text_pdf("Native text paragraph with sufficient character length for testing.")
    doc = await parser.parse(pdf_bytes, "native_doc.pdf")

    assert len(doc.pages) == 1
    assert "Native text paragraph" in doc.pages[0].text
    assert doc.pages[0].metadata["extraction_method"] == "native"
    assert doc.pages[0].page_number == 1

    # Crucial guarantee: OCR was NEVER called
    assert mock_ocr.invocation_count == 0
    assert doc.metadata["extraction_method"] == "native"
    assert doc.metadata["ocr_pages_count"] == 0
    assert "ocr_provider" not in doc.metadata


# ── Test 2: Scanned Image-only PDF ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_scanned_image_only_pdf_triggers_ocr():
    mock_ocr = MockOCRProvider(default_text="Extracted text from invoice scan via MockOCR.")
    parser = PDFParser(ocr_provider=mock_ocr)

    pdf_bytes = generate_scanned_image_pdf()
    doc = await parser.parse(pdf_bytes, "scanned_doc.pdf")

    assert len(doc.pages) == 1
    assert doc.pages[0].text == "Extracted text from invoice scan via MockOCR."
    assert doc.pages[0].metadata["extraction_method"] == "ocr"
    assert doc.pages[0].metadata["ocr_provider"] == "mock"
    assert doc.pages[0].page_number == 1

    # OCR was invoked for the scanned page
    assert mock_ocr.invocation_count == 1
    assert doc.metadata["extraction_method"] == "ocr"
    assert doc.metadata["ocr_pages_count"] == 1
    assert doc.metadata["ocr_provider"] == "mock"


# ── Test 3: Mixed PDF (Page-level Detection & Routing) ──────────────────────

@pytest.mark.asyncio
async def test_mixed_pdf_page_by_page_routing():
    mock_ocr = MockOCRProvider()
    mock_ocr.set_response_for_call(1, "Page 2 OCR Scanned Receipt Text.")
    parser = PDFParser(ocr_provider=mock_ocr)

    pdf_bytes = generate_mixed_pdf()
    doc = await parser.parse(pdf_bytes, "mixed_doc.pdf")

    assert len(doc.pages) == 3

    # Page 1: Native
    assert "Native Page One Content" in doc.pages[0].text
    assert doc.pages[0].metadata["extraction_method"] == "native"
    assert doc.pages[0].page_number == 1

    # Page 2: OCR
    assert doc.pages[1].text == "Page 2 OCR Scanned Receipt Text."
    assert doc.pages[1].metadata["extraction_method"] == "ocr"
    assert doc.pages[1].metadata["ocr_provider"] == "mock"
    assert doc.pages[1].page_number == 2

    # Page 3: Native
    assert "Native Page Three Content" in doc.pages[2].text
    assert doc.pages[2].metadata["extraction_method"] == "native"
    assert doc.pages[2].page_number == 3

    # Document-level metadata: hybrid
    assert doc.metadata["extraction_method"] == "hybrid"
    assert doc.metadata["ocr_pages_count"] == 1
    assert doc.metadata["ocr_provider"] == "mock"

    # OCR was only called for Page 2, NOT Page 1 or 3
    assert mock_ocr.invocation_count == 1


# ── Test 4: OCR Failure Handling (Graceful Degradation) ─────────────────────

@pytest.mark.asyncio
async def test_ocr_unavailable_graceful_handling():
    mock_ocr = MockOCRProvider(is_available_flag=False)
    parser = PDFParser(ocr_provider=mock_ocr)

    pdf_bytes = generate_scanned_image_pdf()
    doc = await parser.parse(pdf_bytes, "scanned_doc.pdf")

    # Document parsing does not crash
    assert len(doc.pages) == 1
    assert doc.pages[0].metadata["extraction_method"] == "native"
    assert doc.pages[0].metadata.get("ocr_attempted") is False
    assert "unavailable" in doc.pages[0].metadata.get("ocr_error", "")
    assert doc.metadata["extraction_method"] == "native"
    assert doc.metadata["ocr_pages_count"] == 0


@pytest.mark.asyncio
async def test_ocr_exception_during_extraction_does_not_crash():
    mock_ocr = MagicMock(spec=BaseOCRProvider)
    mock_ocr.name = "failing_ocr"
    mock_ocr.is_available.return_value = True
    mock_ocr.extract_text_from_images.side_effect = RuntimeError("OCR engine crashed unexpectedly")

    parser = PDFParser(ocr_provider=mock_ocr)
    pdf_bytes = generate_scanned_image_pdf()

    # Parsing catches exception per page and continues
    doc = await parser.parse(pdf_bytes, "scanned_doc.pdf")
    assert len(doc.pages) == 1
    assert "OCR engine crashed" in doc.pages[0].metadata.get("ocr_error", "")


# ── Test 5: Citation & Page Metadata Provenance ─────────────────────────────

@pytest.mark.asyncio
async def test_citation_page_provenance_preserved_for_ocr_content():
    mock_ocr = MockOCRProvider()
    mock_ocr.set_response_for_call(1, "Scanned Section on Page 2: Financial revenue reached $50 million.")
    parser = PDFParser(ocr_provider=mock_ocr)

    pdf_bytes = generate_mixed_pdf()
    doc = await parser.parse(pdf_bytes, "financials.pdf")

    # Pass pages through existing chunking engine with chunk_size sized to separate pages
    chunker = SemanticBoundaryChunker(chunk_size=20, chunk_overlap=0)
    chunks = chunker.split(document_id="doc-123", pages=doc.pages)

    assert len(chunks) >= 3

    # Find the chunk corresponding to Page 2
    page_2_chunks = [c for c in chunks if c.page_number == 2]
    assert len(page_2_chunks) >= 1
    assert "Financial revenue reached $50 million" in page_2_chunks[0].content
    assert page_2_chunks[0].page_number == 2

    # Verify AttributionEngine builds citation pointing to pageNumber 2
    retrieval_item = RetrievalItem(
        chunk_id=page_2_chunks[0].id,
        document_id="doc-123",
        text=page_2_chunks[0].content,
        score=0.92,
        page_number=page_2_chunks[0].page_number,
    )
    attribution_engine = AttributionEngine()
    citations = attribution_engine.format_citations(
        retrieval_results=[retrieval_item],
        doc_names={"doc-123": "financials.pdf"}
    )

    assert len(citations) == 1
    assert citations[0]["documentId"] == "doc-123"
    assert citations[0]["documentName"] == "financials.pdf"
    assert citations[0]["pageNumber"] == 2
    assert "Financial revenue" in citations[0]["snippet"]


# ── Test 6: Existing Formats Unaffected (DOCX, Markdown, TXT) ───────────────

@pytest.mark.asyncio
async def test_existing_parsers_unaffected():
    resolver = DocumentParserResolver()

    # TXT parser
    txt_doc = await resolver.parse_document(b"Simple plain text file content.", "file.txt")
    assert txt_doc.pages[0].page_number == 1
    assert "Simple plain text" in txt_doc.pages[0].text
    assert txt_doc.metadata["mime_type"] == "text/plain"

    # Markdown parser
    md_doc = await resolver.parse_document(b"# Title\n\nMarkdown document body.", "file.md")
    assert md_doc.pages[0].page_number == 1
    assert "Markdown document body" in md_doc.pages[0].text
    assert md_doc.metadata["mime_type"] == "text/markdown"

    # PDF resolver
    pdf_parser = resolver.resolve("report.pdf")
    assert isinstance(pdf_parser, PDFParser)


# ── Test 7: Security Limits (OCR Max Pages Budget) ──────────────────────────

@pytest.mark.asyncio
async def test_ocr_max_pages_limit_budget():
    mock_ocr = MockOCRProvider()
    parser = PDFParser(ocr_provider=mock_ocr)

    # Generate a 2-page scanned PDF
    img = Image.new("RGB", (100, 100), color="red")
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    img_buf.seek(0)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawImage(ImageReader(img_buf), 100, 500, width=100, height=100)
    c.showPage()
    img_buf.seek(0)
    c.drawImage(ImageReader(img_buf), 100, 500, width=100, height=100)
    c.showPage()
    c.save()

    # Patch OCR_MAX_PAGES to 1
    with patch("parsers.pdf.settings.OCR_MAX_PAGES", 1):
        doc = await parser.parse(buf.getvalue(), "oversized_scan.pdf")
        assert len(doc.pages) == 2
        # Page 1 gets OCR
        assert doc.pages[0].metadata["extraction_method"] == "ocr"
        # Page 2 skips OCR due to limit
        assert doc.pages[1].metadata.get("ocr_skipped") == "limit_exceeded"
        assert mock_ocr.invocation_count == 1


# ── Test 8: TesseractOCRProvider Unit & Failure Modes ────────────────────────

def test_tesseract_provider_availability():
    tesseract = TesseractOCRProvider()
    # When tesseract is not installed in the environment, is_available() returns False safely
    assert isinstance(tesseract.is_available(), bool)
    assert tesseract.name == "tesseract"


def test_tesseract_provider_raises_when_unavailable():
    tesseract = TesseractOCRProvider()
    with patch.object(tesseract, "is_available", return_value=False):
        with pytest.raises(OCRUnavailableError) as exc_info:
            tesseract.extract_text_from_image(b"fake image bytes")
        assert "not installed or not available" in str(exc_info.value)


# ── Test 9: End-to-End Pipeline Ingestion with Scanned PDF ──────────────────

@pytest.mark.asyncio
async def test_end_to_end_scanned_pdf_ingestion_pipeline(test_db):
    from models.document import DocumentModel
    from orchestration.service import IngestionOrchestrator
    from embeddings.providers import MockEmbeddingProvider
    from vectorstore.chroma import ChromaVectorStore

    doc_id = "doc-ocr-e2e-001"
    doc_model = DocumentModel(
        id=doc_id,
        name="scanned_invoice.pdf",
        storage_url="local://storage/scanned_invoice.pdf",
        status="queued",
        metadata_json={},
        user_id="test-user-123",
    )
    test_db.add(doc_model)
    await test_db.commit()

    mock_ocr = MockOCRProvider(default_text="Invoice #1024 Total Due: $4,500.00. Payment terms: 30 days.")
    set_ocr_provider(mock_ocr)
    try:
        embedding_provider = MockEmbeddingProvider(dimension=1536)
        vector_store = ChromaVectorStore()
        orchestrator = IngestionOrchestrator(
            db=test_db,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )

        pdf_bytes = generate_scanned_image_pdf()
        await orchestrator.ingest_document(
            document_id=doc_id,
            file_content=pdf_bytes,
            filename="scanned_invoice.pdf",
            mime_type="application/pdf",
            user_id="test-user-123",
        )

        await test_db.refresh(doc_model)
        assert doc_model.status == "COMPLETED"
        assert doc_model.progress_percentage == 100
        assert doc_model.metadata_json["extraction_method"] == "ocr"
        assert doc_model.metadata_json["ocr_pages_count"] == 1
        assert doc_model.metadata_json["ocr_provider"] == "mock"
        assert doc_model.metadata_json["chunks_count"] >= 1
    finally:
        set_ocr_provider(None)


@pytest.mark.asyncio
async def test_scanned_pdf_fails_gracefully_when_ocr_unavailable(test_db):
    from models.document import DocumentModel
    from orchestration.service import IngestionOrchestrator
    from embeddings.providers import MockEmbeddingProvider
    from vectorstore.chroma import ChromaVectorStore

    doc_id = "doc-ocr-fail-002"
    doc_model = DocumentModel(
        id=doc_id,
        name="scanned_no_engine.pdf",
        storage_url="local://storage/scanned_no_engine.pdf",
        status="queued",
        metadata_json={},
        user_id="test-user-123",
    )
    test_db.add(doc_model)
    await test_db.commit()

    mock_ocr = MockOCRProvider(is_available_flag=False)
    set_ocr_provider(mock_ocr)
    try:
        embedding_provider = MockEmbeddingProvider(dimension=1536)
        vector_store = ChromaVectorStore()
        orchestrator = IngestionOrchestrator(
            db=test_db,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )

        pdf_bytes = generate_scanned_image_pdf()
        with pytest.raises(ValueError) as exc_info:
            await orchestrator.ingest_document(
                document_id=doc_id,
                file_content=pdf_bytes,
                filename="scanned_no_engine.pdf",
                mime_type="application/pdf",
                user_id="test-user-123",
            )
        assert "readable text content" in str(exc_info.value)

        await test_db.refresh(doc_model)
        assert doc_model.status == "FAILED"
        assert doc_model.failure_reason is not None and "readable text content" in doc_model.failure_reason
    finally:
        set_ocr_provider(None)

