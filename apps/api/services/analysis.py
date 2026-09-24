import uuid
import json
import re
import logging
import asyncio
import time
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models.analysis import DocumentAnalysisModel
from repositories.analysis import DocumentAnalysisRepository
from repositories.document import DocumentRepository

logger = logging.getLogger("documind.services.analysis")

_analysis_locks: dict[str, asyncio.Lock] = {}
_MAX_LOCKS = 500  # bound the lock dict to prevent unbounded memory growth

class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentAnalysisRepository(db)
        self.doc_repo = DocumentRepository(db)

    async def get_or_create_analysis(self, document_id: str) -> DocumentAnalysisModel:
        # 1. Check Redis Cache first (Section 7 Requirements)
        from services.cache import cache_service
        cached_data = await cache_service.get("analysis", "document", document_id)
        if cached_data:
            logger.info(f"[Analysis] Cache HIT in Redis for doc={document_id}")
            analyzed_at = None
            if cached_data.get("analyzed_at"):
                try:
                    analyzed_at = datetime.fromisoformat(cached_data["analyzed_at"])
                except Exception:
                    analyzed_at = None
            if not analyzed_at:
                analyzed_at = datetime.now(timezone.utc).replace(tzinfo=None)

            return DocumentAnalysisModel(
                id=cached_data["id"],
                document_id=cached_data["document_id"],
                summary_json=cached_data["summary_json"],
                entities_json=cached_data["entities_json"],
                kv_pairs_json=cached_data["kv_pairs_json"],
                entity_conflicts_json=cached_data.get("entity_conflicts_json"),
                facts_json=cached_data.get("facts_json"),
                semantic_conflicts_json=cached_data.get("semantic_conflicts_json"),
                ambiguities_json=cached_data.get("ambiguities_json"),
                references_json=cached_data.get("references_json"),
                requirements_json=cached_data.get("requirements_json"),
                trust_score_json=cached_data.get("trust_score_json"),
                executive_summary_json=cached_data.get("executive_summary_json"),
                review_json=cached_data.get("review_json"),
                analyzed_at=analyzed_at
            )

        if document_id not in _analysis_locks:
            # Evict oldest entry if we hit the cap
            if len(_analysis_locks) >= _MAX_LOCKS:
                oldest_key = next(iter(_analysis_locks))
                del _analysis_locks[oldest_key]
            _analysis_locks[document_id] = asyncio.Lock()
            
        async with _analysis_locks[document_id]:
            # Double-check under lock in case another coroutine just created it
            analysis = await self.repo.get_by_document_id(document_id)
            if analysis:
                logger.info(f"[Analysis] Returning cached analysis from DB for doc={document_id}")
                # Save to cache for subsequent requests
                await self._write_to_redis_cache(analysis)
                return analysis

            # Load document name
            doc = await self.doc_repo.get(document_id)
            doc_name = doc.name if doc else "Unknown Document"

            return await self._compute_and_persist_analysis(document_id, doc_name)

    async def _compute_and_persist_analysis(self, document_id: str, doc_name: str) -> DocumentAnalysisModel:
        # Fetch document chunks from ChromaDB
        chunks_text, chunks_meta = await self._fetch_document_chunks(document_id)

        if not chunks_text:
            logger.warning(
                f"[Analysis] No chunks found for doc={document_id}. "
                f"Document may not be ingested yet."
            )
            return await self._create_empty_analysis(document_id)

        # ── Stage 1: Parallel extraction of base representations ───────────────
        # Entity extraction, Fact extraction, Deterministic contradictions,
        # Ambiguities, References, and Requirements are independent of each other.
        from services.entity import EntityGraphService
        from services.facts import FactExtractionService
        from services.deterministic_contradiction import DeterministicContradictionDetector
        from services.ambiguity import AmbiguityDetectionService
        from services.reference import ReferenceIntegrityService
        from services.requirements import RequirementTraceabilityService

        entity_service = EntityGraphService(self.repo.db)
        fact_service = FactExtractionService()
        det_detector = DeterministicContradictionDetector()
        ambiguity_service = AmbiguityDetectionService()
        reference_service = ReferenceIntegrityService()
        requirements_service = RequirementTraceabilityService()

        logger.info(
            f"[Analysis] Running Stage 1 parallel extractions for doc={document_id} "
            f"on {len(chunks_text)} chunks"
        )
        t_stage1 = time.perf_counter()
        stage1_results = await asyncio.gather(
            entity_service.analyze_entities(chunks_text, document_id, doc_name),
            fact_service.extract_facts(chunks=chunks_text, document_id=document_id, metadatas=chunks_meta),
            asyncio.to_thread(det_detector.detect, chunks=chunks_text, metadatas=chunks_meta, document_id=document_id, doc_name=doc_name),
            ambiguity_service.detect_ambiguities(chunks=chunks_text, metadatas=chunks_meta),
            reference_service.verify_references(chunks=chunks_text, metadatas=chunks_meta),
            requirements_service.generate_matrix(chunks=chunks_text, metadatas=chunks_meta),
            return_exceptions=True
        )
        logger.info(
            f"[Analysis] Stage 1 parallel extractions complete for doc={document_id} in "
            f"{(time.perf_counter()-t_stage1)*1000:.1f}ms"
        )

        extracted = stage1_results[0] if not isinstance(stage1_results[0], BaseException) else {}
        facts = stage1_results[1] if not isinstance(stage1_results[1], BaseException) else []
        deterministic_conflicts = stage1_results[2] if not isinstance(stage1_results[2], BaseException) else []
        ambiguities = stage1_results[3] if not isinstance(stage1_results[3], BaseException) else []
        references = stage1_results[4] if not isinstance(stage1_results[4], BaseException) else []
        requirements = stage1_results[5] if not isinstance(stage1_results[5], BaseException) else []

        entities = extracted.get("entities", [])
        entity_conflicts = extracted.get("entityConflicts", [])
        kv_pairs = extracted.get("keyValuePairs", [])
        summary_data = extracted.get("summary", {})

        # Assign stable IDs
        for ent in entities:
            ent["id"] = ent.get("id") or f"ent-{uuid.uuid4()}"
            ent["frequency"] = ent.get("frequency") or len(ent.get("mentions", []))
            if "related_entities" not in ent:
                ent["related_entities"] = []

        for kv in kv_pairs:
            kv["id"] = kv.get("id") or f"kv-{uuid.uuid4()}"

        # ── Stage 2: Parallel Inconsistency & Semantic Conflict Discovery ─────
        from services.entity_consistency import EntityConsistencyService
        from services.semantic_conflict import SemanticConflictDiscovery

        consistency_service = EntityConsistencyService()
        embedding_provider = None
        try:
            from services.dependencies import get_embedding_provider
            embedding_provider = get_embedding_provider()
        except Exception:
            pass
        conflict_service = SemanticConflictDiscovery(embedding_provider=embedding_provider)

        t_stage2 = time.perf_counter()
        stage2_results = await asyncio.gather(
            consistency_service.find_inconsistencies(entities=entities, document_id=document_id, facts=facts),
            conflict_service.discover_conflicts(facts=facts, document_id=document_id),
            return_exceptions=True
        )
        logger.info(
            f"[Analysis] Stage 2 consistency & conflict discovery complete for doc={document_id} in "
            f"{(time.perf_counter()-t_stage2)*1000:.1f}ms"
        )

        entity_inconsistencies = stage2_results[0] if not isinstance(stage2_results[0], BaseException) else []
        llm_conflicts = stage2_results[1] if not isinstance(stage2_results[1], BaseException) else []

        # Merge conflicts: deterministic first (authoritative), then LLM — dedup
        seen_summaries: set = set()
        semantic_conflicts: list = []
        for c in deterministic_conflicts + llm_conflicts:
            key = (c.get("summary") or c.get("explanation") or "").lower().strip()[:120]
            if key and key not in seen_summaries:
                seen_summaries.add(key)
                semantic_conflicts.append(c)

        # ── Stage 3: Trust Score V2 ───────────────────────────────────────────
        from services.trust_score import TrustScoreV2Service
        trust_service = TrustScoreV2Service()
        t_stage3 = time.perf_counter()
        trust_score = await trust_service.compute_trust_score(
            document_id=document_id,
            chunks=chunks_text,
            metadatas=chunks_meta,
            semantic_conflicts=semantic_conflicts,
            references=references,
            requirements=requirements,
            entity_conflicts=entity_inconsistencies,
            ambiguities=ambiguities
        )
        logger.info(
            f"[Analysis] TrustScoreV2 complete for doc={document_id} in "
            f"{(time.perf_counter()-t_stage3)*1000:.1f}ms | score={trust_score.get('score', 100)}"
        )

        # ── Stage 4: Parallel Executive Summary & Review Copilot ───────────────
        from services.executive_summary import ExecutiveSummaryService
        from services.copilot import ReviewCopilotService
        summary_service = ExecutiveSummaryService()
        copilot_service = ReviewCopilotService()

        t_stage4 = time.perf_counter()
        stage4_results = await asyncio.gather(
            summary_service.generate_summary(
                document_id=document_id,
                doc_name=doc_name,
                facts=facts,
                semantic_conflicts=semantic_conflicts,
                references=references,
                requirements=requirements,
                entity_conflicts=entity_inconsistencies,
                ambiguities=ambiguities,
                trust_score=trust_score
            ),
            copilot_service.generate_review(
                document_id=document_id,
                doc_name=doc_name,
                facts=facts,
                semantic_conflicts=semantic_conflicts,
                references=references,
                requirements=requirements,
                entity_conflicts=entity_inconsistencies,
                ambiguities=ambiguities
            ),
            return_exceptions=True
        )
        logger.info(
            f"[Analysis] Stage 4 summary & review complete for doc={document_id} in "
            f"{(time.perf_counter()-t_stage4)*1000:.1f}ms"
        )

        executive_summary = stage4_results[0] if not isinstance(stage4_results[0], BaseException) else {
            "executive_summary": "Summary completed.", "key_findings": [], "critical_risks": [],
            "major_contradictions": [], "important_entities": [], "requirements_overview": "",
            "trust_assessment": "", "recommended_actions": []
        }
        review = stage4_results[1] if not isinstance(stage4_results[1], BaseException) else {
            "reviewer_checklist": [], "open_questions": [], "compliance_concerns": [],
            "risk_items": [], "verification_tasks": []
        }

        # ── Persist ───────────────────────────────────────────────────────────
        new_analysis = DocumentAnalysisModel(
            id=f"an-{uuid.uuid4()}",
            document_id=document_id,
            summary_json=summary_data,
            entities_json=entities,
            kv_pairs_json=kv_pairs,
            entity_conflicts_json=entity_inconsistencies,
            facts_json=facts,
            semantic_conflicts_json=semantic_conflicts,
            ambiguities_json=ambiguities,
            references_json=references,
            requirements_json=requirements,
            trust_score_json=trust_score,
            executive_summary_json=executive_summary,
            review_json=review,
            analyzed_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )

        try:
            saved_analysis = await self.repo.create(new_analysis)
            await self._write_to_redis_cache(saved_analysis)
            return saved_analysis
        except Exception as e:
            logger.error(f"[Analysis] DB save failed for doc={document_id}, trying to fetch existing: {e}")
            existing = await self.repo.get_by_document_id(document_id)
            if existing:
                await self._write_to_redis_cache(existing)
                return existing
            raise e

    async def _write_to_redis_cache(self, analysis: DocumentAnalysisModel) -> None:
        """Helper to write database analysis model data to Redis cache."""
        try:
            from services.cache import cache_service
            await cache_service.set(
                "analysis",
                "document",
                analysis.document_id,
                {
                    "id": analysis.id,
                    "document_id": analysis.document_id,
                    "summary_json": analysis.summary_json,
                    "entities_json": analysis.entities_json,
                    "kv_pairs_json": analysis.kv_pairs_json,
                    "entity_conflicts_json": analysis.entity_conflicts_json,
                    "facts_json": analysis.facts_json,
                    "semantic_conflicts_json": analysis.semantic_conflicts_json,
                    "ambiguities_json": analysis.ambiguities_json,
                    "references_json": analysis.references_json,
                    "requirements_json": analysis.requirements_json,
                    "trust_score_json": analysis.trust_score_json,
                    "executive_summary_json": analysis.executive_summary_json,
                    "review_json": analysis.review_json,
                    "analyzed_at": (analysis.analyzed_at.isoformat() if hasattr(analysis.analyzed_at, "isoformat") else str(analysis.analyzed_at)) if getattr(analysis, "analyzed_at", None) else datetime.now(timezone.utc).isoformat()
                },
                ttl_seconds=3600
            )
        except Exception as exc:
            logger.warning(f"[Analysis] Cache set failed for doc={analysis.document_id}: {exc}")

    async def _fetch_document_chunks(
        self, document_id: str
    ) -> tuple[list[str], list[dict]]:
        """Retrieve all document text chunks and metadata from ChromaDB."""
        try:
            from services.dependencies import get_vector_store
            store = get_vector_store()
            client = getattr(store, "_client", None)
            if not client:
                return [], []

            collection = await asyncio.to_thread(
                client.get_or_create_collection,
                "documind_chunks",
                metadata={"hnsw:space": "cosine"},
            )
            res = await asyncio.to_thread(
                collection.get,
                where={"document_id": document_id},
                include=["documents", "metadatas"],
            )
            documents = res.get("documents") or []
            metadatas = res.get("metadatas") or []

            # Sort by chunk_index
            pairs = list(zip(documents, metadatas))
            pairs.sort(key=lambda p: p[1].get("chunk_index", 0))
            texts = [p[0] for p in pairs]
            metas = [p[1] for p in pairs]
            return texts, metas

        except Exception as e:
            logger.error(f"[Analysis] Failed to fetch chunks for doc={document_id}: {e}")
            return [], []

    async def _create_empty_analysis(self, document_id: str) -> DocumentAnalysisModel:
        """Create a placeholder analysis for unprocessed documents."""
        new_analysis = DocumentAnalysisModel(
            id=f"an-{uuid.uuid4()}",
            document_id=document_id,
            summary_json={
                "abstract": "Document is still being processed. Please retry after ingestion completes.",
                "keyPoints": [],
                "suggestedQuestions": [],
            },
            entities_json=[],
            kv_pairs_json=[],
            entity_conflicts_json=[],
            facts_json=[],
            semantic_conflicts_json=[],
            ambiguities_json=[],
            references_json=[],
            requirements_json=[],
            trust_score_json={"score": 100.0, "confidence": 1.0, "breakdown": {}, "deductions": [], "evidence": ""},
            executive_summary_json={"executive_summary": "Document is processing.", "key_findings": [], "critical_risks": [], "major_contradictions": [], "important_entities": [], "requirements_overview": "", "trust_assessment": "", "recommended_actions": []},
            review_json={"reviewer_checklist": [], "open_questions": [], "compliance_concerns": [], "risk_items": [], "verification_tasks": []},
            analyzed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        return await self.repo.create(new_analysis)
