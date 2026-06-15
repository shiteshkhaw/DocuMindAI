import pytest
from unittest.mock import MagicMock, patch

from parsers.resolver import DocumentParserResolver
from parsers.txt import TxtParser
from parsers.markdown import MarkdownParser
from parsers.pdf import PDFParser
from parsers.docx import DocxParser
from parsers.base import ParsedDocument


async def test_txt_parser() -> None:
    parser = TxtParser()
    assert parser.can_handle("text/plain") is True
    assert parser.can_handle("some_file.txt") is True
    assert parser.can_handle("application/pdf") is False

    content = b"Hello DocuMind AI!\nThis is a simple text file."
    doc = await parser.parse(content, "test_file.txt")

    assert isinstance(doc, ParsedDocument)
    assert len(doc.pages) == 1
    assert doc.pages[0].page_number == 1
    assert "Hello DocuMind" in doc.pages[0].text
    assert doc.metadata["title"] == "test_file"
    assert doc.metadata["page_count"] == 1
    assert doc.metadata["file_size"] == len(content)


async def test_markdown_parser() -> None:
    parser = MarkdownParser()
    assert parser.can_handle("text/markdown") is True
    assert parser.can_handle("test.md") is True

    content = b"# DocuMind Architecture\n\nSome design principles."
    doc = await parser.parse(content, "arch.md")
    assert doc.metadata["title"] == "DocuMind Architecture"
    assert "design principles" in doc.pages[0].text

    content_no_h1 = b"No header, just text."
    doc_no_h1 = await parser.parse(content_no_h1, "arch_no_h1.md")
    assert doc_no_h1.metadata["title"] == "arch_no_h1"


async def test_pdf_parser_mocked() -> None:
    parser = PDFParser()
    assert parser.can_handle("application/pdf") is True

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Extracted PDF text content page 1"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.metadata.title = "Sample PDF Title"
    mock_reader.metadata.author = "Google DeepMind"

    with patch("parsers.pdf.PdfReader", return_value=mock_reader):
        doc = await parser.parse(b"%PDF-1.4 mock content", "sample.pdf")

        assert len(doc.pages) == 1
        assert doc.pages[0].text == "Extracted PDF text content page 1"
        assert doc.metadata["title"] == "Sample PDF Title"
        assert doc.metadata["author"] == "Google DeepMind"
        assert doc.metadata["page_count"] == 1


async def test_docx_parser_mocked() -> None:
    parser = DocxParser()
    assert parser.can_handle(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ) is True

    mock_p1 = MagicMock()
    mock_p1.text = "Hello from DOCX!"
    mock_p2 = MagicMock()
    mock_p2.text = "Second line."

    mock_doc = MagicMock()
    mock_doc.paragraphs = [mock_p1, mock_p2]
    mock_doc.core_properties.title = "Docx Sample Title"
    mock_doc.core_properties.author = "DocuMind Interns"

    with patch("parsers.docx.docx.Document", return_value=mock_doc):
        doc = await parser.parse(b"mock zip stream", "test.docx")

        assert len(doc.pages) == 1
        assert "Hello from DOCX!" in doc.pages[0].text
        assert "Second line." in doc.pages[0].text
        assert doc.metadata["title"] == "Docx Sample Title"
        assert doc.metadata["author"] == "DocuMind Interns"


def test_document_parser_resolver() -> None:
    from fastapi import HTTPException

    resolver = DocumentParserResolver()

    assert isinstance(resolver.resolve("doc.pdf"), PDFParser)
    assert isinstance(resolver.resolve("doc.docx"), DocxParser)
    assert isinstance(resolver.resolve("doc.doc"), DocxParser)
    assert isinstance(resolver.resolve("doc.md"), MarkdownParser)
    assert isinstance(resolver.resolve("doc.markdown"), MarkdownParser)
    assert isinstance(resolver.resolve("doc.txt"), TxtParser)

    assert isinstance(resolver.resolve("unknown_file", "application/pdf"), PDFParser)
    assert isinstance(resolver.resolve("unknown_file", "text/markdown"), MarkdownParser)

    # text/* MIME falls back to TxtParser
    assert isinstance(resolver.resolve("unknown_file", "text/html"), TxtParser)

    with pytest.raises(HTTPException) as exc_info:
        resolver.resolve("binary.bin", "application/octet-stream")
    assert exc_info.value.status_code == 400
