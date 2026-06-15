import json
import logging
import asyncio
import re
from typing import List, Dict, Any

from llm.registry import llm_registry
from llm.base import LLMMessage

logger = logging.getLogger("documind.services.copilot")

_SYSTEM_PROMPT = """\
You are a senior document auditor and risk officer. Based ONLY on the provided document findings, generate a review report containing:
1. reviewer_checklist: A list of items the reviewer should check/verify in the document.
2. open_questions: A list of clarifying questions to ask the document owner/author about ambiguities or contradictions.
3. compliance_concerns: A list of potential compliance, regulatory, or policy issues.
4. risk_items: Key risk factors identified in the findings (broken references, entity clashes).
5. verification_tasks: Actionable verification tasks (e.g. check budget on page X, check date on page Y).

Rules:
- DO NOT invent or hallucinate issues. Every item must map to a finding in the context.
- Keep recommendations and questions highly specific to the actual text/finding.
- Return ONLY valid JSON matching this schema:
{
  "reviewer_checklist": ["...", "..."],
  "open_questions": ["...", "..."],
  "compliance_concerns": ["...", "..."],
  "risk_items": ["...", "..."],
  "verification_tasks": ["...", "..."]
}
Do NOT return markdown fences. Return only the JSON object.
"""

class ReviewCopilotService:
    _MAX_RETRIES = 3

    async def generate_review(
        self,
        document_id: str,
        doc_name: str,
        facts: List[Dict[str, Any]],
        semantic_conflicts: List[Dict[str, Any]],
        references: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]],
        entity_conflicts: List[Dict[str, Any]],
        ambiguities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a review copilot report based on findings.
        """
        logger.info(f"[ReviewCopilot] Generating review dashboard for doc={document_id}")

        findings_context = {
            "document_name": doc_name,
            "facts_count": len(facts),
            "semantic_conflicts": [f["summary"] for f in semantic_conflicts[:8]],
            "broken_references": [f"{f['reference']} -> {f['target']} (Page {f['page']})" for f in references if f["status"] == "BROKEN_REFERENCE"][:8],
            "requirements": [{"id": r["requirement_id"], "status": r["status"]} for r in requirements[:8]],
            "entity_conflicts": [f"{c['entity']}: '{c['value_a']}' vs '{c['value_b']}'" for c in entity_conflicts[:8]],
            "top_ambiguities": [f"'{a['phrase']}' ({a['category']}) on Page {a['page']}" for a in ambiguities[:8]]
        }

        user_prompt = f"Structured Document Findings:\n{json.dumps(findings_context, indent=2)}\n\nGenerate the review dashboard JSON."

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
                    max_tokens=2000,
                ):
                    if chunk.token:
                        full_content += chunk.token
                break
            except Exception as e:
                if attempt < self._MAX_RETRIES - 1:
                    logger.warning(f"[ReviewCopilot] Attempt {attempt+1} failed: {e}. Retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    logger.error(f"[ReviewCopilot] LLM copilot failed: {e}")
                    return self._fallback_review(findings_context)

        return self._parse_review(full_content, findings_context)

    def _parse_review(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
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
            logger.warning(f"[ReviewCopilot] JSON parse failed: {e}. Falling back.")
            return self._fallback_review(context)

    def _fallback_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Grounded fallback review items in case of LLM parsing issues."""
        checklist = ["Verify that all sections mentioned in references exist."]
        open_questions = []
        risk_items = []
        verification_tasks = []

        for c in context["entity_conflicts"]:
            open_questions.append(f"What is the correct value for entity: {c}?")
            verification_tasks.append(f"Resolve conflict: {c}.")
            risk_items.append(f"Entity data clash: {c}")

        for r in context["broken_references"]:
            verification_tasks.append(f"Check broken reference: {r}")
            risk_items.append(f"Broken internal reference: {r}")

        for a in context["top_ambiguities"]:
            open_questions.append(f"Can we replace the ambiguous phrase {a} with a concrete description?")

        return {
            "reviewer_checklist": checklist or ["Verify document consistency."],
            "open_questions": open_questions or ["Are there any outstanding project questions?"],
            "compliance_concerns": ["Confirm that all requirement trace targets are satisfied."],
            "risk_items": risk_items or ["No high-priority risks detected."],
            "verification_tasks": verification_tasks or ["Verify text contents."]
        }
