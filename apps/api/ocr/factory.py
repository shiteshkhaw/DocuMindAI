import logging
from config import settings
from ocr.base import BaseOCRProvider
from ocr.tesseract import TesseractOCRProvider
from ocr.mock import MockOCRProvider

logger = logging.getLogger(__name__)

_ocr_provider: BaseOCRProvider | None = None


def get_ocr_provider(provider_type: str | None = None) -> BaseOCRProvider:
    """
    Resolve and return the singleton OCR provider instance.
    Follows DocuMind's provider resolution patterns.
    """
    global _ocr_provider
    if _ocr_provider is not None and provider_type is None:
        return _ocr_provider

    chosen = (provider_type or getattr(settings, "OCR_PROVIDER", "auto")).lower()

    if chosen == "mock":
        provider = MockOCRProvider()
    elif chosen == "tesseract":
        provider = TesseractOCRProvider()
    elif chosen == "auto":
        tesseract = TesseractOCRProvider()
        if tesseract.is_available():
            provider = tesseract
        else:
            logger.info(
                "[OCR] Tesseract binary not detected in environment. "
                "Operating in safe fallback mode (OCR unavailable unless configured)."
            )
            provider = tesseract
    else:
        logger.warning(f"[OCR] Unknown provider '{chosen}'. Defaulting to Tesseract.")
        provider = TesseractOCRProvider()

    if provider_type is None:
        _ocr_provider = provider

    logger.debug(f"[OCR] Active OCR provider: {provider.name}")
    return provider


def set_ocr_provider(provider: BaseOCRProvider | None) -> None:
    """Explicitly override the active OCR provider (useful for unit testing)."""
    global _ocr_provider
    _ocr_provider = provider
