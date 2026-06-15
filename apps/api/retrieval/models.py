from pydantic import BaseModel, Field
from typing import Dict, Any, List

class RetrievalItem(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float
    page_number: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievalItem]
    
    @property
    def merged_context(self) -> str:
        """Helper to join retrieval contexts together for feeding LLM prompts."""
        return "\n\n".join(
            f"[Source: Doc ID {item.document_id}, Page {item.page_number}] {item.text}"
            for item in self.results
        )
