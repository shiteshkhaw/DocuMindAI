import uuid
import json
import logging
import time
import asyncio
import re
import numpy as np
from typing import AsyncGenerator, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.document import DocumentRepository
from llm.registry import llm_registry
from llm.base import LLMMessage
from embeddings.base import BaseEmbeddingProvider
from vectorstore.base import BaseVectorStore

logger = logging.getLogger("documind.services.contradiction_v2")

_JSON_SCHEMA = """
{
  "contradictions": [
    {
      "type": "numerical|date|timeline|requirement|entity|logical",
      "confidence": 0.0-1.0,
      "contradiction_strength": 0.0-1.0,
      "summary": "One-sentence summary of the conflict",
      "explanation": "Detailed explanation of why these statements contradict",
      "conflictingStatements": [
        {"text": "Exact quote from document", "page": <page_number>},
        {"text": "Exact conflicting quote", "page": <page_number>}
      ]
    }
  ]
}
"""

CONTRADICTION_PROMPT_SYSTEM = f"""You are a senior document intelligence auditor specializing in inconsistency detection.
Identify internal contradictions, discrepancies, and conflicts within the provided document segments.

Detection categories:
- numerical: Different values assigned to the same metric/quantity (revenue, budget, counts, versions).
- date: Conflicting calendar dates or deadlines for the same event/deliverable.
- timeline: Sequence or dependency inconsistencies (e.g. Task A before Task B, but later Task B before Task A).
- requirement: System or business requirements that directly contradict (e.g., system must require auth vs allow anonymous access).
- entity: Conflicting attributes, names, or roles assigned to the same entity (person, vendor, location, product).
- logical: Directly contradicting cause-effect, constraints, or structural logic (e.g., feature mandatory vs optional).

For each contradiction:
1. Provide a confidence score (0.0 to 1.0) on whether this is a genuine contradiction.
2. Provide a contradiction_strength score (0.0 to 1.0) representing how direct/strong the conflict is (1.0 = mutually exclusive, 0.1 = minor difference).
3. Extract the exact quotes for conflictingStatements (exactly as they appear in the text) and their page numbers.

Return ONLY raw valid JSON matching this schema:
{_JSON_SCHEMA}

If no contradictions are found, return: {{"contradictions": []}}
Do NOT include markdown code fences or HTML block wrapping. Return only the JSON object."""


class ContradictionEngine:
    def __init__(
        self,
        db: AsyncSession,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider
    ):
        self.db = db
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.doc_repo = DocumentRepository(db)
        self.collection_name = "documind_chunks"

    async def detect_contradictions(
        self,
        document_id: str,
        model_name: str = "documind-v3"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Runs the contradiction detection pipeline V2:
        1. Fetch document chunks & embeddings from Chroma
        2. Cluster chunks using cosine similarity neighborhoods
        3. For each cluster, invoke LLM contradiction agent
        4. Calculate semantic distance of conflicting statements via embedding cosine distance
        5. Compute mathematical severity scoring
        6. Yield discoveries and final metrics telemetry
        """
        start_time = time.perf_counter()
        
        yield {"type": "status", "message": "Loading document metadata..."}
        doc = await self.doc_repo.get(document_id)
        if not doc:
            yield {"type": "error", "message": f"Document {document_id} not found."}
            return
        doc_name = doc.name

        yield {"type": "status", "message": "Retrieving document chunks from Chroma..."}
        client = getattr(self.vector_store, "_client", None)
        if not client:
            yield {"type": "error", "message": "Vector store client is unavailable."}
            return

        try:
            collection = await asyncio.to_thread(
                client.get_or_create_collection,
                self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            res = await asyncio.to_thread(
                collection.get,
                where={"document_id": document_id},
                include=["embeddings", "documents", "metadatas"],
            )
        except Exception as e:
            logger.error(f"[ContradictionEngine] Chroma fetch failed: {e}", exc_info=True)
            yield {"type": "error", "message": f"Chroma fetch failed: {e}"}
            return

        embeddings = res.get("embeddings")
        if embeddings is None:
            embeddings = []
        documents = res.get("documents")
        if documents is None:
            documents = []
        metadatas = res.get("metadatas")
        if metadatas is None:
            metadatas = []
        ids = res.get("ids")
        if ids is None:
            ids = []
        retrieval_count = len(ids)

        if retrieval_count == 0:
            yield {"type": "error", "message": f"No indexed chunks found for document: {doc_name}"}
            return

        yield {"type": "status", "message": f"Analysing {retrieval_count} chunks..."}

        # Step 2: Semantic Grouping & Candidate Pair Generation
        candidate_pairs = self._generate_candidate_pairs(ids, embeddings)
        max_candidates = max(8, min(15, len(candidate_pairs)))
        candidate_pairs = candidate_pairs[:max_candidates]

        yield {"type": "status", "message": f"Auditing {len(candidate_pairs)} candidate contradiction pairs..."}

        # Resolve LLM Provider
        provider_name, actual_model = llm_registry.resolve_model_route(model_name)
        provider = llm_registry.get_provider(provider_name)

        total_reasoning_time = 0.0
        all_findings = []
        seen_summaries = set()

        async def analyze_pair(pair: List[int]) -> List[Dict[str, Any]]:
            nonlocal total_reasoning_time
            idx_a, idx_b = pair[0], pair[1]
            page_a = metadatas[idx_a].get("page_number", 1)
            page_b = metadatas[idx_b].get("page_number", 1)

            if idx_a == idx_b:
                user_prompt = (
                    f"Document Name: {doc_name}\n\n"
                    f"Source Segment:\n---\n"
                    f"[Segment 1 - Page {page_a}]\n\"{documents[idx_a]}\"\n---\n\n"
                    f"Identify contradictions within this segment. Return raw JSON matching schema."
                )
            else:
                user_prompt = (
                    f"Document Name: {doc_name}\n\n"
                    f"Source Segments:\n---\n"
                    f"[Segment 1 - Page {page_a}]\n\"{documents[idx_a]}\"\n\n"
                    f"[Segment 2 - Page {page_b}]\n\"{documents[idx_b]}\"\n---\n\n"
                    f"Identify contradictions between these two segments. Return raw JSON matching schema."
                )
            messages = [
                LLMMessage(role="system", content=CONTRADICTION_PROMPT_SYSTEM),
                LLMMessage(role="user", content=user_prompt),
            ]

            t_start = time.perf_counter()
            full_content = ""
            max_retries = 3
            retry_delay = 1.0

            for attempt in range(max_retries):
                try:
                    async for chunk in provider.generate_stream(
                        messages=messages,
                        model=actual_model,
                        temperature=0.0,
                        max_tokens=2000,
                    ):
                        if chunk.token:
                            full_content += chunk.token
                    break
                except Exception as e:
                    logger.warning(f"[ContradictionEngine] LLM attempt {attempt+1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2.0
                    else:
                        raise e

            elapsed = time.perf_counter() - t_start
            total_reasoning_time += elapsed

            return await self._process_llm_response(
                full_content, [idx_a, idx_b] if idx_a != idx_b else [idx_a], documents, metadatas, document_id, doc_name
            )

        # Build analysis tasks
        analysis_tasks = [analyze_pair(pair) for pair in candidate_pairs]
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        for r_list in results:
            if isinstance(r_list, BaseException):
                logger.error(f"[ContradictionEngine] Analysis task failed: {r_list}", exc_info=True)
                continue
            if isinstance(r_list, list):
                for item in r_list:
                    summ = item.get("summary", "").lower().strip()
                    if summ and summ not in seen_summaries:
                        seen_summaries.add(summ)
                        all_findings.append(item)
                        yield {"type": "insight", "insight": item}

        orch_duration = time.perf_counter() - start_time
        telemetry = {
            "retrievalCount": retrieval_count,
            "contradictionCount": len(all_findings),
            "reasoningLatency": round(total_reasoning_time, 3),
            "orchestrationLatency": round(orch_duration, 3),
            "providerLatency": round(total_reasoning_time, 3),
        }
        logger.info(f"[ContradictionEngine] Completed for {document_id}. Telemetry: {telemetry}")
        yield {"type": "telemetry", "metrics": telemetry}

    def _generate_candidate_pairs(self, ids: List[str], embeddings: List) -> List[List[int]]:
        """Find candidate contradiction pairs using cosine similarity on embeddings."""
        if len(ids) == 0:
            return []
        if len(ids) == 1:
            return [[0, 0]]

        try:
            emb_array = np.array(embeddings, dtype=np.float32)
            norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            normalized = emb_array / norms
            sim_matrix = np.dot(normalized, normalized.T)

            candidates = []
            visited = set()
            n = len(ids)
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    sim = float(sim_matrix[i][j])
                    # Target similarity band for contradictions
                    if 0.45 <= sim <= 0.95:
                        pair = tuple(sorted([i, j]))
                        if pair not in visited:
                            visited.add(pair)
                            candidates.append((list(pair), sim))

            # Sort by "most likely to conflict" (closest to 0.70)
            candidates.sort(key=lambda x: abs(x[1] - 0.70))
            return [x[0] for x in candidates]
        except Exception as e:
            logger.error(f"[ContradictionEngine] Candidate generation failed: {e}")
            return [[i, i + 1] for i in range(len(ids) - 1)]

    async def _process_llm_response(
        self,
        content: str,
        group: List[int],
        documents: List[str],
        metadatas: List[Dict],
        document_id: str,
        doc_name: str,
    ) -> List[Dict[str, Any]]:
        """Parse LLM JSON, calculate semantic distance, compute severity, and resolve citations."""
        try:
            clean = content.strip()
            if clean.startswith("```"):
                first_brace = clean.find("{")
                last_brace = clean.rfind("}")
                if first_brace != -1 and last_brace != -1:
                    clean = clean[first_brace : last_brace + 1]

            match = re.search(r"(\{.*\})", clean, re.DOTALL)
            json_str = match.group(0) if match else clean
            data = json.loads(json_str)
            findings = data.get("contradictions", [])

            resolved = []
            for finding in findings:
                conflicting = finding.get("conflictingStatements", [])
                if len(conflicting) < 2:
                    continue

                stmt_a = conflicting[0].get("text", "")
                stmt_b = conflicting[1].get("text", "")
                confidence = float(finding.get("confidence", 0.8))
                strength = float(finding.get("contradiction_strength", 0.8))

                # Step 4 & 5: Calculate Semantic Distance & Severity Score
                similarity = 0.5
                try:
                    # Embed statements using provider
                    embs = await self.embedding_provider.embed_documents([stmt_a, stmt_b])
                    if len(embs) == 2:
                        vec_a = np.array(embs[0])
                        vec_b = np.array(embs[1])
                        norm_a = np.linalg.norm(vec_a)
                        norm_b = np.linalg.norm(vec_b)
                        if norm_a > 0 and norm_b > 0:
                            similarity = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
                except Exception as emb_e:
                    logger.warning(f"[ContradictionEngine] Statement embedding failed: {emb_e}")

                # semantic_distance = 1.0 - similarity
                # score = confidence * 0.4 + strength * 0.4 + similarity * 0.2
                # similarity represents (1.0 - semantic_distance)
                score = confidence * 0.4 + strength * 0.4 + similarity * 0.2

                # Classify severity
                if score >= 0.85:
                    severity = "critical"
                elif score >= 0.65:
                    severity = "high"
                elif score >= 0.45:
                    severity = "medium"
                else:
                    severity = "low"

                citations = []
                conflicting_resolved = []

                for stmt in conflicting:
                    text = stmt.get("text", "")
                    page = stmt.get("page", 1)

                    # Find best match in group
                    best_idx = -1
                    for idx in group:
                        if text.lower().strip() in documents[idx].lower():
                            best_idx = idx
                            break

                    page_resolved = metadatas[best_idx].get("page_number", page) if best_idx != -1 else page
                    snippet_resolved = documents[best_idx] if best_idx != -1 else text

                    conflicting_resolved.append({
                        "text": text,
                        "page": page_resolved,
                        "documentId": document_id
                    })
                    citations.append({
                        "documentId": document_id,
                        "documentName": doc_name,
                        "pageNumber": page_resolved,
                        "snippet": snippet_resolved[:400],
                        "score": 1.0 if best_idx != -1 else 0.5,
                    })

                finding_id = f"contr-{uuid.uuid4()}"
                resolved.append({
                    "id": finding_id,
                    "type": finding.get("type", "statement"),
                    "severity": severity,
                    "confidence": confidence,
                    "summary": finding.get("summary", "Contradiction detected"),
                    "explanation": finding.get("explanation", ""),
                    "conflictingStatements": conflicting_resolved,
                    "citations": citations
                })

            return resolved

        except Exception as e:
            logger.warning(f"[ContradictionEngine] Failed to parse response: {e}. Content: {content[:150]}")
            return []
