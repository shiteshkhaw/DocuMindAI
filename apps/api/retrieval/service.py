import logging
import time
from typing import List, Dict, Any
from config import settings
from embeddings.base import BaseEmbeddingProvider
from vectorstore.base import BaseVectorStore
from retrieval.models import RetrievalResponse, RetrievalItem
from retrieval.hybrid import HybridRanker
from retrieval.reranker import CrossEncoderReranker

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Production retrieval service with hybrid (semantic + BM25) ranking.
    
    Pipeline:
        1. Embed query → cosine similarity search in Chroma
        2. HybridRanker re-scores using BM25 (keyword matching)
        3. Filter by min_score on the hybrid score
        4. Return top-k ranked results with diagnostics
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.collection_name = "documind_chunks"
        self._ranker = HybridRanker(semantic_weight=0.7, keyword_weight=0.3)
        self.reranker = CrossEncoderReranker(
            embedding_provider=embedding_provider,
            hf_api_key=settings.HF_API_KEY
        )


    async def _expand_query_internal(self, query: str) -> str:
        """Expand user query with synonyms and terminology using LLM."""
        try:
            from llm.registry import llm_registry
            from llm.base import LLMMessage
            provider_name, model = llm_registry.resolve_model_route("documind-v3")
            provider = llm_registry.get_provider(provider_name)
            
            system_prompt = (
                "You are a search query optimizer.\n"
                "Your task is to expand a user's query with relevant synonyms, related concepts, and alternative phrasings "
                "to improve document retrieval precision.\n\n"
                "Rules:\n"
                "- Keep the expanded query concise (max 2.5x the original length)\n"
                "- Preserve the original intent\n"
                "- Add domain-specific terminology where appropriate\n"
                "- Return ONLY the expanded query text, no explanation, no punctuation prefix\n"
            )
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"Original query: {query}"),
            ]
            expanded = ""
            async for chunk in provider.generate_stream(
                messages=messages,
                model=model,
                temperature=0.0,
                max_tokens=200,
                timeout=10.0,
            ):
                if chunk.token:
                    expanded += chunk.token

            expanded = expanded.strip()
            if expanded and len(expanded) > 5:
                logger.info(f"[Retrieval] Internal query expansion: '{query[:60]}' → '{expanded[:80]}'")
                return expanded
        except Exception as e:
            logger.warning(f"[Retrieval] Internal query expansion failed (using original): {e}")
        return query

    async def retrieve(
        self,
        query: str,
        document_ids: List[str] | None = None,
        limit: int = 5,
        min_score: float = 0.05,
        expanded_query: str | None = None,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ) -> RetrievalResponse:
        """
        Hybrid semantic + keyword retrieval.

        Args:
            query: Original user query
            document_ids: Filter results to these documents (empty = search all)
            limit: Maximum number of results to return after re-ranking
            min_score: Minimum hybrid score threshold (0–1)
            expanded_query: Optional expanded/enriched query for BM25 scoring

        Returns:
            RetrievalResponse with ranked items and diagnostics metadata
        """
        start_time = time.perf_counter()

        # ── 1. Embed query ─────────────────────────────────────────────────
        if expanded_query is None:
            expanded_query = await self._expand_query_internal(query)

        embed_query_text = expanded_query or query
        logger.info(f"[Retrieval] Embedding query: '{embed_query_text[:80]}'")
        query_vector = await self.embedding_provider.embed_query(embed_query_text)

        # ── 2. Build metadata filter ───────────────────────────────────────
        filter_meta: Dict[str, Any] = {}
        if document_ids:
            if len(document_ids) == 1:
                filter_meta["document_id"] = document_ids[0]
            else:
                filter_meta["document_id"] = document_ids  # Chroma $in operator
        if user_id:
            filter_meta["user_id"] = user_id
        if workspace_id:
            filter_meta["workspace_id"] = workspace_id

        # Fetch exactly 30 candidate chunks for cross-encoder reranking
        fetch_limit = 30

        # ── 3. Vector similarity search ────────────────────────────────────
        logger.info(
            f"[Retrieval] Querying Chroma '{self.collection_name}' | "
            f"limit={fetch_limit} filters={filter_meta}"
        )
        raw_results = await self.vector_store.query(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=fetch_limit,
            filter_meta=filter_meta or None,
        )

        if not raw_results:
            logger.warning(
                f"[Retrieval] Zero raw results from Chroma for query='{query[:60]}'. "
                f"Collection may be empty or filter_meta={filter_meta} is over-constrained."
            )
            return RetrievalResponse(query=query, results=[])

        # ── 4. Hybrid re-ranking ───────────────────────────────────────────
        chunk_ids = [r[0] for r in raw_results]
        sem_scores = [r[1] for r in raw_results]
        doc_texts = [r[2] for r in raw_results]
        metadatas = [r[3] for r in raw_results]

        bm25_query = expanded_query or query
        ranked = self._ranker.rerank(
            query=bm25_query,
            chunk_ids=chunk_ids,
            documents=doc_texts,
            semantic_scores=sem_scores,
        )

        # ── 5. Build final result list with Cross-Encoder reranking ────────
        chunk_id_to_raw: Dict[str, int] = {cid: i for i, cid in enumerate(chunk_ids)}

        items: List[RetrievalItem] = []
        rejected = 0

        try:
            reranked_results = await self.reranker.rerank(
                query=bm25_query,
                chunks=doc_texts,
                chunk_ids=chunk_ids
            )
        except Exception as e:
            logger.warning(f"[Retrieval] CrossEncoder reranking failed: {e}. Falling back to hybrid ranking order.")
            reranked_results = []
            for cid, hybrid_score, sem_score, kw_score in ranked:
                raw_idx = chunk_id_to_raw[cid]
                reranked_results.append((cid, hybrid_score, doc_texts[raw_idx]))

        for cid, ce_score, chunk_text in reranked_results:
            if ce_score < min_score:
                rejected += 1
                continue
            if len(items) >= limit:
                break

            raw_idx = chunk_id_to_raw[cid]
            meta = metadatas[raw_idx]

            doc_id = meta.get("document_id", "unknown")
            page_num = int(meta.get("page_number", 1))

            orig_hybrid = 0.0
            orig_sem = 0.0
            orig_kw = 0.0
            for rank_cid, h_s, s_s, k_s in ranked:
                if rank_cid == cid:
                    orig_hybrid = h_s
                    orig_sem = s_s
                    orig_kw = k_s
                    break

            items.append(RetrievalItem(
                chunk_id=cid,
                document_id=doc_id,
                text=chunk_text,
                score=round(ce_score, 4),
                page_number=page_num,
                metadata={
                    **meta,
                    "_cross_encoder_score": round(ce_score, 4),
                    "_hybrid_score": round(orig_hybrid, 4),
                    "_semantic_score": round(orig_sem, 4),
                    "_keyword_score": round(orig_kw, 4),
                },
            ))

        retrieval_time_ms = (time.perf_counter() - start_time) * 1000.0

        if not items:
            logger.warning(
                f"[Retrieval] All {len(raw_results)} candidates filtered below "
                f"min_score={min_score} (rejected={rejected}). "
                f"Consider lowering min_score."
            )
        else:
            top_scores = [f"ce={r.score:.3f}" for r in items[:3]]
            logger.info(
                f"[Retrieval] Success in {retrieval_time_ms:.1f}ms | "
                f"kept={len(items)}/{len(raw_results)} | "
                f"top_scores={top_scores}"
            )

        return RetrievalResponse(query=query, results=items)
