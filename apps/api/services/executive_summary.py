import json
import logging
import asyncio
import re
from typing import List, Dict, Any

from llm.registry import llm_registry
from llm.base import LLMMessage

logger = logging.getLogger("documind.services.executive_summary")

_SYSTEM_PROMPT = """\
You are an executive document intelligence assistant. Your task is to compile a high-level executive report based ONLY on the supplied structured document findings.

Your response must contain exactly these 8 sections in a structured JSON format:
1. executive_summary: A concise, executive-level summary of the document.
2. key_findings: A list of the most important facts/points extracted from the document.
3. critical_risks: A list of any risks identified (broken references, conflicts, ambiguities).
4. major_contradictions: A list of contradictions or inconsistencies found.
5. important_entities: A list of key entities (organizations, people, budgets) and their roles.
6. requirements_overview: A summary of the requirements and their traceability.
7. trust_assessment: An explanation of the trust score and why points were deducted.
8. recommended_actions: A list of concrete recommendations to fix the issues in the document.

Rules:
- DO NOT invent or hallucinate any facts.
- Ground all summaries and assessments strictly on the findings provided in the user prompt.
- Return ONLY valid JSON matching this schema:
{
  "executive_summary": "...",
  "key_findings": ["...", "..."],
  "critical_risks": ["...", "..."],
  "major_contradictions": ["...", "..."],
  "important_entities": ["...", "..."],
  "requirements_overview": "...",
  "trust_assessment": "...",
  "recommended_actions": ["...", "..."]
}
Do NOT return markdown fences. Return only the JSON object.
"""

class ExecutiveSummaryService:
    _MAX_RETRIES = 3

    async def generate_summary(
        self,
        document_id: str,
        doc_name: str,
        facts: List[Dict[str, Any]],
        semantic_conflicts: List[Dict[str, Any]],
        references: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]],
        entity_conflicts: List[Dict[str, Any]],
        ambiguities: List[Dict[str, Any]],
        trust_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an executive summary based entirely on findings.
        """
        logger.info(f"[ExecutiveSummary] Generating summary for doc={document_id}")
        
        # Prepare structured findings as a clean context prompt
        findings_context = {
            "document_name": doc_name,
            "trust_score": trust_score.get("score", 100.0),
            "trust_breakdown": trust_score.get("breakdown", {}),
            "facts_count": len(facts),
            "top_facts": [
                f"{f['subject']} {f['predicate']} {f.get('value') or f.get('object_value', '')}"
                for f in facts[:15]
            ],
            "semantic_conflicts": [f["summary"] for f in semantic_conflicts[:8]],
            "broken_references": [f"{f['reference']} -> {f['target']}" for f in references if f["status"] == "BROKEN_REFERENCE"][:8],
            "requirements": [{"id": r["requirement_id"], "status": r["status"]} for r in requirements[:10]],
            "entity_conflicts": [f"{c['entity']}: '{c['value_a']}' vs '{c['value_b']}'" for c in entity_conflicts[:8]],
            "top_ambiguities": [f"'{a['phrase']}' ({a['category']})" for a in ambiguities[:8]]
        }

        user_prompt = f"Structured Document Findings:\n{json.dumps(findings_context, indent=2)}\n\nGenerate the executive report matching the required 8 sections."

        messages = [
            LLMMessage(role="system", content=_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt)
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
                    max_tokens=2500,
                ):
                    if chunk.token:
                        full_content += chunk.token
                break
            except Exception as e:
                if attempt < self._MAX_RETRIES - 1:
                    logger.warning(f"[ExecutiveSummary] Attempt {attempt+1} failed: {e}. Retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    logger.error(f"[ExecutiveSummary] LLM summary failed: {e}")
                    # Return a default fallback grounded in facts
                    return self._fallback_summary(findings_context)

        return self._parse_summary(full_content, findings_context)

    def _parse_summary(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            clean = content.strip()
            if clean.startswith("```"):
                first = clean.find("{")
                last = clean.rfind("}")
                if first != -1 and last != -1:
                    clean = clean[first : last + 1]
            match = re.search(r"(\{.*\})", clean, re.DOTALL)
            json_str = match.group(0) if match else clean
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"[ExecutiveSummary] JSON parse failed: {e}. Falling back.")
            return self._fallback_summary(context)

    def _fallback_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Grounded fallback summary in case of LLM parsing errors."""
        return {
            "executive_summary": f"Executive summary of {context['document_name']}. The document has a trust score of {context['trust_score']}% based on automated intelligence checks.",
            "key_findings": [f"Fact: {f}" for f in context["top_facts"]] or ["No major facts extracted."],
            "critical_risks": [f"Broken reference: {r}" for r in context["broken_references"]] + [f"Ambiguity: {a}" for a in context["top_ambiguities"]],
            "major_contradictions": context["semantic_conflicts"] or ["No major contradictions found."],
            "important_entities": context["entity_conflicts"] or ["No major entity conflicts found."],
            "requirements_overview": f"Document contains {len(context['requirements'])} identified requirement tracking items.",
            "trust_assessment": f"Evaluated trust score is {context['trust_score']}%: Contradiction health score is {context['trust_breakdown'].get('contradiction_health', 100.0)}%. Reference integrity score is {context['trust_breakdown'].get('reference_integrity', 100.0)}%.",
            "recommended_actions": ["Verify and repair identified broken references.", "Clarify identified ambiguous terminology."]
        }
