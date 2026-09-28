import io
import asyncio
import hashlib
import logging
from typing import Dict, Any, List
from PIL import Image
from pypdf import PdfReader
from parsers.base import BaseParser, ParsedDocument, ParsedPage
from ocr.base import BaseOCRProvider
from ocr.factory import get_ocr_provider
from config import settings

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    def __init__(self, ocr_provider: BaseOCRProvider | None = None):
        self._ocr_provider = ocr_provider

    @property
    def ocr_provider(self) -> BaseOCRProvider:
        if self._ocr_provider is not None:
            return self._ocr_provider
        return get_ocr_provider()

    def can_handle(self, mime_type: str) -> bool:
        return mime_type.lower() == "application/pdf" or mime_type.lower().endswith("pdf")

    async def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        # Run parsing in a separate thread to prevent blocking FastAPI's main loop
        return await asyncio.to_thread(self._parse_sync, file_content, filename)

    @staticmethod
    def _is_usable_text(text: str) -> bool:
        """
        Heuristic to determine if native PDF extraction produced sufficient usable text.
        Returns False for scanned/image-only pages, blank pages, or corrupt character noise.
        """
        clean = text.strip()
        if not clean:
            return False
        alnum_count = sum(1 for c in clean if c.isalnum())
        if len(clean) < 30:
            # Very short text (e.g. lone page number or artifact); require at least 20 alnum chars
            return alnum_count >= 20
        # For longer text, verify at least 20% alphanumeric ratio to filter out gibberish/corrupt streams
        return (alnum_count / len(clean)) >= 0.2

    def _parse_sync(self, file_content: bytes, filename: str) -> ParsedDocument:
        stream = io.BytesIO(file_content)
        reader = PdfReader(stream)

        pages: List[ParsedPage] = []
        ocr_pages_count = 0
        provider = self.ocr_provider
        max_ocr_pages = getattr(settings, "OCR_MAX_PAGES", 100)

        for i, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""

            # 1. Native Extraction Check: If usable text is found, use it directly (0 OCR overhead)
            if self._is_usable_text(raw_text):
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text=raw_text,
                    metadata={
                        "source_page": i + 1,
                        "extraction_method": "native",
                    }
                ))
                continue

            # 2. Text is insufficient; check if page contains raster images
            page_images = []
            try:
                if hasattr(page, "images"):
                    page_images = list(page.images)
            except Exception as img_err:
                logger.warning(f"[PDFParser] Error reading page images on page {i + 1}: {img_err}")

            if not page_images:
                # Blank page with no readable text and no embedded images
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text=raw_text,
                    metadata={
                        "source_page": i + 1,
                        "extraction_method": "native",
                    }
                ))
                continue

            # 3. Scanned/Image-only page: check limits & OCR availability
            if ocr_pages_count >= max_ocr_pages:
                logger.warning(
                    f"[PDFParser] Document exceeded maximum OCR page budget ({max_ocr_pages}). "
                    f"Skipping OCR on page {i + 1}."
                )
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text=raw_text,
                    metadata={
                        "source_page": i + 1,
                        "extraction_method": "native",
                        "ocr_skipped": "limit_exceeded",
                    }
                ))
                continue

            if not provider.is_available():
                logger.warning(
                    f"[PDFParser] Page {i + 1} requires OCR, but OCR provider '{provider.name}' is unavailable."
                )
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text=raw_text,
                    metadata={
                        "source_page": i + 1,
                        "extraction_method": "native",
                        "ocr_attempted": False,
                        "ocr_error": f"OCR provider '{provider.name}' is unavailable",
                    }
                ))
                continue

            # 4. Perform OCR on the page images
            try:
                logger.info(
                    f"[PDFParser] Performing OCR on page {i + 1}/{len(reader.pages)} "
                    f"({len(page_images)} image(s)) via '{provider.name}'"
                )
                images_to_process: List[Image.Image | bytes] = []
                for img_obj in page_images:
                    if hasattr(img_obj, "image"):
                        try:
                            pil_candidate = getattr(img_obj, "image")
                            if isinstance(pil_candidate, Image.Image):
                                images_to_process.append(pil_candidate)
                                continue
                        except Exception:
                            pass
                    if hasattr(img_obj, "data"):
                        raw_data = getattr(img_obj, "data")
                        if isinstance(raw_data, bytes) and raw_data:
                            images_to_process.append(raw_data)

                ocr_text = provider.extract_text_from_images(images_to_process)

                if ocr_text and ocr_text.strip():
                    pages.append(ParsedPage(
                        page_number=i + 1,
                        text=ocr_text.strip(),
                        metadata={
                            "source_page": i + 1,
                            "extraction_method": "ocr",
                            "ocr_provider": provider.name,
                        }
                    ))
                    ocr_pages_count += 1
                else:
                    logger.warning(f"[PDFParser] OCR extraction yielded empty text for page {i + 1}")
                    pages.append(ParsedPage(
                        page_number=i + 1,
                        text=raw_text,
                        metadata={
                            "source_page": i + 1,
                            "extraction_method": "ocr",
                            "ocr_provider": provider.name,
                            "ocr_empty": True,
                        }
                    ))
            except Exception as ocr_err:
                logger.error(f"[PDFParser] OCR failed on page {i + 1}: {ocr_err}")
                pages.append(ParsedPage(
                    page_number=i + 1,
                    text=raw_text,
                    metadata={
                        "source_page": i + 1,
                        "extraction_method": "native",
                        "ocr_error": str(ocr_err),
                    }
                ))

        # Extract PDF metadata details safely
        info = reader.metadata
        title: str = filename.rsplit(".", 1)[0]
        author: str = "Unknown"
        if info is not None:
            extracted_title = getattr(info, "title", None) or (info.get("title") if isinstance(info, dict) else None)
            if extracted_title:
                title = str(extracted_title)
            extracted_author = getattr(info, "author", None) or (info.get("author") if isinstance(info, dict) else None)
            if extracted_author:
                author = str(extracted_author)

        # Determine overall document extraction method
        total_pages = len(reader.pages)
        if ocr_pages_count == 0:
            extraction_method = "native"
        elif ocr_pages_count == total_pages:
            extraction_method = "ocr"
        else:
            extraction_method = "hybrid"

        doc_metadata: Dict[str, Any] = {
            "title": title,
            "author": author,
            "page_count": total_pages,
            "file_size": len(file_content),
            "mime_type": "application/pdf",
            "checksum": hashlib.sha256(file_content).hexdigest(),
            "extraction_method": extraction_method,
            "ocr_pages_count": ocr_pages_count,
        }
        if ocr_pages_count > 0:
            doc_metadata["ocr_provider"] = provider.name

        return ParsedDocument(pages=pages, metadata=doc_metadata)
