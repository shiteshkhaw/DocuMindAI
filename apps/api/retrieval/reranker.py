import logging
import asyncio
from typing import List, Dict, Any, Tuple
import httpx
from embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        hf_api_key: str | None = None,
        model: str = "BAAI/bge-reranker-large",
        timeout: float = 10.0
    ):
        self.embedding_provider = embedding_provider
        self.hf_api_key = hf_api_key
        self.model = model
        self.url = f"https://api-inference.huggingface.co/models/{model}"
        self.timeout = timeout

    async def rerank(
        self,
        query: str,
        chunks: List[str],
        chunk_ids: List[str]
    ) -> List[Tuple[str, float, str]]:
        """
        Reranks document chunks using Cross-Encoder.
        If hf_api_key is present, queries Hugging Face Inference API.
        Otherwise (or on failure), falls back to local scoring.
        
        Returns:
            List of (chunk_id, score, chunk_text)
        """
        if not chunks:
            return []

        if self.hf_api_key:
            try:
                scores = await self._query_hf(query, chunks)
                if len(scores) == len(chunks):
                    logger.info(f"[Reranker] Successfully reranked {len(chunks)} chunks using HF Serverless API.")
                    ranked = sorted(
                        zip(chunk_ids, scores, chunks),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    return ranked
            except Exception as e:
                logger.warning(f"[Reranker] HF Serverless Inference failed, falling back to local: {e}")

        # Local fallback
        logger.info(f"[Reranker] Using local semantic + token-overlap fallback to rerank {len(chunks)} chunks.")
        scores = await self._local_fallback(query, chunks)
        ranked = sorted(
            zip(chunk_ids, scores, chunks),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked

    async def _query_hf(self, query: str, chunks: List[str]) -> List[float]:
        # Formulate payload for cross-encoder sequence classification
        payload = {
            "inputs": [{"text": query, "text_pair": chunk} for chunk in chunks]
        }
        headers = {}
        if self.hf_api_key:
            headers["Authorization"] = f"Bearer {self.hf_api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.url, json=payload, headers=headers)
            if response.status_code == 503:
                # Model loading, wait and retry once
                logger.warning("[Reranker] HuggingFace model loading (503). Retrying in 3 seconds...")
                await asyncio.sleep(3.0)
                response = await client.post(self.url, json=payload, headers=headers)
            
            response.raise_for_status()
            res_data = response.json()

        # Parse response
        # BAAI/bge-reranker-large is sequence classification.
        # HF response usually looks like:
        # [
        #   [{"label": "LABEL_0", "score": 0.99}],  # For pair 0
        #   [{"label": "LABEL_0", "score": 0.01}],  # For pair 1
        #   ...
        # ]
        # or simplified structures.
        scores: List[float] = []
        if isinstance(res_data, list):
            for item in res_data:
                if isinstance(item, list):
                    if item and isinstance(item[0], dict) and "score" in item[0]:
                        scores.append(float(item[0]["score"]))
                    else:
                        scores.append(0.0)
                elif isinstance(item, dict):
                    if "score" in item:
                        scores.append(float(item["score"]))
                    else:
                        scores.append(0.0)
                elif isinstance(item, (int, float)):
                    scores.append(float(item))
                else:
                    scores.append(0.0)
        else:
            raise ValueError(f"Unexpected HF response format: {res_data}")

        return scores

    async def _local_fallback(self, query: str, chunks: List[str]) -> List[float]:
        # Token intersection score
        query_words = set(query.lower().split())
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "is", "are", "of", "that", "this"}
        query_words = {w for w in query_words if len(w) > 1 and w not in stopwords}
        if not query_words:
            query_words = set(query.lower().split())

        intersection_scores: List[float] = []
        for chunk in chunks:
            chunk_words = set(chunk.lower().split())
            if not query_words:
                intersection_scores.append(0.0)
            else:
                intersect = query_words.intersection(chunk_words)
                intersection_scores.append(len(intersect) / len(query_words))

        # Semantic cosine similarity score using embedding_provider
        try:
            query_vector = await self.embedding_provider.embed_query(query)
            chunk_vectors = await self.embedding_provider.embed_documents(chunks)
            
            q_norm = self.embedding_provider.normalize(query_vector)
            semantic_scores: List[float] = []
            for cv in chunk_vectors:
                cv_norm = self.embedding_provider.normalize(cv)
                cos_sim = sum(q * c for q, c in zip(q_norm, cv_norm))
                semantic_scores.append(cos_sim)
        except Exception as e:
            logger.warning(f"[Reranker] Local semantic embedding failed: {e}")
            semantic_scores = [0.0] * len(chunks)

        # Combine scores
        combined_scores: List[float] = []
        for item_intersect, item_semantic in zip(intersection_scores, semantic_scores):
            if item_semantic > 0.0:
                # Cosine similarity is [-1, 1], map it to [0, 1] for scaling
                scaled_semantic = (item_semantic + 1.0) / 2.0
                combined_scores.append(0.3 * item_intersect + 0.7 * scaled_semantic)
            else:
                combined_scores.append(item_intersect)

        return combined_scores
