import re
import unicodedata
from typing import List
from cleaners.base import BaseCleaner

class UnicodeNormalizer(BaseCleaner):
    def clean(self, text: str) -> str:
        # Standardize characters using NFKC normalization
        normalized = unicodedata.normalize("NFKC", text)
        # Standardize curly quotes, dashes, and other common unicode artifacts
        normalized = normalized.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        normalized = normalized.replace("–", "-").replace("—", "-")
        return normalized

class WhitespaceNormalizer(BaseCleaner):
    def clean(self, text: str) -> str:
        # Replace tabs with spaces
        text = text.replace("\t", " ")
        # Compress multiple spaces to a single space
        return re.sub(r"[ ]{2,}", " ", text)

class DuplicateNewlineNormalizer(BaseCleaner):
    def clean(self, text: str) -> str:
        # Collapse multiple consecutive newlines to a maximum of two newlines
        return re.sub(r"\n{3,}", "\n\n", text)

class InvalidCharacterCleaner(BaseCleaner):
    def clean(self, text: str) -> str:
        # Filter out control characters except tabs and newlines
        return "".join(c for c in text if unicodedata.category(c)[0] != "C" or c in "\n\t")

class PageArtifactCleaner(BaseCleaner):
    def __init__(self):
        # Match common page number formats: e.g., "Page 1 of 5", "- 3 -", "[Page 12]"
        self.patterns = [
            re.compile(r"^\s*page\s+\d+\s+of\s+\d+\s*$", re.IGNORECASE | re.MULTILINE),
            re.compile(r"^\s*-\s*\d+\s*-\s*$", re.IGNORECASE | re.MULTILINE),
            re.compile(r"^\s*\[\s*page\s+\d+\s*\]\s*$", re.IGNORECASE | re.MULTILINE),
            re.compile(r"^\s*page\s+\d+\s*$", re.IGNORECASE | re.MULTILINE),
        ]

    def clean(self, text: str) -> str:
        cleaned = text
        for pattern in self.patterns:
            cleaned = pattern.sub("", cleaned)
        return cleaned

class ContentCleanerPipeline:
    def __init__(self, cleaners: List[BaseCleaner] | None = None):
        if cleaners is not None:
            self.cleaners = cleaners
        else:
            self.cleaners = [
                UnicodeNormalizer(),
                InvalidCharacterCleaner(),
                PageArtifactCleaner(),
                WhitespaceNormalizer(),
                DuplicateNewlineNormalizer()
            ]

    def clean(self, text: str) -> str:
        result = text
        for cleaner in self.cleaners:
            result = cleaner.clean(result)
        return result.strip()
