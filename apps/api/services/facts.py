import uuid
import logging
from typing import List, Dict, Any
from services.fact_extraction import FactExtractionService as CoreFactExtractionService

logger = logging.getLogger("documind.services.facts")

class FactExtractionService:
    def __init__(self):
        self.core_service = CoreFactExtractionService()

    async def extract_facts(
        self,
        chunks: List[str],
        document_id: str,
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract facts and shape them into the requested format:
        { id, type, subject, predicate, value, confidence, page, chunk_id, evidence }
        """
        logger.info(f"[FactsService] Starting extraction for doc={document_id}")
        raw_facts = await self.core_service.extract_facts(chunks, document_id, metadatas)
        
        formatted_facts = []
        for fact in raw_facts:
            evidence_list = fact.get("evidence", [])
            evidence_text = evidence_list[0].get("text", "") if evidence_list else ""
            chunk_idx = evidence_list[0].get("chunk_index", 0) if evidence_list else 0
            
            formatted_facts.append({
                "id": fact.get("id") or f"fact-{uuid.uuid4()}",
                "type": fact.get("fact_type") or "definitional",
                "subject": fact.get("subject", ""),
                "predicate": fact.get("predicate", ""),
                "value": fact.get("object_value", ""),
                "confidence": fact.get("confidence", 0.7),
                "page": fact.get("page") or 1,
                "chunk_id": f"chunk-{chunk_idx}",
                "evidence": evidence_text
            })
            
        logger.info(f"[FactsService] Extracted {len(formatted_facts)} facts for doc={document_id}")
        return formatted_facts
