import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("documind.services.ambiguity")

AMBIGUITY_RULES = [
    {"pattern": r"\bsoon\b", "phrase": "soon", "category": "Vagueness", "severity": "medium", "recommendation": "Define a specific date or deadline (e.g. 'within 10 business days') instead of the vague 'soon'."},
    {"pattern": r"\bpromptly\b", "phrase": "promptly", "category": "Vagueness", "severity": "medium", "recommendation": "Specify a precise turnaround time (e.g., 'within 24 hours') instead of 'promptly'."},
    {"pattern": r"\bquickly\b", "phrase": "quickly", "category": "Vagueness", "severity": "low", "recommendation": "Quantify the duration or performance metric instead of 'quickly'."},
    {"pattern": r"\bas needed\b", "phrase": "as needed", "category": "Vagueness", "severity": "low", "recommendation": "Specify the exact triggering conditions or criteria for what is needed."},
    {"pattern": r"\breasonable\b", "phrase": "reasonable", "category": "Subjectivity", "severity": "low", "recommendation": "Define the objective standard or metrics that define 'reasonable'."},
    {"pattern": r"\bappropriate\b", "phrase": "appropriate", "category": "Subjectivity", "severity": "low", "recommendation": "State the standard, policy, or role responsible for determining what is 'appropriate'."},
    {"pattern": r"\bsufficient\b", "phrase": "sufficient", "category": "Subjectivity", "severity": "low", "recommendation": "Specify the quantitative threshold that qualifies as 'sufficient'."},
    {"pattern": r"\bmay\b", "phrase": "may", "category": "Permissiveness", "severity": "medium", "recommendation": "State if this is purely optional, or use 'shall' / 'must' if it is a mandatory obligation."},
    {"pattern": r"\bshould\b", "phrase": "should", "category": "Permissiveness", "severity": "medium", "recommendation": "Use 'shall' or 'must' to establish a requirement, or clearly label this as a recommendation."},
    {"pattern": r"\bif necessary\b", "phrase": "if necessary", "category": "Conditional", "severity": "low", "recommendation": "Explicitly define the scenarios under which this action is necessary."},
    {"pattern": r"\bwhere applicable\b", "phrase": "where applicable", "category": "Conditional", "severity": "low", "recommendation": "Detail the specific scope or sections where this clause applies."},
    {"pattern": r"\btypically\b", "phrase": "typically", "category": "Generalization", "severity": "low", "recommendation": "Clearly state the rule and describe any known exceptions instead of using 'typically'."},
    {"pattern": r"\bnormally\b", "phrase": "normally", "category": "Generalization", "severity": "low", "recommendation": "Specify the normal operating conditions or criteria."}
]

class AmbiguityDetectionService:
    # Cap total ambiguities to avoid trust score collapse on verbose documents
    _MAX_FINDINGS = 50

    async def detect_ambiguities(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Scan document chunks for ambiguous terms and return a list of findings:
        { phrase, category, page, severity, recommendation }
        Deduplicates by (phrase_lower, page) to avoid overcounting repeated terms.
        """
        logger.info(f"[AmbiguityService] Scanning {len(chunks)} chunks...")
        findings = []
        seen: set = set()  # (phrase_lower, page) dedup key

        for chunk_idx, (text, meta) in enumerate(zip(chunks, metadatas)):
            page = meta.get("page_number", 1)
            
            for rule in AMBIGUITY_RULES:
                # Find all occurrences of the pattern in this chunk
                for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
                    phrase_matched = match.group(0).lower().strip()
                    dedup_key = (phrase_matched, page)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    findings.append({
                        "phrase": match.group(0),
                        "category": rule["category"],
                        "page": page,
                        "severity": rule["severity"],
                        "recommendation": rule["recommendation"]
                    })
                    if len(findings) >= self._MAX_FINDINGS:
                        logger.info(
                            f"[AmbiguityService] Hit cap of {self._MAX_FINDINGS} findings — stopping early."
                        )
                        return findings

        logger.info(f"[AmbiguityService] Found {len(findings)} ambiguities (deduped)")
        return findings
