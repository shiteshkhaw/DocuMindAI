from typing import List, Dict, Any
from pydantic import BaseModel

class Citation(BaseModel):
    documentId: str
    documentName: str
    pageNumber: int
    snippet: str
    score: float

class AttributionEngine:
    def format_citations(self, retrieval_results: List[Any], doc_names: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Formats vector hits into serialized JSON-friendly Citation shapes.
        """
        citations = []
        for item in retrieval_results:
            doc_name = doc_names.get(item.document_id, "Source Document")
            
            # Extract a neat snippet preview
            snippet = item.text.strip()
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
                
            citations.append({
                "documentId": item.document_id,
                "documentName": doc_name,
                "pageNumber": item.page_number,
                "snippet": snippet,
                "score": float(item.score)
            })
        return citations
