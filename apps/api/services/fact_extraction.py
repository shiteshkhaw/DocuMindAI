"""
FactExtractionService
=====================
Extracts discrete, verifiable facts (subject-predicate-object triples) from
document chunks using an LLM.  Every fact is grounded by a verbatim evidence
span so it is fully traceable back to the source text.

Design principles:
- No hallucination: every fact must be evidenced by actual chunk content.
- Idempotent: results are stored in `facts_json`; call site must NOT re-run
  unless the document has changed.
- No paid infra additions: uses existing LLM registry and OpenAI provider.
"""

import uuid
import json
import logging
import asyncio
import re
from typing import List, Dict, Any

from llm.registry import llm_registry
from llm.base import LLMMessage

logger = logging.getLogger("documind.services.fact_extraction")

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a precision document analyst. Your task is to extract every discrete,
verifiable fact from the supplied document segments.

A "fact" is a concrete, falsifiable claim such as:
  - A numerical measurement:     "System latency is 200 ms"
  - A temporal statement:        "Project deadline is Q3 2025"
  - A definitional statement:    "The system uses AES-256 encryption"
  - A relational statement:      "Alice is the owner of Module B"
  - A requirement:               "Users must authenticate via SSO"

For each fact return:
  - subject:      The entity, system, or concept the fact is about
  - predicate:    The relationship, property, or action
  - object_value: The value, target, or object
  - confidence:   0.0–1.0 (how certain you are this is a genuine fact)
  - fact_type:    One of: numerical | temporal | definitional | relational | requirement
  - page:         The page number where the fact appears (use the [Segment N] marker to infer)
  - evidence_text: The EXACT verbatim quote from the segment that contains the fact

Return ONLY valid JSON with this exact structure:
{
  "facts": [
    {
      "subject": "...",
      "predicate": "...",
      "object_value": "...",
      "confidence": 0.95,
      "fact_type": "numerical",
      "page": 3,
      "evidence_text": "exact verbatim quote from document"
    }
  ]
}

Rules:
- Include only facts with confidence >= 0.6.
- Do NOT invent facts not present in the text.
- Do NOT return markdown, code fences, or HTML.
- Return only the JSON object.
"""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class FactExtractionService:
    """
    Extracts structured facts from document chunks via LLM.
    Each fact is a (subject, predicate, object_value) triple with evidence.
    """

    # Feed at most this many characters to the LLM per call to stay within
    # context windows (GPT-4o: 128 k, GPT-4-turbo: 128 k).
    _MAX_CHARS_PER_BATCH = 12_000
    _MAX_CHUNKS_PER_BATCH = 25
    _MAX_RETRIES = 3

    async def extract_facts(
        self,
        chunks: List[str],
        document_id: str,
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract facts from document chunks.

        Args:
            chunks:      List of text segments (ordered by chunk_index).
            document_id: Used only for logging.
            metadatas:   Optional list of chunk metadata dicts (same order as
                         chunks) used to resolve real page numbers.

        Returns:
            List of fact dicts matching the FactSchema Pydantic model.
        """
        if not chunks:
            logger.warning(f"[FactExtraction] No chunks provided for doc={document_id}")
            return []

        metadatas = metadatas or [{} for _ in chunks]

        # Build page-aware text segments
        segments = self._build_segments(chunks, metadatas)

        # Batch into groups that fit the context window
        batches = self._batch_segments(segments)

        logger.info(
            f"[FactExtraction] doc={document_id} | "
            f"chunks={len(chunks)} → {len(batches)} LLM batch(es)"
        )

        all_facts: List[Dict[str, Any]] = []
        for batch_idx, batch in enumerate(batches):
            try:
                facts = await self._extract_batch(batch, document_id, batch_idx)
                all_facts.extend(facts)
            except Exception as e:
                logger.error(
                    f"[FactExtraction] Batch {batch_idx} failed for doc={document_id}: {e}",
                    exc_info=True,
                )

        # Deduplicate (same subject+predicate+object) and assign stable IDs
        deduped = self._deduplicate(all_facts)

        logger.info(
            f"[FactExtraction] doc={document_id} | "
            f"raw={len(all_facts)} facts → {len(deduped)} after dedup"
        )
        return deduped

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_segments(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Pair each chunk with its page number and chunk index."""
        segments = []
        for i, (text, meta) in enumerate(zip(chunks, metadatas)):
            page = meta.get("page_number", 1)
            chunk_idx = meta.get("chunk_index", i)
            segments.append({"text": text, "page": page, "chunk_index": chunk_idx})
        return segments

    def _batch_segments(
        self,
        segments: List[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        """Group segments into batches that fit the token budget."""
        batches: List[List[Dict[str, Any]]] = []
        current_batch: List[Dict[str, Any]] = []
        current_chars = 0

        for seg in segments:
            seg_chars = len(seg["text"])
            if (
                current_batch
                and (
                    current_chars + seg_chars > self._MAX_CHARS_PER_BATCH
                    or len(current_batch) >= self._MAX_CHUNKS_PER_BATCH
                )
            ):
                batches.append(current_batch)
                current_batch = []
                current_chars = 0
            current_batch.append(seg)
            current_chars += seg_chars

        if current_batch:
            batches.append(current_batch)
        return batches

    async def _extract_batch(
        self,
        batch: List[Dict[str, Any]],
        document_id: str,
        batch_idx: int,
    ) -> List[Dict[str, Any]]:
        """Run one LLM call for a single batch of segments."""
        # Assemble prompt body
        lines = []
        for seg in batch:
            lines.append(
                f"[Segment - Page {seg['page']} / Chunk {seg['chunk_index']}]\n{seg['text']}"
            )
        prompt_body = "\n\n---\n\n".join(lines)

        messages = [
            LLMMessage(role="system", content=_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=f"Extract all verifiable facts from the following document segments:\n\n{prompt_body}",
            ),
        ]

        provider_name, model = llm_registry.resolve_model_route("documind-v3")
        provider = llm_registry.get_provider(provider_name)

        full_content = ""
        retry_delay = 1.0
        for attempt in range(self._MAX_RETRIES):
            try:
                full_content = ""
                async for chunk in provider.generate_stream(
                    messages=messages,
                    model=model,
                    temperature=0.0,
                    max_tokens=3000,
                ):
                    if chunk.token:
                        full_content += chunk.token
                break
            except Exception as e:
                if attempt < self._MAX_RETRIES - 1:
                    logger.warning(
                        f"[FactExtraction] Batch {batch_idx} LLM attempt {attempt+1} failed: {e}. Retrying…"
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    raise

        raw_facts = self._parse_response(full_content, batch_idx)

        # Enrich each fact with chunk_index from source batch
        enriched: List[Dict[str, Any]] = []
        for fact in raw_facts:
            page = int(fact.get("page", 1))
            # Find the segment whose page matches (fallback to first)
            source_seg = next(
                (s for s in batch if s["page"] == page),
                batch[0],
            )
            enriched.append(
                {
                    "id": f"fact-{uuid.uuid4()}",
                    "subject": str(fact.get("subject", "")).strip(),
                    "predicate": str(fact.get("predicate", "")).strip(),
                    "object_value": str(fact.get("object_value", "")).strip(),
                    "confidence": float(fact.get("confidence", 0.7)),
                    "fact_type": str(fact.get("fact_type", "definitional")),
                    "page": page,
                    "evidence": [
                        {
                            "text": str(fact.get("evidence_text", ""))[:500],
                            "page": page,
                            "chunk_index": source_seg["chunk_index"],
                        }
                    ],
                }
            )
        return enriched

    def _parse_response(
        self,
        content: str,
        batch_idx: int,
    ) -> List[Dict[str, Any]]:
        """Parse JSON from LLM response with repair fallback."""
        try:
            clean = content.strip()
            # Strip markdown code fences if present
            if clean.startswith("```"):
                first = clean.find("{")
                last = clean.rfind("}")
                if first != -1 and last != -1:
                    clean = clean[first : last + 1]

            match = re.search(r"(\{.*\})", clean, re.DOTALL)
            json_str = match.group(0) if match else clean
            data = json.loads(json_str)
            facts = data.get("facts", [])
            if not isinstance(facts, list):
                return []
            return [f for f in facts if isinstance(f, dict)]
        except Exception as e:
            logger.warning(
                f"[FactExtraction] Batch {batch_idx} JSON parse failed: {e}. "
                f"Preview: {content[:200]}"
            )
            return []

    def _deduplicate(
        self,
        facts: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Remove near-duplicate facts (same subject+predicate+object_value,
        case-insensitive). Keep the highest-confidence copy.
        """
        seen: Dict[tuple, Dict[str, Any]] = {}
        for fact in facts:
            # Skip empty
            if not fact.get("subject") or not fact.get("predicate") or not fact.get("object_value"):
                continue
            key = (
                fact["subject"].lower().strip(),
                fact["predicate"].lower().strip(),
                fact["object_value"].lower().strip(),
            )
            if key not in seen:
                seen[key] = fact
            else:
                # Keep the higher-confidence one; merge evidence spans
                existing = seen[key]
                if fact["confidence"] > existing["confidence"]:
                    fact["evidence"] = existing["evidence"] + fact["evidence"]
                    seen[key] = fact
                else:
                    existing["evidence"] = existing["evidence"] + fact["evidence"]

        return list(seen.values())
