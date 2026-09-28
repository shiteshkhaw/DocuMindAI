import logging
from typing import List, Dict, Any
from PIL import Image
from ocr.base import BaseOCRProvider

logger = logging.getLogger(__name__)


class MockOCRProvider(BaseOCRProvider):
    """
    Deterministic Mock OCR Provider for tests, CI, and local dev environments
    where external OCR binaries are not present.
    """

    def __init__(
        self,
        default_text: str = "Mock OCR Extracted Text Content",
        is_available_flag: bool = True
    ):
        self.default_text = default_text
        self._is_available = is_available_flag
        self.invocation_count: int = 0
        self.extracted_images: List[Any] = []
        self.custom_responses: Dict[int, str] = {}

    @property
    def name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return self._is_available

    def set_available(self, available: bool) -> None:
        self._is_available = available

    def set_response_for_call(self, call_index: int, text: str) -> None:
        """Map 1-indexed call number to custom OCR response string."""
        self.custom_responses[call_index] = text

    def extract_text_from_image(self, image: Image.Image | bytes) -> str:
        self.invocation_count += 1
        self.extracted_images.append(image)
        logger.debug(f"[MockOCR] Invocations: {self.invocation_count}")
        return self.custom_responses.get(self.invocation_count, self.default_text)
