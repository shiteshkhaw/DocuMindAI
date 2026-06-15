import io
import asyncio
import hashlib
from typing import Dict, Any
from pypdf import PdfReader
from parsers.base import BaseParser, ParsedDocument, ParsedPage

class PDFParser(BaseParser):
    def can_handle(self, mime_type: str) -> bool:
        return mime_type.lower() == "application/pdf" or mime_type.lower().endswith("pdf")

    async def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        # Run parsing in a separate thread to prevent blocking FastAPI's main loop
        return await asyncio.to_thread(self._parse_sync, file_content, filename)

    def _parse_sync(self, file_content: bytes, filename: str) -> ParsedDocument:
        stream = io.BytesIO(file_content)
        reader = PdfReader(stream)
        
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(ParsedPage(
                page_number=i + 1,
                text=text,
                metadata={"source_page": i + 1}
            ))

        # Extract PDF metadata details
        info = reader.metadata or {}
        title = info.title if info.title else filename.rsplit(".", 1)[0]
        author = info.author if info.author else "Unknown"
        
        doc_metadata: Dict[str, Any] = {
            "title": title,
            "author": author,
            "page_count": len(reader.pages),
            "file_size": len(file_content),
            "mime_type": "application/pdf",
            "checksum": hashlib.sha256(file_content).hexdigest(),
        }
        
        return ParsedDocument(pages=pages, metadata=doc_metadata)
