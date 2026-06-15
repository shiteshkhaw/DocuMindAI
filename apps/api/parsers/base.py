from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ParsedPage(BaseModel):
    page_number: int
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParsedDocument(BaseModel):
    pages: List[ParsedPage]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages)

class BaseParser(ABC):
    @abstractmethod
    def can_handle(self, mime_type: str) -> bool:
        """Returns True if the parser can process the given mime_type."""
        pass

    @abstractmethod
    async def parse(self, file_content: bytes, filename: str) -> ParsedDocument:
        """Parses the raw file bytes asynchronously and returns structured content and metadata."""
        pass
