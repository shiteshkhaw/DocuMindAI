import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("documind.services.trust_score")


# ── Deduction amounts (named constants — no magic numbers) ────────────────────
_DEDUCT_CONTRADICTION_CRITICAL = 20.0
_DEDUCT_CONTRADICTION_HIGH     = 12.0
_DEDUCT_CONTRADICTION_MEDIUM   = 6.0
_DEDUCT_CONTRADICTION_LOW      = 2.0

_DEDUCT_ENTITY_CONFLICT_HIGH   = 15.0
_DEDUCT_ENTITY_CONFLICT_MEDIUM = 8.0
_DEDUCT_ENTITY_CONFLICT_LOW    = 3.0

_DEDUCT_REF_BROKEN             = 8.0

_DEDUCT_REQ_MISSING            = 12.0
_DEDUCT_REQ_ORPHANED           = 4.0

_DEDUCT_AMBIGUITY_HIGH         = 8.0
_DEDUCT_AMBIGUITY_MEDIUM       = 4.0
_DEDUCT_AMBIGUITY_LOW          = 1.5

_DEDUCT_PLACEHOLDER            = 8.0

# ── Component score floor — prevent one type of issue from zeroing overall ─────
_COMPONENT_MIN = 0.0


class TrustScoreV2Service:
    async def compute_trust_score(
        self,
        document_id: str,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        semantic_conflicts: List[Dict[str, Any]],
        references: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]],
        entity_conflicts: List[Dict[str, Any]],
        ambiguities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute a weighted, explainable trust score.

        Components and weights:
          - 35% Contradiction Health      — semantic + entity conflicts
          - 20% Reference Integrity       — broken internal references
          - 15% Requirement Traceability  — missing / orphaned requirements
          - 15% Entity Consistency        — attribute-level contradictions
          - 10% Ambiguity Analysis        — vague language
          -  5% Document Completeness     — unresolved placeholders

        Every deduction is logged with evidence + page + finding_id.
        Confidence score is derived from evidence quality, not a magic number.
        """
        logger.info(f"[TrustScoreService] Computing trust score for doc={document_id}")
        deductions: List[Dict[str, Any]] = []

        # ── 1. Contradiction Health (35%) ─────────────────────────────────────
        contr_score = 100.0
        for conflict in semantic_conflicts:
            sev = conflict.get("severity", "medium").lower()
            if sev == "critical":
                deduct_pts = _DEDUCT_CONTRADICTION_CRITICAL
            elif sev == "high":
                deduct_pts = _DEDUCT_CONTRADICTION_HIGH
            elif sev == "low":
                deduct_pts = _DEDUCT_CONTRADICTION_LOW
            else:
                deduct_pts = _DEDUCT_CONTRADICTION_MEDIUM

            contr_score -= deduct_pts
            deductions.append({
                "component": "Contradiction Health",
                "points": deduct_pts,
                "evidence": f"Semantic conflict ({sev}): '{conflict.get('summary') or conflict.get('conflict_type', '')}'",
                "page": conflict.get("page_a") or 1,
                "finding_id": conflict.get("id") or "unknown"
            })
        contr_score = max(_COMPONENT_MIN, contr_score)

        # ── 2. Reference Integrity (20%) ──────────────────────────────────────
        ref_score = 100.0
        for ref in references:
            if ref.get("status") == "BROKEN_REFERENCE":
                ref_score -= _DEDUCT_REF_BROKEN
                deductions.append({
                    "component": "Reference Integrity",
                    "points": _DEDUCT_REF_BROKEN,
                    "evidence": f"Broken reference: '{ref.get('reference')}' → target '{ref.get('target')}' not found",
                    "page": ref.get("page") or 1,
                    "finding_id": f"ref-{ref.get('reference')}-{ref.get('page')}"
                })
        ref_score = max(_COMPONENT_MIN, ref_score)

        # ── 3. Requirement Traceability (15%) ─────────────────────────────────
        req_score = 100.0
        for req in requirements:
            status = req.get("status")
            if status == "MISSING":
                req_score -= _DEDUCT_REQ_MISSING
                page = (req.get("reference_pages") or [1])[0]
                deductions.append({
                    "component": "Requirement Traceability",
                    "points": _DEDUCT_REQ_MISSING,
                    "evidence": f"Requirement '{req.get('requirement_id')}' referenced but never defined",
                    "page": page,
                    "finding_id": f"req-missing-{req.get('requirement_id')}"
                })
            elif status == "ORPHANED":
                req_score -= _DEDUCT_REQ_ORPHANED
                page = (req.get("definition_pages") or [1])[0]
                deductions.append({
                    "component": "Requirement Traceability",
                    "points": _DEDUCT_REQ_ORPHANED,
                    "evidence": f"Requirement '{req.get('requirement_id')}' defined but never referenced (orphaned)",
                    "page": page,
                    "finding_id": f"req-orphaned-{req.get('requirement_id')}"
                })
        req_score = max(_COMPONENT_MIN, req_score)

        # ── 4. Entity Consistency (15%) ───────────────────────────────────────
        ent_score = 100.0
        for conflict in entity_conflicts:
            sev = conflict.get("severity", "medium").lower()
            if sev == "critical" or sev == "high":
                deduct_pts = _DEDUCT_ENTITY_CONFLICT_HIGH
            elif sev == "low":
                deduct_pts = _DEDUCT_ENTITY_CONFLICT_LOW
            else:
                deduct_pts = _DEDUCT_ENTITY_CONFLICT_MEDIUM

            ent_score -= deduct_pts
            pages = conflict.get("pages") or [1]
            deductions.append({
                "component": "Entity Consistency",
                "points": deduct_pts,
                "evidence": (
                    f"Conflicting values for entity '{conflict.get('entity')}': "
                    f"'{conflict.get('value_a')}' vs '{conflict.get('value_b')}'"
                ),
                "page": pages[0],
                "finding_id": f"ent-conflict-{conflict.get('entity')}"
            })
        ent_score = max(_COMPONENT_MIN, ent_score)

        # ── 5. Ambiguity Analysis (10%) ───────────────────────────────────────
        amb_score = 100.0
        for amb in ambiguities:
            sev = amb.get("severity", "low").lower()
            if sev == "high":
                deduct_pts = _DEDUCT_AMBIGUITY_HIGH
            elif sev == "medium":
                deduct_pts = _DEDUCT_AMBIGUITY_MEDIUM
            else:
                deduct_pts = _DEDUCT_AMBIGUITY_LOW

            amb_score -= deduct_pts
            deductions.append({
                "component": "Ambiguity Analysis",
                "points": deduct_pts,
                "evidence": f"Ambiguous term '{amb.get('phrase')}' ({amb.get('category')}) — {amb.get('recommendation', '')}",
                "page": amb.get("page") or 1,
                "finding_id": f"amb-{amb.get('phrase')}-{amb.get('page')}"
            })
        amb_score = max(_COMPONENT_MIN, amb_score)

        # ── 6. Document Completeness (5%) ─────────────────────────────────────
        comp_score = 100.0
        placeholder_regex = re.compile(r"\b(?:TODO|TBD|__+|\[insert[^\]]*\])\b", re.IGNORECASE)
        seen_placeholders: set = set()
        for idx, (text, meta) in enumerate(zip(chunks, metadatas)):
            page = meta.get("page_number", 1)
            for match in placeholder_regex.finditer(text):
                ph_key = (match.group(0).lower(), page)
                if ph_key in seen_placeholders:
                    continue
                seen_placeholders.add(ph_key)
                comp_score -= _DEDUCT_PLACEHOLDER
                deductions.append({
                    "component": "Document Completeness",
                    "points": _DEDUCT_PLACEHOLDER,
                    "evidence": f"Unresolved placeholder: '{match.group(0)}' on page {page}",
                    "page": page,
                    "finding_id": f"comp-{match.group(0)}-{page}"
                })
        comp_score = max(_COMPONENT_MIN, comp_score)

        # ── Weighted final score ───────────────────────────────────────────────
        final_score = (
            0.35 * contr_score +
            0.20 * ref_score +
            0.15 * req_score +
            0.15 * ent_score +
            0.10 * amb_score +
            0.05 * comp_score
        )
        final_score = max(0.0, min(100.0, round(final_score, 2)))

        # ── Confidence score: based on how many components have evidence ───────
        # High evidence quality → high confidence in the score
        components_with_issues = sum([
            1 if contr_score < 100 else 0,
            1 if ref_score < 100 else 0,
            1 if req_score < 100 else 0,
            1 if ent_score < 100 else 0,
            1 if amb_score < 100 else 0,
            1 if comp_score < 100 else 0,
        ])
        total_chunks = max(1, len(chunks))
        # More chunks = higher confidence in coverage; more issues found = higher confidence in accuracy
        coverage_factor = min(1.0, total_chunks / 20.0)  # saturates at 20+ chunks
        confidence = round(0.70 + 0.20 * coverage_factor + 0.10 * (components_with_issues / 6.0), 3)
        confidence = min(0.98, confidence)  # cap at 0.98 — we never claim perfect confidence

        evidence_text = (
            f"Trust score computed from {len(chunks)} chunks across 6 dimensions. "
            f"Breakdown — Contradictions: {round(contr_score)}%, "
            f"References: {round(ref_score)}%, "
            f"Requirements: {round(req_score)}%, "
            f"Entities: {round(ent_score)}%, "
            f"Ambiguity: {round(amb_score)}%, "
            f"Completeness: {round(comp_score)}%. "
            f"Total deductions: {len(deductions)}."
        )

        return {
            "score": final_score,
            "confidence": confidence,
            "breakdown": {
                "contradiction_health": round(contr_score, 2),
                "reference_integrity": round(ref_score, 2),
                "requirement_traceability": round(req_score, 2),
                "entity_consistency": round(ent_score, 2),
                "ambiguity_analysis": round(amb_score, 2),
                "document_completeness": round(comp_score, 2)
            },
            "deductions": deductions,
            "evidence": evidence_text
        }
