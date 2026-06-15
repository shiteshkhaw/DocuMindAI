import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("documind.services.reference")

# Reference extraction regexes
REF_PATTERNS = {
    "section": re.compile(r"\b(?:Section|Sec\.)\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    "clause": re.compile(r"\bClause\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    "appendix": re.compile(r"\bAppendix\s*([A-Z\d]+)\b", re.IGNORECASE),
    "figure": re.compile(r"\b(?:Figure|Fig\.)\s*(\d+)\b", re.IGNORECASE),
    "table": re.compile(r"\bTable\s*(\d+)\b", re.IGNORECASE),
    "requirement": re.compile(r"\b(?:REQ|Requirement)\s*[- ]*(\d+)\b", re.IGNORECASE)
}

# Target definition regexes
TARGET_PATTERNS = {
    "section": [
        re.compile(r"^\s*(?:Section|Sec\.)\s*(\d+(?:\.\d+)*)", re.MULTILINE | re.IGNORECASE),
        re.compile(r"^\s*(\d+\.\d+(?:\.\d+)*)\s+[A-Z]", re.MULTILINE) # e.g. "3.2.1 Setup" at start of line
    ],
    "clause": [
        re.compile(r"^\s*Clause\s*(\d+(?:\.\d+)*)", re.MULTILINE | re.IGNORECASE)
    ],
    "appendix": [
        re.compile(r"^\s*Appendix\s*([A-Z\d]+)", re.MULTILINE | re.IGNORECASE)
    ],
    "figure": [
        re.compile(r"\b(?:Figure|Fig\.)\s*(\d+)\b\s*[:\-]", re.IGNORECASE)
    ],
    "table": [
        re.compile(r"\bTable\s*(\d+)\b\s*[:\-]", re.IGNORECASE)
    ],
    "requirement": [
        re.compile(r"\b(?:REQ|Requirement)\s*[- ]*(\d+)\b\s*[:\-]", re.IGNORECASE),
        re.compile(r"^\s*(?:REQ|Requirement)\s*[- ]*(\d+)\b", re.MULTILINE | re.IGNORECASE)
    ]
}

class ReferenceIntegrityService:
    async def verify_references(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Scan document chunks to extract references, find if their target exists,
        and flag broken references.
        Returns a list of dicts:
        { reference, target, page, status }
        """
        logger.info(f"[ReferenceService] Checking references across {len(chunks)} chunks...")
        
        # 1. Collect all defined targets
        defined_targets = {
            "section": set(),
            "clause": set(),
            "appendix": set(),
            "figure": set(),
            "table": set(),
            "requirement": set()
        }

        for text in chunks:
            for ref_type, patterns in TARGET_PATTERNS.items():
                for pattern in patterns:
                    for match in pattern.finditer(text):
                        target_val = match.group(1).strip().upper()
                        defined_targets[ref_type].add(target_val)

        # 2. Extract and verify references
        findings = []
        for text, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            
            for ref_type, pattern in REF_PATTERNS.items():
                for match in pattern.finditer(text):
                    ref_val = match.group(1).strip().upper()
                    full_ref_text = match.group(0)
                    
                    # Normalize target representation
                    target_name = f"{ref_type.capitalize()} {ref_val}"
                    
                    # Check if target exists
                    exists = ref_val in defined_targets[ref_type]
                    status = "VALID" if exists else "BROKEN_REFERENCE"
                    
                    findings.append({
                        "reference": full_ref_text,
                        "target": target_name,
                        "page": page,
                        "status": status
                    })

        # Deduplicate findings by (reference, target, page, status)
        seen = set()
        deduped = []
        for f in findings:
            key = (f["reference"].lower(), f["target"].lower(), f["page"], f["status"])
            if key not in seen:
                seen.add(key)
                deduped.append(f)

        logger.info(f"[ReferenceService] Found {len(deduped)} references (broken={sum(1 for x in deduped if x['status'] == 'BROKEN_REFERENCE')})")
        return deduped
