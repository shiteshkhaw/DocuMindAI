import hashlib
import asyncio
import re
from typing import Dict, Any
from parsers.base import BaseParser, ParsedDocument, ParsedPage

class MarkdownParser(BaseParser):
    def can_handle(self, mime_type: str) -> bool:
        return mime_type.lower() in [
            "text/markdown",
            "text/x-markdown"
        ] or mime_type.lower().endswith("md") or mime_type.lower().endswith("markdown")

    async def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        return await asyncio.to_thread(self._parse_sync, file_content, filename)

    def _parse_sync(self, file_content: bytes, filename: str) -> ParsedDocument:
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1")

        # Try to find a title from first H1 header: # Title
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename.rsplit(".", 1)[0]

        pages = [ParsedPage(
            page_number=1,
            text=text,
            metadata={"source_page": 1}
        )]

        doc_metadata: Dict[str, Any] = {
            "title": title,
            "author": "Unknown",
            "page_count": 1,
            "file_size": len(file_content),
            "mime_type": "text/markdown",
            "checksum": hashlib.sha256(file_content).hexdigest(),
        }

        return ParsedDocument(pages=pages, metadata=doc_metadata)
