from abc import ABC, abstractmethod
from typing import List
import math

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generates embedding for a single query string."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of document chunks."""
        pass

    def normalize(self, vector: List[float]) -> List[float]:
        """Normalizes a vector to unit length (L2 norm) for clean cosine similarity."""
        magnitude = math.sqrt(sum(val ** 2 for val in vector))
        if magnitude == 0:
            return vector
        return [val / magnitude for val in vector]
