"""
EntityConsistencyService
========================
Analyses the entity graph and extracted facts for attribute-level inconsistencies
within and across the document.

Outputs conflicts containing:
- entity
- value_a
- value_b
- pages
- confidence
- evidence
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("documind.services.entity_consistency")

class EntityConsistencyService:
    """
    Analyses entity graph and facts for intra-document attribute inconsistencies.
    """

    async def find_inconsistencies(
        self,
        entities: List[Dict[str, Any]],
        document_id: str,
        facts: List[Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Identify conflicts in entities and facts.
        """
        conflicts = []

        # 1. Check conflicts in Extracted Facts
        if facts:
            fact_groups = {}
            for fact in facts:
                sub = fact.get("subject", "").strip()
                pred = fact.get("predicate", "").strip()
                # Facts formatted by FactsService use 'value'; raw FactExtractionService uses 'object_value'
                val = (fact.get("value") or fact.get("object_value", "")).strip()
                page = fact.get("page", 1)
                evidence = fact.get("evidence", "")
                conf = fact.get("confidence", 0.7)

                if not sub or not pred or not val:
                    continue

                # Group by subject and predicate/property
                key = (sub.lower(), pred.lower())
                fact_groups.setdefault(key, []).append({
                    "entity": sub,
                    "attribute": pred,
                    "value": val,
                    "page": page,
                    "evidence": evidence,
                    "confidence": conf
                })

            for (sub_lower, pred_lower), group in fact_groups.items():
                if len(group) < 2:
                    continue
                # Find pairs with differing values
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        val_a = group[i]["value"]
                        val_b = group[j]["value"]
                        # Compare case-insensitive
                        if val_a.lower().replace(",", "").replace("$", "") != val_b.lower().replace(",", "").replace("$", ""):
                            # Determine severity based on confidence
                            conf_val = min(group[i]["confidence"], group[j]["confidence"])
                            if conf_val >= 0.85:
                                severity = "high"
                            elif conf_val >= 0.65:
                                severity = "medium"
                            else:
                                severity = "low"
                            conflicts.append({
                                "entity": group[i]["entity"],
                                "value_a": val_a,
                                "value_b": val_b,
                                "pages": sorted(list({group[i]["page"], group[j]["page"]})),
                                "confidence": conf_val,
                                "severity": severity,
                                "evidence": f"Conflicting '{group[i]['attribute']}' for '{group[i]['entity']}'. Page {group[i]['page']}: \"{group[i]['evidence']}\" vs Page {group[j]['page']}: \"{group[j]['evidence']}\""
                            })

        # 2. Check conflicts in Entity mentions as a fallback / supplement
        if entities:
            for ent in entities:
                etype = ent.get("type", "")
                mentions = ent.get("mentions", [])
                text = ent.get("text", "")
                if len(mentions) < 2:
                    continue

                if etype == "MONEY":
                    # Look for different monetary numbers in snippets
                    values = {}
                    for m in mentions:
                        import re
                        m_text = m.get("snippet", "")
                        page = m.get("page", 1)
                        # Extract currency amounts like $50k or $50,000
                        matches = re.findall(r"\$\s*[\d,]+(?:\.\d+)?\s*(?:M|B|K|million|billion|thousand)?", m_text, re.IGNORECASE)
                        for match in matches:
                            values.setdefault(match, []).append(page)
                    
                    val_keys = list(values.keys())
                    if len(val_keys) >= 2:
                        conflicts.append({
                            "entity": text,
                            "value_a": val_keys[0],
                            "value_b": val_keys[1],
                            "pages": sorted(list({p for plist in values.values() for p in plist})),
                            "confidence": 0.8,
                            "severity": "medium",
                            "evidence": f"Different monetary values mentions for '{text}' across mentions: {', '.join(val_keys)}"
                        })

                elif etype == "DATE":
                    # Look for different dates in snippets
                    values = {}
                    for m in mentions:
                        import re
                        m_text = m.get("snippet", "")
                        page = m.get("page", 1)
                        # Match simple date patterns
                        matches = re.findall(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}|\b\d{1,2}/\d{1,2}/\d{2,4}\b", m_text, re.IGNORECASE)
                        for match in matches:
                            values.setdefault(match, []).append(page)
                    
                    val_keys = list(values.keys())
                    if len(val_keys) >= 2:
                        conflicts.append({
                            "entity": text,
                            "value_a": val_keys[0],
                            "value_b": val_keys[1],
                            "pages": sorted(list({p for plist in values.values() for p in plist})),
                            "confidence": 0.8,
                            "severity": "medium",
                            "evidence": f"Different date assignments for event '{text}': {', '.join(val_keys)}"
                        })

        # Deduplicate conflicts by entity + value_a + value_b
        seen = set()
        deduped = []
        for c in conflicts:
            ent = c.get("entity")
            ent_str = "".join(ent) if isinstance(ent, list) else str(ent or "")

            va = c.get("value_a")
            va_str = "".join(va) if isinstance(va, list) else str(va or "")

            vb = c.get("value_b")
            vb_str = "".join(vb) if isinstance(vb, list) else str(vb or "")

            key = (ent_str.lower(), va_str.lower(), vb_str.lower())
            rev_key = (ent_str.lower(), vb_str.lower(), va_str.lower())
            if key not in seen and rev_key not in seen:
                seen.add(key)
                deduped.append(c)

        logger.info(f"[EntityConsistency] Found {len(deduped)} inconsistencies in doc={document_id}")
        return deduped
