class OCRError(Exception):
    """Base exception for all OCR-related errors in DocuMind AI."""
    pass


class OCRUnavailableError(OCRError):
    """Raised when an OCR operation is requested but no OCR provider is available."""
    pass


class OCRTimeoutError(OCRError):
    """Raised when OCR processing exceeds configured time limit."""
    pass


class OCRProcessingError(OCRError):
    """Raised when an error occurs during OCR image processing or text recognition."""
    pass
