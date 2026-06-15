import time
import json
import logging
import asyncio
from typing import AsyncGenerator, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from retrieval.service import RetrievalService
from context.optimizer import ContextOptimizer
from citations.attribution import AttributionEngine
from llm.registry import llm_registry
from llm.base import LLMMessage
from observability.logger import ExecutionTracker, log_llm_metrics
from repositories.document import DocumentRepository

logger = logging.getLogger("documind.orchestration.rag")

QUERY_EXPANSION_SYSTEM = """You are a search query optimizer.
Your task is to expand a user's query with relevant synonyms, related concepts, and alternative phrasings
to improve document retrieval precision.

Rules:
- Keep the expanded query concise (max 2.5x the original length)
- Preserve the original intent
- Add domain-specific terminology where appropriate
- Return ONLY the expanded query text, no explanation, no punctuation prefix
"""


class RAGOrchestrator:
    def __init__(
        self,
        db: AsyncSession,
        retrieval_service: RetrievalService,
        token_budget: int = 4000
    ):
        self.db = db
        self.retrieval_service = retrieval_service
        self.optimizer = ContextOptimizer(token_budget=token_budget)
        self.attribution_engine = AttributionEngine()
        self.doc_repo = DocumentRepository(db)

    async def _expand_query(self, query: str, provider_name: str, model: str) -> str:
        """
        Expand the user query using LLM to improve retrieval coverage.
        Falls back to original query on any failure.
        """
        try:
            provider = llm_registry.get_provider(provider_name)
            messages = [
                LLMMessage(role="system", content=QUERY_EXPANSION_SYSTEM),
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
                logger.info(
                    f"[RAG] Query expansion: '{query[:60]}' → '{expanded[:80]}'"
                )
                return expanded
        except Exception as e:
            logger.warning(f"[RAG] Query expansion failed (using original): {e}")

        return query

    async def execute_stream(
        self,
        session_id: str,
        query: str,
        document_ids: List[str],
        model_name: str,
        temperature: float = 0.2,
        chat_history: List[LLMMessage] | None = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Production RAG pipeline with query expansion, hybrid retrieval, and diagnostics streaming.
        Yields chunks: citations | retrieval_diagnostics | token | metrics | error
        """
        start_time = time.perf_counter()
        chat_history = chat_history or []

        # ── 0. Resolve LLM provider early (needed for query expansion) ────
        provider_name, actual_model = llm_registry.resolve_model_route(model_name)

        # ── 1. Query Expansion (concurrent with nothing else, but fast) ───
        expanded_query = await self._expand_query(query, provider_name, actual_model)

        # ── 2. Hybrid Retrieval ───────────────────────────────────────────
        with ExecutionTracker("RAG_Retrieval", {"query": query, "document_ids": document_ids}):
            retrieval_res = await self.retrieval_service.retrieve(
                query=query,
                document_ids=document_ids,
                limit=5,
                min_score=0.05,
                expanded_query=expanded_query if expanded_query != query else None,
            )

        logger.info(
            f"[RAG] Retrieved {len(retrieval_res.results)} chunk(s) for query='{query[:60]}' "
            f"document_ids={document_ids}"
        )
        if retrieval_res.results:
            scores = [f"{r.score:.3f}" for r in retrieval_res.results]
            logger.info(f"[RAG] Hybrid scores (top {len(scores)}): {scores}")
        else:
            logger.warning(
                "[RAG] Zero chunks retrieved — vector store may be empty or "
                "embeddings not yet ingested."
            )

        # ── 3. Lookup document names ──────────────────────────────────────
        doc_names: Dict[str, str] = {}
        if document_ids:
            for doc_id in document_ids:
                doc_m = await self.doc_repo.get(doc_id)
                if doc_m:
                    doc_names[doc_id] = doc_m.name

        # ── 4. Citations ──────────────────────────────────────────────────
        with ExecutionTracker("RAG_ContextOptimization"):
            opt_result = self.optimizer.optimize(retrieval_res.results, doc_names)

        citations = self.attribution_engine.format_citations(
            [r for r in retrieval_res.results if r.chunk_id in opt_result.selected_chunk_ids],
            doc_names
        )

        # Emit citations immediately so frontend shows source cards during stream
        yield {"type": "citations", "citations": citations}

        # ── 5. Retrieval Diagnostics (NEW) ────────────────────────────────
        diagnostics_chunks = []
        for r in retrieval_res.results:
            meta = r.metadata or {}
            diagnostics_chunks.append({
                "chunk_id": r.chunk_id,
                "document_id": r.document_id,
                "document_name": doc_names.get(r.document_id, r.document_id),
                "page": r.page_number,
                "hybrid_score": meta.get("_hybrid_score", r.score),
                "semantic_score": meta.get("_semantic_score", r.score),
                "keyword_score": meta.get("_keyword_score", 0.0),
                "preview": r.text[:120] + ("..." if len(r.text) > 120 else ""),
            })

        yield {
            "type": "retrieval_diagnostics",
            "original_query": query,
            "expanded_query": expanded_query if expanded_query != query else None,
            "chunks": diagnostics_chunks,
            "retrieval_count": len(retrieval_res.results),
        }

        # ── 6. Context Formatting ─────────────────────────────────────────
        if opt_result.formatted_context:
            context_block = opt_result.formatted_context
            logger.info(
                f"[RAG] Context: ~{opt_result.total_estimated_tokens} tokens, "
                f"{len(opt_result.selected_chunk_ids)} chunk(s)"
            )
        else:
            context_block = (
                "[NO DOCUMENT CONTEXT AVAILABLE]\n"
                "No relevant chunks were retrieved from the uploaded documents for this query. "
                "This may mean the document has not finished ingestion, or the query does not "
                "match any content in the selected files."
            )
            logger.warning("[RAG] Context block is EMPTY — LLM will be told no context available.")

        system_instruction = (
            "You are DocuMind AI, a premium semantic document intelligence assistant.\n"
            "Your objective is to provide highly precise, context-grounded, and objective responses "
            "based ONLY on the source context documents provided below. Do not make up facts.\n"
            "Always cite document names and page numbers (e.g. `[Document Name Page X]`) "
            "when referencing facts from the context.\n\n"
            f"{context_block}\n\n"
            "Answer the query comprehensively using only the context details. If the context does not "
            "contain the information needed, state that clearly."
        )

        messages = [LLMMessage(role="system", content=system_instruction)]
        messages.extend(chat_history[-5:])
        messages.append(LLMMessage(role="user", content=query))

        # ── 7. LLM Streaming ──────────────────────────────────────────────
        logger.info(f"[RAG] Routing to provider={provider_name} model={actual_model}")

        full_content = ""
        prompt_tokens = 0
        completion_tokens = 0

        try:
            provider = llm_registry.get_provider(provider_name)

            with ExecutionTracker("RAG_LLMGeneration", {"provider": provider_name, "model": actual_model}):
                async for chunk in provider.generate_stream(
                    messages=messages,
                    model=actual_model,
                    temperature=temperature
                ):
                    if chunk.token:
                        full_content += chunk.token
                        yield {"type": "token", "content": chunk.token}

                    if chunk.prompt_tokens is not None:
                        prompt_tokens = chunk.prompt_tokens
                    if chunk.completion_tokens is not None:
                        completion_tokens = chunk.completion_tokens

        except Exception as e:
            logger.error(f"[RAG] LLM stream error: {e}", exc_info=True)
            yield {"type": "error", "content": f"LLM generation failed: {str(e)}"}
            return

        # ── 8. Finalise metrics ───────────────────────────────────────────
        if prompt_tokens == 0:
            prompt_tokens = self.optimizer.estimate_tokens(system_instruction) + self.optimizer.estimate_tokens(query)
            completion_tokens = self.optimizer.estimate_tokens(full_content)

        duration = time.perf_counter() - start_time
        log_llm_metrics(
            session_id=session_id,
            model=actual_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_seconds=duration,
            retrieval_count=len(citations)
        )

        yield {
            "type": "metrics",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "duration_seconds": duration,
            "citations": citations,
            "full_content": full_content,
        }
