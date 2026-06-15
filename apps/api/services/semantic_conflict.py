"""
SemanticConflictDiscovery
=========================
Detects semantic-level contradictions between document chunks using embedding
cosine-distance analysis combined with LLM verification.

Architecture:
  1. Build an embedding matrix from the extracted facts produced by
     FactExtractionService.
  2. Compute pairwise cosine similarity across all fact pairs.
  3. Flag pairs whose semantic distance is HIGH (meaning the statements are
     about the same topic but say opposite things — a contradiction zone),
     NOT pairs that are merely different topics.
  4. Deduplicate and send candidate conflict pairs to the LLM for structured
     explanation.
  5. Return SemanticConflictSchema-conformant dicts.

Key insight on contradiction semantics:
  - A contradiction occurs in the *intermediate similarity band*: both
    statements share enough topic overlap to be about the same thing, but
    differ enough in claims to conflict.
  - Pairs with similarity > 0.95 are likely duplicates (not conflicts).
  - Pairs with similarity < 0.20 are on different topics (not conflicts).
  - Target band: 0.20 ≤ similarity ≤ 0.85 for candidate pairs.
  - LLM confirms/rejects each candidate.

Design constraints:
  - No paid infra. Uses existing embedding provider and LLM registry.
  - Scales to documents with 200+ chunks via batched O(n²) capping.
"""

import uuid
import json
import logging
import asyncio
import re
from typing import List, Dict, Any, Tuple

import numpy as np

from llm.registry import llm_registry
from llm.base import LLMMessage

logger = logging.getLogger("documind.services.semantic_conflict")


def _obj(fact: dict) -> str:
    """Return the object/value field, supporting both 'object_value' and 'value' keys."""
    return fact.get("object_value") or fact.get("value", "")


def _evidence_text(fact: dict, max_chars: int = 120) -> str:
    """Get evidence text, handling both string (facts.py) and list-of-dicts formats."""
    ev = fact.get("evidence", "")
    if isinstance(ev, str):
        return ev[:max_chars]
    if isinstance(ev, list) and ev:
        first = ev[0]
        if isinstance(first, dict):
            return first.get("text", "")[:max_chars]
        return str(first)[:max_chars]
    return ""


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a senior document auditor specialising in semantic consistency analysis.

You will be given two statements extracted from the same document. They have
been flagged by an embedding-distance algorithm as potentially contradictory.

Your task:
1. Determine whether the two statements GENUINELY contradict each other.
2. If yes, classify the contradiction type and provide a structured explanation.
3. If no, say so clearly.

Return ONLY valid JSON (no markdown, no HTML):
{
  "is_contradiction": true | false,
  "conflict_type": "numerical | temporal | definitional | relational | logical",
  "explanation": "One paragraph explanation of the contradiction and its significance.",
  "confidence": 0.0–1.0
}

If the statements do NOT contradict, return: {"is_contradiction": false, "confidence": 0.9}
"""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class SemanticConflictDiscovery:
    """
    Discovers semantic-level contradictions between document facts using
    embedding proximity analysis + LLM verification.
    """

    # Similarity band for candidate contradiction pairs
    _SIM_LOW = 0.20   # Below this → different topics, skip
    _SIM_HIGH = 0.85  # Above this → likely duplicates, skip

    # Maximum candidate pairs to send to LLM (cost & latency guard)
    _MAX_CANDIDATES = 40

    # Composite conflict score weights
    _W_CONFIDENCE = 0.50
    _W_DISTANCE = 0.30    # semantic distance = 1 - similarity
    _W_LLM_STRENGTH = 0.20

    _MAX_RETRIES = 3

    def __init__(self, embedding_provider=None):
        """
        Args:
            embedding_provider: An instance of BaseEmbeddingProvider.
                                If None, embeddings are skipped and a fallback
                                heuristic is used (pure LLM).
        """
        self.embedding_provider = embedding_provider

    async def discover_conflicts(
        self,
        facts: List[Dict[str, Any]],
        document_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Discover semantic conflicts between facts in the document.

        Args:
            facts:       List of fact dicts (as produced by FactExtractionService).
            document_id: Used for logging only.

        Returns:
            List of SemanticConflictSchema-conformant dicts.
        """
        if len(facts) < 2:
            logger.info(f"[SemanticConflict] doc={document_id}: fewer than 2 facts, skipping.")
            return []

        logger.info(
            f"[SemanticConflict] doc={document_id}: analysing {len(facts)} facts "
            f"for pairwise contradictions."
        )

        # Step 1: Build candidate pairs
        if self.embedding_provider is not None:
            candidates = await self._embedding_candidates(facts, document_id)
        else:
            candidates = self._heuristic_candidates(facts)

        if not candidates:
            logger.info(f"[SemanticConflict] doc={document_id}: no candidate pairs found.")
            return []

        logger.info(
            f"[SemanticConflict] doc={document_id}: {len(candidates)} candidate pairs → LLM verification."
        )

        # Step 2: Verify candidates via LLM
        conflicts: List[Dict[str, Any]] = []
        verification_tasks = [
            self._verify_pair(fa, fb, sim, document_id)
            for fa, fb, sim in candidates
        ]
        results = await asyncio.gather(*verification_tasks, return_exceptions=True)

        for (fa, fb, sim), result in zip(candidates, results):
            if isinstance(result, BaseException):
                logger.warning(
                    f"[SemanticConflict] LLM verification failed for pair: {result}"
                )
                continue
            if result is not None:
                conflicts.append(result)

        logger.info(
            f"[SemanticConflict] doc={document_id}: "
            f"{len(conflicts)} confirmed conflicts from {len(candidates)} candidates."
        )
        return conflicts

    # ------------------------------------------------------------------
    # Candidate selection
    # ------------------------------------------------------------------

    async def _embedding_candidates(
        self,
        facts: List[Dict[str, Any]],
        document_id: str,
    ) -> List[Tuple[Dict, Dict, float]]:
        """Use cosine distance on fact embeddings to find candidate pairs."""
        # Build fact statements
        statements = [
            f"{f['subject']} {f['predicate']} {_obj(f)}"
            for f in facts
        ]

        provider = self.embedding_provider
        if provider is None:
            return self._heuristic_candidates(facts)

        try:
            embeddings = await provider.embed_documents(statements)
        except Exception as e:
            logger.warning(
                f"[SemanticConflict] Embedding failed for doc={document_id}: {e}. "
                "Falling back to heuristic candidates."
            )
            return self._heuristic_candidates(facts)

        emb_array = np.array(embeddings, dtype=np.float32)
        norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = emb_array / norms
        sim_matrix = np.dot(normalized, normalized.T)

        candidates: List[Tuple[Dict, Dict, float]] = []
        n = len(facts)
        for i in range(n):
            for j in range(i + 1, n):
                sim = float(sim_matrix[i][j])
                if self._SIM_LOW <= sim <= self._SIM_HIGH:
                    # Only flag pairs of the SAME fact_type as higher priority
                    candidates.append((facts[i], facts[j], sim))

        # Sort by "most likely to conflict" = intermediate similarity
        # Closer to 0.55 = maximally ambiguous
        candidates.sort(key=lambda t: abs(t[2] - 0.55))
        return candidates[: self._MAX_CANDIDATES]

    def _heuristic_candidates(
        self,
        facts: List[Dict[str, Any]],
    ) -> List[Tuple[Dict, Dict, float]]:
        """
        Heuristic fallback: find pairs with the same subject but different
        object values.  Uses exact string matching.
        """
        from itertools import combinations

        candidates: List[Tuple[Dict, Dict, float]] = []
        for fa, fb in combinations(facts, 2):
            if fa["subject"].lower().strip() == fb["subject"].lower().strip():
                if _obj(fa).lower().strip() != _obj(fb).lower().strip():
                    candidates.append((fa, fb, 0.55))  # placeholder similarity
        return candidates[: self._MAX_CANDIDATES]

    # ------------------------------------------------------------------
    # LLM verification
    # ------------------------------------------------------------------

    async def _verify_pair(
        self,
        fa: Dict[str, Any],
        fb: Dict[str, Any],
        similarity: float,
        document_id: str,
    ) -> Dict[str, Any] | None:
        """
        Send a fact pair to the LLM for contradiction verification.
        Returns a SemanticConflictSchema dict if confirmed, else None.
        """
        stmt_a = (
            f"[Page {fa.get('page', '?')}] "
            f"{fa['subject']} {fa['predicate']} {_obj(fa)}"
        )
        stmt_b = (
            f"[Page {fb.get('page', '?')}] "
            f"{fb['subject']} {fb['predicate']} {_obj(fb)}"
        )
        evidence_a = _evidence_text(fa)
        evidence_b = _evidence_text(fb)

        user_msg = (
            f"Statement A: {stmt_a}\n"
            f"Evidence A:  {evidence_a}\n\n"
            f"Statement B: {stmt_b}\n"
            f"Evidence B:  {evidence_b}\n\n"
            "Do these statements contradict each other?"
        )

        messages = [
            LLMMessage(role="system", content=_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_msg),
        ]

        provider_name, model = llm_registry.resolve_model_route("documind-v3")
        provider = llm_registry.get_provider(provider_name)

        full_content = ""
        retry_delay = 1.0
        for attempt in range(self._MAX_RETRIES):
            try:
                full_content = ""
                async for ch in provider.generate_stream(
                    messages=messages,
                    model=model,
                    temperature=0.0,
                    max_tokens=400,
                ):
                    if ch.token:
                        full_content += ch.token
                break
            except Exception as e:
                if attempt < self._MAX_RETRIES - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    raise

        return self._build_conflict(fa, fb, similarity, full_content)

    # ------------------------------------------------------------------
    # Response parsing & conflict construction
    # ------------------------------------------------------------------

    def _build_conflict(
        self,
        fa: Dict[str, Any],
        fb: Dict[str, Any],
        similarity: float,
        llm_response: str,
    ) -> Dict[str, Any] | None:
        """Parse LLM response and build a SemanticConflictSchema dict."""
        try:
            clean = llm_response.strip()
            if clean.startswith("```"):
                first = clean.find("{")
                last = clean.rfind("}")
                if first != -1 and last != -1:
                    clean = clean[first : last + 1]
            match = re.search(r"(\{.*\})", clean, re.DOTALL)
            json_str = match.group(0) if match else clean
            data = json.loads(json_str)
        except Exception as e:
            logger.warning(
                f"[SemanticConflict] JSON parse failed: {e}. "
                f"Preview: {llm_response[:150]}"
            )
            return None

        if not data.get("is_contradiction", False):
            return None

        confidence = float(data.get("confidence", 0.75))
        semantic_distance = 1.0 - similarity
        conflict_score = (
            self._W_CONFIDENCE * confidence
            + self._W_DISTANCE * semantic_distance
            + self._W_LLM_STRENGTH * confidence
        )

        # Severity classification
        if conflict_score >= 0.80:
            severity = "critical"
        elif conflict_score >= 0.60:
            severity = "high"
        elif conflict_score >= 0.40:
            severity = "medium"
        else:
            severity = "low"

        return {
            "id": f"sconf-{uuid.uuid4()}",
            "statement_a": (
                f"{fa['subject']} {fa['predicate']} {_obj(fa)}"
            ),
            "statement_b": (
                f"{fb['subject']} {fb['predicate']} {_obj(fb)}"
            ),
            "page_a": int(fa.get("page", 0)),
            "page_b": int(fb.get("page", 0)),
            "semantic_distance": round(semantic_distance, 4),
            "conflict_score": round(conflict_score, 4),
            "severity": severity,
            "conflict_type": str(data.get("conflict_type", "logical")),
            "explanation": str(data.get("explanation", "")),
            "confidence": confidence,
        }
