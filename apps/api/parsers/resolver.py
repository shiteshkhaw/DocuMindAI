import os
from typing import List
from fastapi import HTTPException
from parsers.base import BaseParser, ParsedDocument
from parsers.pdf import PDFParser
from parsers.docx import DocxParser
from parsers.txt import TxtParser
from parsers.markdown import MarkdownParser

class DocumentParserResolver:
    def __init__(self):
        self._parsers: List[BaseParser] = [
            PDFParser(),
            DocxParser(),
            TxtParser(),
            MarkdownParser()
        ]

    def resolve(self, filename: str, mime_type: str | None = None) -> BaseParser:
        # If mime_type is not provided, deduce from file extension
        resolved_mime = mime_type
        if not resolved_mime:
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".pdf":
                resolved_mime = "application/pdf"
            elif ext in [".docx", ".doc"]:
                resolved_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext in [".md", ".markdown"]:
                resolved_mime = "text/markdown"
            elif ext == ".txt":
                resolved_mime = "text/plain"
            else:
                resolved_mime = "application/octet-stream"

        for parser in self._parsers:
            if parser.can_handle(resolved_mime):
                return parser

        # Fallback to TxtParser if it's text-based, or raise HTTP 400
        if resolved_mime.startswith("text/"):
            return TxtParser()
            
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format for ingestion: {filename} (MIME: {resolved_mime})"
        )

    async def parse_document(self, file_content: bytes, filename: str, mime_type: str | None = None) -> ParsedDocument:
        parser = self.resolve(filename, mime_type)
        return await parser.parse(file_content, filename)
