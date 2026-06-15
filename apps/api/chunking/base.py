from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class Tokenizer(ABC):
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Returns the number of tokens in the text."""
        pass


class CharacterEstimateTokenizer(Tokenizer):
    """Fallback tokenizer: estimates ~4 characters per English token."""
    def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


class TiktokenTokenizer(Tokenizer):
    """
    Production-grade BPE tokenizer using OpenAI's cl100k_base encoding.
    This matches the encoding used by text-embedding-3-small and GPT-4,
    ensuring chunk sizes are accurate for both embedding and LLM context budgets.
    """
    def __init__(self, encoding_name: str = "cl100k_base"):
        try:
            import tiktoken
            self._enc = tiktoken.get_encoding(encoding_name)
            logger.info(f"[Tokenizer] TiktokenTokenizer initialised with encoding '{encoding_name}'")
        except ImportError:
            logger.warning(
                "[Tokenizer] tiktoken is not installed. Falling back to CharacterEstimateTokenizer. "
                "Install with: pip install tiktoken>=0.7.0"
            )
            self._enc = None
        self._fallback = CharacterEstimateTokenizer()

    def count_tokens(self, text: str) -> int:
        if self._enc is not None:
            try:
                # disallowed_special=() prevents errors on documents with <|special|> tokens
                return len(self._enc.encode(text, disallowed_special=()))
            except Exception as e:
                logger.debug(f"[Tokenizer] tiktoken encode failed, using fallback: {e}")
        return self._fallback.count_tokens(text)


def get_default_tokenizer() -> Tokenizer:
    """Returns TiktokenTokenizer with automatic fallback to CharacterEstimateTokenizer."""
    return TiktokenTokenizer()


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    page_number: int
    token_count: int
    char_offset_start: int
    char_offset_end: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseChunker(ABC):
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        tokenizer: Tokenizer | None = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tokenizer or get_default_tokenizer()

    @abstractmethod
    def split(self, document_id: str, pages: List[Any]) -> List[DocumentChunk]:
        """Splits the parsed pages into structured document chunks."""
        pass
