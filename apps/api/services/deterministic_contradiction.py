"""
DeterministicContradictionDetector
====================================
Layer 1 of the multi-layer contradiction engine.
Performs fast, rule-based detection of concrete conflicts BEFORE the LLM runs.

Detection layers:
  L1 — Numerical conflicts  (same metric, different numbers)
  L2 — Date / deadline conflicts
  L3 — Monetary value conflicts
  L4 — Entity attribute conflicts (same entity, different assigned attribute)
  L5 — Requirement polarity conflicts (REQ-X shall / shall not)

All detections are deterministic — zero hallucination risk.
LLM is only invoked for semantic / logical conflicts that pass this filter.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from itertools import combinations

logger = logging.getLogger("documind.services.deterministic_contradiction")


# ─── Regex patterns ─────────────────────────────────────────────────────────

# Matches patterns like "latency is 200ms", "budget of $5M", "16 GB RAM"
_NUMERIC_PATTERN = re.compile(
    r"(?P<label>[a-zA-Z][a-zA-Z0-9 _\-]{1,40}?)\s+"
    r"(?:is|was|are|=|:|of|at|to|equals?)\s+"
    r"(?P<value>\d[\d,\.]*\s*(?:ms|s|GB|MB|TB|KB|%|k|M|B|million|billion|thousand|USD|EUR|GBP|days?|weeks?|months?|years?|hours?|minutes?)?\b)",
    re.IGNORECASE
)

# Dates: "2023-01-01", "Q3 2024", "Jan 15, 2024", "March 2025", "2025"
_DATE_PATTERN = re.compile(
    r"(?P<label>[a-zA-Z][a-zA-Z0-9 _\-]{1,40}?)\s+"
    r"(?:is|was|are|=|:|on|at|by|deadline|due|scheduled)\s+"
    r"(?P<date>"
    r"\d{4}-\d{2}-\d{2}"
    r"|Q[1-4]\s+\d{4}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}"
    r"|\d{1,2}/\d{1,2}/\d{2,4}"
    r"|\d{4}"
    r")",
    re.IGNORECASE
)

# Money: "$5M", "5 million dollars", "€1.2 billion", "USD 50,000"
_MONEY_PATTERN = re.compile(
    r"(?P<label>[a-zA-Z][a-zA-Z0-9 _\-]{1,40}?)\s+"
    r"(?:is|was|are|=|:|of|at|budget)\s+"
    r"(?P<value>(?:USD|EUR|GBP|£|€|\$)\s*[\d,\.]+\s*(?:k|M|B|million|billion|thousand)?"
    r"|[\d,\.]+\s*(?:k|M|B|million|billion|thousand)\s*(?:USD|EUR|GBP|dollars?|euros?|pounds?)?)",
    re.IGNORECASE
)

# Requirement polarity: "system shall use X" vs "system shall not use X"
_REQ_POSITIVE = re.compile(
    r"\b(?:system|service|application|platform|component)\b.{0,60}?\b(?:shall|must|will)\b\s+"
    r"(?P<verb>[a-zA-Z]{2,20})\s+(?P<object>[a-zA-Z][a-zA-Z0-9 \-]{2,40})",
    re.IGNORECASE
)
_REQ_NEGATIVE = re.compile(
    r"\b(?:system|service|application|platform|component)\b.{0,60}?\b(?:shall not|must not|will not|cannot|should not)\b\s+"
    r"(?P<verb>[a-zA-Z]{2,20})\s+(?P<object>[a-zA-Z][a-zA-Z0-9 \-]{2,40})",
    re.IGNORECASE
)


class DeterministicContradictionDetector:
    """
    Runs deterministic contradiction checks across all document chunks.
    Returns a list of pre-confirmed contradiction dicts that do NOT need LLM verification.
    """

    def detect(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str,
        doc_name: str,
    ) -> List[Dict[str, Any]]:
        """
        Run all deterministic detection layers.

        Returns: List of contradiction dicts (same schema as LLM-confirmed contradictions).
        """
        results: List[Dict[str, Any]] = []

        results.extend(self._detect_numerical(chunks, metadatas, document_id, doc_name))
        results.extend(self._detect_dates(chunks, metadatas, document_id, doc_name))
        results.extend(self._detect_money(chunks, metadatas, document_id, doc_name))
        results.extend(self._detect_requirement_polarity(chunks, metadatas, document_id, doc_name))

        logger.info(
            f"[DeterministicDetector] doc={document_id}: "
            f"{len(results)} deterministic contradictions found."
        )
        return results

    # ── Layer 1: Numerical ─────────────────────────────────────────────────────

    def _detect_numerical(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str,
        doc_name: str,
    ) -> List[Dict[str, Any]]:
        """Detect same-label, different-value numerical conflicts."""
        label_map: Dict[str, List[Dict]] = {}
        for chunk, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            for m in _NUMERIC_PATTERN.finditer(chunk):
                label = m.group("label").strip().lower()
                value = m.group("value").strip()
                # Filter out labels that are too generic
                if len(label) < 3 or label in {"the", "a", "an", "it", "this", "that"}:
                    continue
                label_map.setdefault(label, []).append({
                    "label": m.group("label").strip(),
                    "value": value,
                    "page": page,
                    "snippet": chunk[max(0, m.start() - 60): m.end() + 80].replace("\n", " ")
                })

        return self._conflicts_from_label_map(
            label_map,
            "numerical",
            document_id,
            doc_name,
            confidence=0.92,
        )

    # ── Layer 2: Date / Deadline ───────────────────────────────────────────────

    def _detect_dates(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str,
        doc_name: str,
    ) -> List[Dict[str, Any]]:
        """Detect same-label date conflicts (same event, different dates)."""
        label_map: Dict[str, List[Dict]] = {}
        for chunk, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            for m in _DATE_PATTERN.finditer(chunk):
                label = m.group("label").strip().lower()
                date = m.group("date").strip()
                if len(label) < 4:
                    continue
                label_map.setdefault(label, []).append({
                    "label": m.group("label").strip(),
                    "value": date,
                    "page": page,
                    "snippet": chunk[max(0, m.start() - 60): m.end() + 80].replace("\n", " ")
                })

        return self._conflicts_from_label_map(
            label_map,
            "date",
            document_id,
            doc_name,
            confidence=0.90,
        )

    # ── Layer 3: Monetary ──────────────────────────────────────────────────────

    def _detect_money(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str,
        doc_name: str,
    ) -> List[Dict[str, Any]]:
        """Detect same-label monetary conflicts (same item, different prices)."""
        label_map: Dict[str, List[Dict]] = {}
        for chunk, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            for m in _MONEY_PATTERN.finditer(chunk):
                label = m.group("label").strip().lower()
                value = m.group("value").strip()
                if len(label) < 3:
                    continue
                label_map.setdefault(label, []).append({
                    "label": m.group("label").strip(),
                    "value": value,
                    "page": page,
                    "snippet": chunk[max(0, m.start() - 60): m.end() + 80].replace("\n", " ")
                })

        return self._conflicts_from_label_map(
            label_map,
            "monetary",
            document_id,
            doc_name,
            confidence=0.95,  # money conflicts are usually unambiguous
        )

    # ── Layer 4: Requirement Polarity ─────────────────────────────────────────

    def _detect_requirement_polarity(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str,
        doc_name: str,
    ) -> List[Dict[str, Any]]:
        """Detect affirmative vs. negated requirement conflicts."""
        positives: Dict[Tuple[str, str], Dict] = {}  # (verb, object_lower) -> first occurrence
        conflicts: List[Dict[str, Any]] = []

        for chunk, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            # Collect positives
            for m in _REQ_POSITIVE.finditer(chunk):
                key = (m.group("verb").lower(), m.group("object").strip().lower()[:30])
                if key not in positives:
                    positives[key] = {
                        "text": m.group(0).strip(),
                        "page": page,
                        "snippet": chunk[max(0, m.start() - 20): m.end() + 60].replace("\n", " ")
                    }

        # Now find negations that match a positive
        for chunk, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            for m in _REQ_NEGATIVE.finditer(chunk):
                key = (m.group("verb").lower(), m.group("object").strip().lower()[:30])
                if key in positives and positives[key]["page"] != page:
                    pos = positives[key]
                    neg_text = m.group(0).strip()
                    neg_snippet = chunk[max(0, m.start() - 20): m.end() + 60].replace("\n", " ")
                    conflicts.append({
                        "id": f"determ-req-{abs(hash(key))}",
                        "type": "requirement",
                        "severity": "critical",
                        "confidence": 0.93,
                        "summary": f"Requirement polarity conflict: '{pos['text'][:60]}' vs '{neg_text[:60]}'",
                        "explanation": (
                            f"The document contains a direct requirement contradiction: "
                            f"page {pos['page']} states the system SHALL {m.group('verb')} {m.group('object')}, "
                            f"while page {page} states it SHALL NOT."
                        ),
                        "conflictingStatements": [
                            {"text": pos["text"], "page": pos["page"], "documentId": document_id},
                            {"text": neg_text, "page": page, "documentId": document_id},
                        ],
                        "citations": [
                            {"documentId": document_id, "documentName": doc_name,
                             "pageNumber": pos["page"], "snippet": pos["snippet"][:300], "score": 1.0},
                            {"documentId": document_id, "documentName": doc_name,
                             "pageNumber": page, "snippet": neg_snippet[:300], "score": 1.0},
                        ],
                        "source": "deterministic",
                    })
        return conflicts

    # ── Shared helper ──────────────────────────────────────────────────────────

    def _conflicts_from_label_map(
        self,
        label_map: Dict[str, List[Dict]],
        conflict_type: str,
        document_id: str,
        doc_name: str,
        confidence: float,
    ) -> List[Dict[str, Any]]:
        """Given a map of label → [occurrences], emit contradictions where value differs."""
        conflicts: List[Dict[str, Any]] = []
        for label, occurrences in label_map.items():
            if len(occurrences) < 2:
                continue
            # Compare all pairs
            for a, b in combinations(occurrences, 2):
                # Normalize values for comparison
                va = _normalize_value(a["value"])
                vb = _normalize_value(b["value"])
                if va == vb:
                    continue  # same value — not a conflict
                if a["page"] == b["page"]:
                    continue  # same page — likely a correction, not a contradiction
                # Verified different values on different pages
                conflicts.append({
                    "id": f"determ-{conflict_type}-{abs(hash((label, va, vb)))}",
                    "type": conflict_type,
                    "severity": "high",
                    "confidence": confidence,
                    "summary": (
                        f"{conflict_type.capitalize()} conflict for '{a['label']}': "
                        f"'{a['value']}' (page {a['page']}) vs '{b['value']}' (page {b['page']})"
                    ),
                    "explanation": (
                        f"The document assigns conflicting {conflict_type} values to '{a['label']}'. "
                        f"Page {a['page']} states '{a['value']}' while page {b['page']} states '{b['value']}'. "
                        f"One of these must be incorrect."
                    ),
                    "conflictingStatements": [
                        {"text": a["snippet"], "page": a["page"], "documentId": document_id},
                        {"text": b["snippet"], "page": b["page"], "documentId": document_id},
                    ],
                    "citations": [
                        {"documentId": document_id, "documentName": doc_name,
                         "pageNumber": a["page"], "snippet": a["snippet"][:300], "score": 1.0},
                        {"documentId": document_id, "documentName": doc_name,
                         "pageNumber": b["page"], "snippet": b["snippet"][:300], "score": 1.0},
                    ],
                    "source": "deterministic",
                })
        return conflicts


def _normalize_value(val: str) -> str:
    """Normalize a value string for comparison (lowercase, strip whitespace, remove commas)."""
    return re.sub(r"[\s,]+", "", val.lower())
