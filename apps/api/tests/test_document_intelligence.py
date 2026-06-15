import pytest
from services.ambiguity import AmbiguityDetectionService
from services.reference import ReferenceIntegrityService
from services.requirements import RequirementTraceabilityService
from services.trust_score import TrustScoreV2Service
from services.entity_consistency import EntityConsistencyService

@pytest.mark.asyncio
async def test_ambiguity_detection_service() -> None:
    service = AmbiguityDetectionService()
    chunks = [
        "We should deliver the software soon. Please review promptly.",
        "Normally, the system latency is reasonable under standard load."
    ]
    metadatas = [{"page_number": 1}, {"page_number": 2}]
    
    findings = await service.detect_ambiguities(chunks, metadatas)
    assert len(findings) > 0
    # "soon" and "promptly" are in chunk 0 (Page 1)
    page_1_phrases = [f["phrase"].lower() for f in findings if f["page"] == 1]
    assert "soon" in page_1_phrases
    assert "promptly" in page_1_phrases or "should" in page_1_phrases

@pytest.mark.asyncio
async def test_reference_integrity_service() -> None:
    service = ReferenceIntegrityService()
    # Chunk 0 has a valid reference to Section 3.2 because Section 3.2 is defined in Chunk 1.
    # Chunk 0 also has a broken reference to Section 4.5.
    chunks = [
        "Please look at Section 3.2 for requirements. Also see Section 4.5.",
        "Section 3.2 Setup Guidelines\nThis details the configuration steps."
    ]
    metadatas = [{"page_number": 1}, {"page_number": 2}]
    
    findings = await service.verify_references(chunks, metadatas)
    assert len(findings) == 3
    
    valid_refs = [f for f in findings if f["status"] == "VALID"]
    broken_refs = [f for f in findings if f["status"] == "BROKEN_REFERENCE"]
    
    assert len(valid_refs) == 2
    assert "Section 3.2" in valid_refs[0]["reference"]
    
    assert len(broken_refs) == 1
    assert "Section 4.5" in broken_refs[0]["reference"]

@pytest.mark.asyncio
async def test_requirement_traceability_service() -> None:
    service = RequirementTraceabilityService()
    # REQ-1 is defined (starts a line with a dash/colon) and referenced.
    # REQ-2 is defined but never referenced (Orphaned).
    # REQ-3 is referenced but never defined (Missing).
    chunks = [
        "REQ-1: The server must support TLS 1.3.",
        "REQ-2 - User settings must load within 2 seconds.",
        "To achieve compliance, we must satisfy REQ-1 and also REQ-3."
    ]
    metadatas = [{"page_number": 1}, {"page_number": 2}, {"page_number": 3}]
    
    matrix = await service.generate_matrix(chunks, metadatas)
    assert len(matrix) >= 3
    
    statuses = {r["requirement_id"]: r["status"] for r in matrix}
    assert statuses.get("REQ 1") == "DEFINED"
    assert statuses.get("REQ 2") == "ORPHANED"
    assert statuses.get("REQ 3") == "MISSING"

@pytest.mark.asyncio
async def test_entity_consistency_service_facts() -> None:
    service = EntityConsistencyService()
    facts = [
        {"subject": "Budget", "predicate": "amount", "value": "$50,000", "page": 1, "confidence": 0.9, "evidence": "Budget is $50,000"},
        {"subject": "Budget", "predicate": "amount", "value": "$75,000", "page": 3, "confidence": 0.8, "evidence": "Revised budget is $75,000"}
    ]
    
    conflicts = await service.find_inconsistencies(entities=[], document_id="doc-test", facts=facts)
    assert len(conflicts) == 1
    assert conflicts[0]["entity"] == "Budget"
    assert conflicts[0]["value_a"] == "$50,000"
    assert conflicts[0]["value_b"] == "$75,000"
    assert conflicts[0]["pages"] == [1, 3]

@pytest.mark.asyncio
async def test_trust_score_v2_service() -> None:
    service = TrustScoreV2Service()
    
    # Run scoring on some dummy findings
    score_details = await service.compute_trust_score(
        document_id="doc-test",
        chunks=["We have TODO items here."],
        metadatas=[{"page_number": 1}],
        semantic_conflicts=[{"id": "c1", "summary": "Conflict 1", "severity": "high", "page_a": 1}],
        references=[{"reference": "Section 4", "target": "Section 4", "page": 1, "status": "BROKEN_REFERENCE"}],
        requirements=[{"requirement_id": "REQ-1", "status": "MISSING"}],
        entity_conflicts=[{"entity": "Budget", "value_a": "50k", "value_b": "75k", "pages": [1, 2], "severity": "medium"}],
        ambiguities=[{"phrase": "soon", "category": "Vagueness", "page": 1, "severity": "medium"}]
    )
    
    assert score_details["score"] < 100.0
    assert "breakdown" in score_details
    assert "deductions" in score_details
    assert len(score_details["deductions"]) == 6 # 1 conflict + 1 broken ref + 1 missing req + 1 entity conflict + 1 ambiguity + 1 completeness (TODO)
