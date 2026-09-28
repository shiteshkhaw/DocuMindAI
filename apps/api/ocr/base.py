from abc import ABC, abstractmethod
from typing import List, Any
from PIL import Image


class BaseOCRProvider(ABC):
    """
    Abstract interface for OCR extraction providers in DocuMind AI.
    Isolates document ingestion and parsing from specific OCR backends.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'tesseract', 'mock')."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the OCR provider and required runtime binaries are operational."""
        pass

    @abstractmethod
    def extract_text_from_image(self, image: Image.Image | bytes) -> str:
        """
        Extracts recognized text from a single image (PIL Image instance or raw bytes).
        Raises OCRError or subclass on fatal processing errors.
        """
        pass

    def extract_text_from_images(self, images: List[Image.Image | bytes]) -> str:
        """
        Extracts recognized text from multiple images and concatenates with clean double-newlines.
        """
        chunks = []
        for img in images:
            text = self.extract_text_from_image(img)
            if text and text.strip():
                chunks.append(text.strip())
        return "\n\n".join(chunks)
