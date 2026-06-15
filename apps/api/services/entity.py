import uuid
import json
import logging
import re
import asyncio
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from llm.registry import llm_registry
from llm.base import LLMMessage

logger = logging.getLogger("documind.services.entity")

ENTITY_EXTRACTION_SYSTEM = """You are an expert document intelligence analyst specialising in information extraction and knowledge graphing.
Extract ALL named entities, their relationships, and conflicts from the document text.

Entity types to extract:
- PERSON: Individual people's names
- ORGANIZATION: Companies, institutions, agencies, departments
- LOCATION: Countries, cities, addresses, regions
- DATE: Specific dates, time periods, or deadlines
- MONEY: Financial values, budgets, costs, revenue
- PRODUCT: Products, software, systems, platforms, hardware
- REQUIREMENT_ID: IDs like REQ-001, RFC-123, FR-456
- SECTION_REF: Document section references like §3.2, Section 4.1

For each entity, record:
- text: The exact string representation of the entity (normalized name)
- type: The entity type from the list above
- confidence: Extraction confidence (0.0 to 1.0)
- mentions: An array of occurrences where page = page number, snippet = surrounding text context (max 50 chars)
- related_entities: A list of names of OTHER extracted entities that this entity directly relates to in the text.

Also detect ENTITY CONFLICTS:
Find instances where the same entity concept or type has conflicting attributes/values assigned in different contexts.
For example:
- "Vendor is listed as ABC Corp on page 2, but XYZ Inc on page 7."
- "Release date is Jan 1st on page 1, but March 15th on page 4."
- "System budget is $1M on page 3, but $2.5M on page 8."

Return ONLY raw valid JSON in this exact schema:
{
  "entities": [
    {
      "text": "Entity text",
      "type": "ENTITY_TYPE",
      "confidence": 0.95,
      "mentions": [
        {"page": 1, "snippet": "surrounding text context"},
        {"page": 4, "snippet": "another context"}
      ],
      "related_entities": ["Other Entity Name"]
    }
  ],
  "entityConflicts": [
    {
      "entity_type": "MONEY",
      "values": ["$1M", "$2.5M"],
      "pages": [3, 8],
      "description": "System budget is $1M on page 3 but $2.5M on page 8"
    }
  ],
  "keyValuePairs": [
    {"key": "Project Name", "value": "DocuMind AI", "confidence": 0.99}
  ],
  "summary": {
    "abstract": "One paragraph description of the document",
    "keyPoints": ["Key insight 1", "Key insight 2"],
    "suggestedQuestions": ["What is...?", "How does...?"]
  }
}

Return ONLY the JSON object. No markdown, no explanations, no code block wrapping."""


class EntityGraphService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_entities(
        self,
        chunks: List[str],
        document_id: str,
        doc_name: str
    ) -> Dict[str, Any]:
        """
        Extracts named entities, maps relationships, identifies conflicts,
        and constructs an entity graph dataset returned as a dictionary.
        """
        try:
            # Combine chunks, preserving page markers in context
            doc_text_parts = []
            for i, chunk in enumerate(chunks[:30]):  # Limit to first 30 chunks
                doc_text_parts.append(f"[Segment {i+1}]\n{chunk}")
            doc_text = "\n\n---\n\n".join(doc_text_parts)

            # Trim to stay within token context window
            if len(doc_text) > 15000:
                doc_text = doc_text[:15000] + "\n\n[...truncated for entity analysis...]"

            provider_name, model = llm_registry.resolve_model_route("documind-v3")
            provider = llm_registry.get_provider(provider_name)

            messages = [
                LLMMessage(role="system", content=ENTITY_EXTRACTION_SYSTEM),
                LLMMessage(
                    role="user",
                    content=f"Extract entities, graph relationships, and conflicts from document '{doc_name}':\n\n{doc_text}"
                ),
            ]

            full_content = ""
            max_retries = 3
            retry_delay = 1.0

            for attempt in range(max_retries):
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
                    if attempt < max_retries - 1:
                        logger.warning(f"[EntityGraphService] LLM attempt {attempt+1} failed: {e}. Retrying...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2.0
                    else:
                        raise e

            extracted = self._parse_extraction_response(full_content)
            
            # Post-process and refine the entity graph
            entities = extracted.get("entities", [])
            deduplicated = self._deduplicate_entities(entities)
            
            # Enrich relationship mappings based on shared mentions or explicit relations
            self._enrich_relationships(deduplicated)

            extracted["entities"] = deduplicated
            return extracted

        except Exception as e:
            logger.error(f"[EntityGraphService] Analysis failed for {document_id}: {e}", exc_info=True)
            return {
                "entities": [],
                "entityConflicts": [],
                "keyValuePairs": [],
                "summary": {
                    "abstract": f"Error running entity intelligence: {str(e)}",
                    "keyPoints": [],
                    "suggestedQuestions": []
                }
            }

    def _parse_extraction_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            clean = content.strip()
            if clean.startswith("```"):
                first = clean.find("{")
                last = clean.rfind("}")
                if first != -1 and last != -1:
                    clean = clean[first : last + 1]

            match = re.search(r"(\{.*\})", clean, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"[EntityGraphService] Failed to parse response: {e}. Preview: {content[:200]}")
            return {}

    def _deduplicate_entities(self, raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge duplicate entities of same text & type, aggregating mentions and relationships."""
        seen = {}
        for ent in raw:
            text = ent.get("text", "").strip()
            etype = ent.get("type", "").strip()
            if not text or not etype:
                continue

            key = (text.lower(), etype)
            if key in seen:
                existing = seen[key]
                existing["mentions"] = self._merge_mentions(existing.get("mentions", []), ent.get("mentions", []))
                existing["confidence"] = max(existing.get("confidence", 0), ent.get("confidence", 0))
                
                # Merge related entities lists
                rels = set(existing.get("related_entities", []))
                for r in ent.get("related_entities", []):
                    if r.lower().strip() != text.lower().strip():
                        rels.add(r)
                existing["related_entities"] = list(rels)
            else:
                ent_copy = dict(ent)
                ent_copy["related_entities"] = [r for r in ent_copy.get("related_entities", []) if r.lower().strip() != text.lower().strip()]
                seen[key] = ent_copy

        return list(seen.values())

    def _merge_mentions(self, a: List[Dict], b: List[Dict]) -> List[Dict]:
        """Merge page mentions lists without duplication."""
        pages_seen = set()
        merged = []
        for m in a + b:
            p = m.get("page", 0)
            snippet = m.get("snippet", "")
            if (p, snippet) not in pages_seen:
                pages_seen.add((p, snippet))
                merged.append(m)
        return sorted(merged, key=lambda x: x.get("page", 0))

    def _enrich_relationships(self, entities: List[Dict[str, Any]]):
        """Build bidirectional relationship edges and clean up references."""
        entity_names_map = {e["text"].lower().strip(): e for e in entities}
        
        # Ensure relations point to valid existing entities, and are bidirectional
        for ent in entities:
            name = ent["text"]
            valid_relations = []
            for rel in ent.get("related_entities", []):
                rel_clean = rel.strip()
                if not rel_clean or rel_clean.lower() == name.lower():
                    continue
                valid_relations.append(rel_clean)

                # Ensure bidirectional link
                if rel_clean.lower() in entity_names_map:
                    rel_ent = entity_names_map[rel_clean.lower()]
                    if "related_entities" not in rel_ent:
                        rel_ent["related_entities"] = []
                    if name.lower() not in [r.lower() for r in rel_ent["related_entities"]]:
                        rel_ent["related_entities"].append(name)

            ent["related_entities"] = valid_relations
