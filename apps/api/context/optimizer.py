import logging
from typing import List, Dict, Any
from pydantic import BaseModel
from chunking.base import TiktokenTokenizer

logger = logging.getLogger("documind.context.optimizer")

class OptimizationResult(BaseModel):
    formatted_context: str
    selected_chunk_ids: List[str]
    total_estimated_tokens: int

class ContextOptimizer:
    def __init__(self, token_budget: int = 4000):
        self.token_budget = token_budget
        self.tokenizer = TiktokenTokenizer()

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens using cl100k_base tiktoken.
        """
        return self.tokenizer.count_tokens(text)

    def optimize(self, retrieval_results: List[Any], doc_names: Dict[str, str]) -> OptimizationResult:
        """
        Optimizes and groups semantic chunks for LLM ingestion.
        - Prioritizes by relevance score
        - Eliminates duplicates
        - Enforces token budgeting
        - Groups chunks from the same document sorted by page number
        """
        # 1. Deduplicate & score filter
        seen_texts = set()
        unique_results = []
        
        for item in retrieval_results:
            normalized_text = item.text.strip().lower()
            # Basic semantic/exact deduplication
            if normalized_text in seen_texts:
                continue
            
            seen_texts.add(normalized_text)
            unique_results.append(item)

        # 2. Token Budgeting
        budget_used = 0
        allocated_results = []
        
        for item in unique_results:
            estimated_chunk_tokens = self.estimate_tokens(item.text)
            # Add a small buffer for formatting headers (approx 30 tokens)
            chunk_cost = estimated_chunk_tokens + 30
            
            if budget_used + chunk_cost <= self.token_budget:
                budget_used += chunk_cost
                allocated_results.append(item)
            else:
                # Truncate or ignore remaining lower-priority chunks
                logger.info(f"Token budget exceeded, omitting chunk {item.chunk_id} from document {item.document_id}")
                break

        # 3. Group by Document & Sort by Page (Metadata-aware grouping)
        # This keeps the logical flow of the original document for the LLM
        grouped_chunks: Dict[str, List[Any]] = {}
        for item in allocated_results:
            doc_id = item.document_id
            if doc_id not in grouped_chunks:
                grouped_chunks[doc_id] = []
            grouped_chunks[doc_id].append(item)

        # Sort each group by page number
        for doc_id in grouped_chunks:
            grouped_chunks[doc_id].sort(key=lambda x: x.page_number)

        # 4. Compose Context Block
        formatted_parts = []
        selected_ids = []
        
        for doc_id, chunks in grouped_chunks.items():
            doc_name = doc_names.get(doc_id, "Unknown Source")
            formatted_parts.append(f"=== SOURCE DOCUMENT: {doc_name} ===")
            
            for chunk in chunks:
                selected_ids.append(chunk.chunk_id)
                formatted_parts.append(
                    f"[Page {chunk.page_number} | Relevance: {chunk.score:.2f}]:\n"
                    f"{chunk.text}\n"
                    f"---"
                )
            formatted_parts.append("") # spacer

        formatted_context = "\n".join(formatted_parts).strip()
        
        return OptimizationResult(
            formatted_context=formatted_context,
            selected_chunk_ids=selected_ids,
            total_estimated_tokens=budget_used
        )
