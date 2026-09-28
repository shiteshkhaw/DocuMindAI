import io
import logging
import shutil
import time
from typing import Any
from PIL import Image
from config import settings
from ocr.base import BaseOCRProvider
from ocr.exceptions import (
    OCRError,
    OCRUnavailableError,
    OCRTimeoutError,
    OCRProcessingError,
)

logger = logging.getLogger(__name__)

# Security: Protect against decompression bombs from hostile/oversized images (50 MP max)
Image.MAX_IMAGE_PIXELS = 50_000_000


class TesseractOCRProvider(BaseOCRProvider):
    """
    Local OCR Provider leveraging Tesseract OCR via pytesseract.
    Conforms to enterprise standards: strictly non-blocking timeouts,
    decompression bomb prevention, and graceful degradation.
    """

    def __init__(
        self,
        lang: str | None = None,
        timeout_seconds: int | None = None,
        tesseract_cmd: str | None = None,
    ):
        self.lang = lang or getattr(settings, "OCR_LANGUAGE", "eng")
        self.timeout_seconds = timeout_seconds or getattr(settings, "OCR_TIMEOUT_SECONDS", 30)
        self._tesseract_cmd = tesseract_cmd or getattr(settings, "TESSERACT_CMD", None)
        self._pytesseract: Any = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "tesseract"

    def _ensure_pytesseract(self) -> Any:
        if not self._initialized:
            try:
                import pytesseract
                if self._tesseract_cmd:
                    pytesseract.pytesseract.tesseract_cmd = self._tesseract_cmd
                self._pytesseract = pytesseract
            except ImportError:
                self._pytesseract = None
            self._initialized = True
        return self._pytesseract

    def is_available(self) -> bool:
        pt = self._ensure_pytesseract()
        if pt is None:
            return False
        try:
            cmd = self._tesseract_cmd or getattr(pt.pytesseract, "tesseract_cmd", "tesseract")
            if shutil.which(cmd):
                return True
            # Secondary check: attempt version probe
            pt.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text_from_image(self, image: Image.Image | bytes) -> str:
        pt = self._ensure_pytesseract()
        if pt is None or not self.is_available():
            raise OCRUnavailableError(
                "Tesseract OCR engine is not installed or not available on the system PATH. "
                "Ensure 'tesseract' is installed or configure TESSERACT_CMD."
            )

        pil_image: Image.Image
        if isinstance(image, bytes):
            try:
                pil_image = Image.open(io.BytesIO(image))
            except Exception as e:
                raise OCRProcessingError(f"Failed to open image bytes for OCR: {e}") from e
        elif isinstance(image, Image.Image):
            pil_image = image
        else:
            raise OCRProcessingError(f"Unsupported image type for OCR: {type(image)}")

        # Convert palette/alpha channels to standard RGB or Grayscale for optimal recognition
        if pil_image.mode not in ("L", "RGB"):
            pil_image = pil_image.convert("RGB")

        try:
            t0 = time.perf_counter()
            text = pt.image_to_string(
                pil_image,
                lang=self.lang,
                timeout=self.timeout_seconds,
            )
            duration_ms = (time.perf_counter() - t0) * 1000
            extracted_len = len(text.strip()) if text else 0
            logger.info(
                f"[TesseractOCR] Extracted {extracted_len} chars in {duration_ms:.1f}ms "
                f"from {pil_image.width}x{pil_image.height} image"
            )
            return text or ""
        except getattr(pt, "TesseractNotFoundError", Exception) as e:
            raise OCRUnavailableError("Tesseract OCR binary not found.") from e
        except RuntimeError as e:
            err_str = str(e).lower()
            if "timeout" in err_str or "timed out" in err_str:
                raise OCRTimeoutError(
                    f"Tesseract OCR timed out after {self.timeout_seconds} seconds."
                ) from e
            raise OCRProcessingError(f"Tesseract OCR runtime error: {e}") from e
        except Exception as e:
            raise OCRProcessingError(f"Unexpected error during Tesseract OCR: {e}") from e
