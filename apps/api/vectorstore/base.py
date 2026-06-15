from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseVectorStore(ABC):
    @abstractmethod
    async def create_collection(self, collection_name: str) -> None:
        """Creates a collection/index if it does not exist."""
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> None:
        """Deletes an entire collection/index."""
        pass

    @abstractmethod
    async def upsert(
        self,
        collection_name: str,
        ids: List[str],
        vectors: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Upserts vectors and associated documents and metadata into the vector store."""
        pass

    @abstractmethod
    async def delete(
        self,
        collection_name: str,
        ids: List[str] | None = None,
        filter_meta: Dict[str, Any] | None = None
    ) -> None:
        """Deletes vectors matching ids or metadata filter."""
        pass

    @abstractmethod
    async def query(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_meta: Dict[str, Any] | None = None
    ) -> List[Tuple[str, float, str, Dict[str, Any]]]:
        """
        Queries the vector store for nearest neighbors.
        Returns a list of tuples: (id, similarity_score, document_content, metadata)
        """
        pass

    @abstractmethod
    async def count(self, collection_name: str) -> int:
        """Returns the number of vectors in the collection."""
        pass

