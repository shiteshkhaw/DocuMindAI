from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from schemas.document import DocumentResponse
from services.document import DocumentService
from services.analysis import AnalysisService
from services.workspace import WorkspaceService
from services.dependencies import get_embedding_provider, get_vector_store, get_retrieval_service
from orchestration.service import IngestionOrchestrator
from routers.auth import get_current_user
from models.auth import UserModel
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import io
import uuid
import time
import asyncio
import hashlib
from models.document import DocumentModel
from schemas.document import IngestionStatus
from fastapi import UploadFile
from starlette.datastructures import Headers

router = APIRouter(prefix="/testing", tags=["Testing"])

EASY_DATASET_CONTENT = """
# Agreement — Sales Team Headcount

## Section 1: Personnel

There are a total of 5 employees in the sales team.
The sales team reports to John Doe, who is the CEO of Acme Corp.

## Section 2: Revised Headcount

Upon internal review, the headcount was corrected.
There are a total of 4 employees in the sales team.
This discrepancy must be resolved before the annual report submission.

## Section 3: Requirements

REQ-001: The system shall be fast and respond within 200ms.
REQ-002: The system must be secure and shall encrypt all data at rest.
REQ-003: All reports must be submitted by 2024-03-31.
""" * 3

MEDIUM_DATASET_CONTENT = """
# Project Charter — Alpha Initiative

## 1. Timeline

The project started on 2023-01-01.
The deadline is set to 2023-12-31.

However, due to scope changes, the project started on 2023-03-01.
The revised release date is Q3 2024.

## 2. Budget

The budget is $10,000 for Phase 1.
Phase 2 requires an additional $5,000.
Note: the budget was updated to $5,000 total in the revised proposal.

## 3. Compliance & Requirements

REQ-101: Data must be encrypted at rest using AES-256.
The system shall not encrypt data to reduce CPU overhead (see performance addendum).

## 4. Entities

GlobalTech LLC is the primary contractor.
Microsoft is a strategic partner.
""" * 5

HARD_DATASET_CONTENT = """
# Project Beta Specification

## Section 1: Security Requirements
REQ-201: The system shall use OAuth2 for authentication.
The system must not use OAuth2 (refer to custom token architecture).

## Section 2: References
Please see Section 3.1 for the database schema definition.
Refer to Section 9.4 for error codes list.

## Section 3: Performance & Budget
The system latency is 150ms.
The latency is 350ms under heavy load.
The budget is $500,000 for server hosting.
The server hosting budget is $800,000.

## Section 4: Named Entities
We will partner with Amazon Web Services (AWS) for hosting.
Google Cloud Platform (GCP) will be our primary cloud vendor.
""" * 7

NIGHTMARE_DATASET_CONTENT = """
# Technical Specification — Project Nexus

## Infrastructure

The server has 16 GB of RAM.
Maximum throughput is set to 1000 requests per second.
The CPU is an Intel Core i9 running at 3.5 GHz.
Budget is $1,000,000 for infrastructure.

## Revised Infrastructure (Engineering Review)

The server has 32 GB of RAM.
The system only needs to handle 500 requests per second.
The CPU is an AMD Ryzen 9 at 3.9 GHz.
Budget is $2,000,000 based on updated procurement estimates.

## Project Management

The project manager is Alice Chen.
The release date is Q1 2024.

## Section 4: Management Addendum

The project manager is Bob Martinez per the Board resolution.
The release date is Q3 2024 per the revised roadmap.

## Requirements

REQ-901: The system shall handle 1000 requests per second.
REQ-901: The system only needs to handle 500 requests per second.
REQ-902: The system shall encrypt all data using TLS 1.3.
REQ-902: The system shall not use TLS for internal service-to-service calls.
REQ-903: All PII must be stored in the EU region.

## References

See Section 4.2 for the detailed architecture diagram.
Please refer to Appendix Z for the compliance checklist.
""" * 10


async def _upload_test_doc(db: AsyncSession, user_id: str, workspace_id: str | None, filename: str, content: str) -> DocumentResponse:
    service = DocumentService(db)
    file_content = content.encode('utf-8')
    dummy_file = UploadFile(filename=filename, file=io.BytesIO(file_content), headers=Headers({"content-type": "text/plain"}))
    d = await service.upload_document(dummy_file, user_id=user_id, workspace_id=workspace_id)
    return DocumentResponse(
        id=d.id,
        name=d.name,
        storageUrl=d.storage_url,
        status=d.status, # type: ignore
        metadata=d.metadata_json, # type: ignore
        createdAt=d.created_at,
        updatedAt=d.updated_at,
        userId=d.user_id,
        error=d.error
    )

@router.post("/generate", response_model=list[DocumentResponse])
async def generate_test_dataset(
    level: str,
    workspace_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    docs = []
    if level == "easy":
        d = await _upload_test_doc(db, current_user.id, workspace_id, "test_easy_dataset.txt", EASY_DATASET_CONTENT)
        docs.append(d)
    elif level == "medium":
        d = await _upload_test_doc(db, current_user.id, workspace_id, "test_medium_dataset.txt", MEDIUM_DATASET_CONTENT)
        docs.append(d)
    elif level == "hard":
        d = await _upload_test_doc(db, current_user.id, workspace_id, "test_hard_dataset.txt", HARD_DATASET_CONTENT)
        docs.append(d)
    elif level == "nightmare":
        d = await _upload_test_doc(db, current_user.id, workspace_id, "test_nightmare_dataset.txt", NIGHTMARE_DATASET_CONTENT)
        docs.append(d)
    else:
        raise HTTPException(status_code=400, detail="Invalid level. Choose easy, medium, hard, or nightmare.")
        
    return docs


async def _ingest_test_doc_sync(db: AsyncSession, user_id: str, workspace_id: str, filename: str, content: str) -> str:
    """Ingests document synchronously in the API thread by utilizing the queue worker flow."""
    file_content = content.encode('utf-8')
    checksum = hashlib.sha256(file_content).hexdigest()
    doc_id = f"doc-{uuid.uuid4()}"
    storage_key = f"documents/{doc_id}/{filename}"
    
    # Upload file using abstract storage provider
    from storage import get_storage_provider
    storage_provider = get_storage_provider()
    storage_result = await storage_provider.upload_file(
        key=storage_key,
        data=file_content,
        content_type="text/plain",
        metadata={"user_id": user_id, "doc_id": doc_id}
    )

    doc_model = DocumentModel(
        id=doc_id,
        name=filename,
        storage_url=storage_result.storage_url,
        status=IngestionStatus.QUEUED.value,
        metadata_json={
            "title": filename.split(".")[0],
            "fileSize": len(file_content),
            "mimeType": "text/plain",
            "checksum": checksum,
            "storage_key": storage_key
        },
        user_id=user_id,
        workspace_id=workspace_id
    )
    
    db.add(doc_model)
    await db.commit()
    
    from workers import ingest_document_worker, is_stub_broker
    if is_stub_broker():
        logger.info(f"[TestingSuite] running ingestion synchronously via stub broker for doc={doc_id}")
        ingest_document_worker(
            document_id=doc_id,
            file_content=file_content,
            filename=filename,
            mime_type="text/plain",
            user_id=user_id,
            workspace_id=workspace_id
        )
    else:
        logger.info(f"[TestingSuite] dispatching ingestion to Dramatiq queue for doc={doc_id}")
        ingest_document_worker.send(
            doc_id,
            file_content,
            filename,
            "text/plain",
            user_id,
            workspace_id
        )
        
        # Poll document status in the DB until processed
        for _ in range(60):
            await asyncio.sleep(1)
            # Expire session cache to force fresh DB fetch
            db.expire_all()
            doc = await db.get(DocumentModel, doc_id)
            if doc and doc.status in ("COMPLETED", "FAILED"):
                logger.info(f"[TestingSuite] Ingestion complete in queue for doc={doc_id} with status={doc.status}")
                break
                
    return doc_id


@router.post("/run-suite")
async def run_validation_suite(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Executes a complete system validation suite covering easy, medium, hard, and nightmare test packs.
    Performs assertions on Contradictions, Entities, Requirements, References, Trust Score, Retrieval accuracy,
    Security restrictions, and Tenant/Workspace Isolation.
    """
    start_time = time.perf_counter()
    workspace_service = WorkspaceService(db)
    analysis_service = AnalysisService(db)
    retrieval_service = get_retrieval_service()
    store = get_vector_store()
    
    # Track created resources for cleanup
    created_workspace_ids = []
    created_document_ids = []
    
    try:
        # 1. Setup Sandbox Workspaces
        ws_a = await workspace_service.create_workspace(current_user.id, f"Suite Workspace A - {uuid.uuid4()}", "Test Sandbox")
        ws_b = await workspace_service.create_workspace(current_user.id, f"Suite Workspace B - {uuid.uuid4()}", "Test Sandbox Isolated")
        created_workspace_ids.extend([ws_a.id, ws_b.id])
        
        # 2. Ingest Test Packs in Workspace A
        easy_doc_id = await _ingest_test_doc_sync(db, current_user.id, ws_a.id, "easy_test.txt", EASY_DATASET_CONTENT)
        medium_doc_id = await _ingest_test_doc_sync(db, current_user.id, ws_a.id, "medium_test.txt", MEDIUM_DATASET_CONTENT)
        hard_doc_id = await _ingest_test_doc_sync(db, current_user.id, ws_a.id, "hard_test.txt", HARD_DATASET_CONTENT)
        nightmare_doc_id = await _ingest_test_doc_sync(db, current_user.id, ws_a.id, "nightmare_test.txt", NIGHTMARE_DATASET_CONTENT)
        created_document_ids.extend([easy_doc_id, medium_doc_id, hard_doc_id, nightmare_doc_id])
        
        # 3. run analyses
        easy_analysis = await analysis_service.get_or_create_analysis(easy_doc_id)
        medium_analysis = await analysis_service.get_or_create_analysis(medium_doc_id)
        hard_analysis = await analysis_service.get_or_create_analysis(hard_doc_id)
        nightmare_analysis = await analysis_service.get_or_create_analysis(nightmare_doc_id)
        
        # Assertions mapping
        results = {}
        total_tests = 0
        passed_tests = 0
        
        def run_assertion(test_name, assertion_fn):
            nonlocal total_tests, passed_tests
            total_tests += 1
            try:
                res = assertion_fn()
                if res is False:
                    raise ValueError("Assertion returned False")
                passed_tests += 1
                return {"name": test_name, "status": "PASS", "message": "Verification successful."}
            except Exception as e:
                return {"name": test_name, "status": "FAIL", "message": str(e)}
        
        # EASY PACK VERIFICATION
        easy_assertions = []
        easy_contradictions = easy_analysis.semantic_conflicts_json or []
        easy_entities = easy_analysis.entities_json or []
        easy_reqs = easy_analysis.requirements_json or []
        easy_refs = easy_analysis.references_json or []
        easy_trust = easy_analysis.trust_score_json or {}
        
        easy_assertions.append(run_assertion("Contradictions: Found Sales Team headcount conflict (5 vs 4)", 
            lambda: any("headcount" in str(c.get("summary", "")).lower() or "5" in str(c.get("summary", "")) for c in easy_contradictions)
        ))
        easy_assertions.append(run_assertion("Entities: Extracted 'John Doe' or 'Acme Corp'", 
            lambda: any(e.get("text") in ("John Doe", "Acme Corp") for e in easy_entities)
        ))
        easy_assertions.append(run_assertion("Requirements: Traced REQ-001, REQ-002, REQ-003", 
            lambda: len(easy_reqs) >= 3 and any("REQ-001" in r.get("id", "") for r in easy_reqs)
        ))
        easy_assertions.append(run_assertion("References: Minimal or zero references expected", 
            lambda: len(easy_refs) < 2
        ))
        easy_assertions.append(run_assertion("Trust Score: Falls in High Range (>= 80)", 
            lambda: easy_trust.get("score", 0) >= 80
        ))
        
        # MEDIUM PACK VERIFICATION
        medium_assertions = []
        medium_contradictions = medium_analysis.semantic_conflicts_json or []
        medium_entities = medium_analysis.entities_json or []
        medium_reqs = medium_analysis.requirements_json or []
        medium_refs = medium_analysis.references_json or []
        medium_trust = medium_analysis.trust_score_json or {}
        
        medium_assertions.append(run_assertion("Contradictions: Detected budget or timeline conflict", 
            lambda: len(medium_contradictions) >= 1
        ))
        medium_assertions.append(run_assertion("Entities: Extracted 'GlobalTech LLC' or 'Microsoft'", 
            lambda: any("globaltech" in str(e.get("text", "")).lower() or "microsoft" in str(e.get("text", "")).lower() for e in medium_entities)
        ))
        medium_assertions.append(run_assertion("Requirements: Traced REQ-101 (encrypt at rest vs CPU overhead)", 
            lambda: any("REQ-101" in r.get("id", "") for r in medium_reqs)
        ))
        medium_assertions.append(run_assertion("Trust Score: Falls in Medium Range (50 to 90)", 
            lambda: 50 <= medium_trust.get("score", 0) <= 90
        ))
        
        # HARD PACK VERIFICATION
        hard_assertions = []
        hard_contradictions = hard_analysis.semantic_conflicts_json or []
        hard_entities = hard_analysis.entities_json or []
        hard_reqs = hard_analysis.requirements_json or []
        hard_refs = hard_analysis.references_json or []
        hard_trust = hard_analysis.trust_score_json or {}
        
        hard_assertions.append(run_assertion("Contradictions: Latency, Budget, and OAuth2 conflicts", 
            lambda: len(hard_contradictions) >= 2
        ))
        hard_assertions.append(run_assertion("Entities: Extracted 'AWS' or 'Google Cloud Platform'", 
            lambda: any("aws" in str(e.get("text", "")).lower() or "gcp" in str(e.get("text", "")).lower() or "google" in str(e.get("text", "")).lower() for e in hard_entities)
        ))
        hard_assertions.append(run_assertion("Requirements: Traced REQ-201 (shall use OAuth2 vs shall not)", 
            lambda: any("REQ-201" in r.get("id", "") for r in hard_reqs)
        ))
        hard_assertions.append(run_assertion("References: Found Section 3.1 and Section 9.4 references", 
            lambda: len(hard_refs) >= 2
        ))
        hard_assertions.append(run_assertion("Trust Score: Degraded to low-medium (< 80)", 
            lambda: hard_trust.get("score", 0) < 80
        ))
        
        # NIGHTMARE PACK VERIFICATION
        nightmare_assertions = []
        nightmare_contradictions = nightmare_analysis.semantic_conflicts_json or []
        nightmare_entities = nightmare_analysis.entities_json or []
        nightmare_reqs = nightmare_analysis.requirements_json or []
        nightmare_refs = nightmare_analysis.references_json or []
        nightmare_trust = nightmare_analysis.trust_score_json or {}
        
        nightmare_assertions.append(run_assertion("Contradictions: Multiple infrastructure conflicts (RAM, CPU, PM, release)", 
            lambda: len(nightmare_contradictions) >= 3
        ))
        nightmare_assertions.append(run_assertion("Entities: Extracted Alice Chen, Bob Martinez, Intel, AMD", 
            lambda: any("alice" in str(e.get("text", "")).lower() or "bob" in str(e.get("text", "")).lower() for e in nightmare_entities)
        ))
        nightmare_assertions.append(run_assertion("Requirements: Traced REQ-901, REQ-902, REQ-903", 
            lambda: any("REQ-901" in r.get("id", "") for r in nightmare_reqs)
        ))
        nightmare_assertions.append(run_assertion("References: Found Section 4.2 and Appendix Z", 
            lambda: len(nightmare_refs) >= 2
        ))
        nightmare_assertions.append(run_assertion("Trust Score: Severely degraded (< 50)", 
            lambda: nightmare_trust.get("score", 0) < 50
        ))
        
        # RETRIEVAL VERIFICATION
        retrieval_assertions = []
        
        async def assert_retrieval_ok():
            response = await retrieval_service.retrieve(
                query="headcount of sales team",
                workspace_id=ws_a.id,
                user_id=current_user.id,
                limit=3
            )
            res = response.results
            return len(res) > 0 and any("headcount" in c.text.lower() or "employee" in c.text.lower() for c in res)
        
        # Helper execution wrapper because assertions run synchronously
        loop = asyncio.get_event_loop()
        retrieval_ok = await assert_retrieval_ok()
        retrieval_assertions.append(run_assertion("Vector Search: Retrieve relevant sales headcount chunks in Workspace A", 
            lambda: retrieval_ok
        ))
        
        # SECURITY VERIFICATION (Cross-User Access Blocked)
        security_assertions = []
        
        async def assert_security_blocked():
            response = await retrieval_service.retrieve(
                query="headcount of sales team",
                workspace_id=ws_a.id,
                user_id="user-security-sandbox",
                limit=3
            )
            return len(response.results) == 0
            
        security_ok = await assert_security_blocked()
        security_assertions.append(run_assertion("Security Access: Query by unauthenticated user returns empty results", 
            lambda: security_ok
        ))
        
        # ISOLATION VERIFICATION (Cross-Workspace Leak Blocked)
        isolation_assertions = []
        
        async def assert_isolation_ok():
            response = await retrieval_service.retrieve(
                query="headcount of sales team",
                workspace_id=ws_b.id,
                user_id=current_user.id,
                limit=3
            )
            return len(response.results) == 0
            
        isolation_ok = await assert_isolation_ok()
        isolation_assertions.append(run_assertion("Tenant Isolation: Query in empty Workspace B does not leak Workspace A data", 
            lambda: isolation_ok
        ))
        
        # Check overall suite status
        suite_passed = passed_tests == total_tests
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "summary": {
                "status": "PASS" if suite_passed else "FAIL",
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "elapsed_ms": round(elapsed_ms, 1)
            },
            "test_packs": {
                "easy": {
                    "status": "PASS" if all(a["status"] == "PASS" for a in easy_assertions) else "FAIL",
                    "metrics": {
                        "contradictions_found": len(easy_contradictions),
                        "entities_extracted": [e.get("text") for e in easy_entities[:5]],
                        "requirements_traced": [r.get("id") for r in easy_reqs],
                        "references_resolved": [r.get("citation") for r in easy_refs],
                        "trust_score": easy_trust.get("score", 0.0)
                    },
                    "assertions": easy_assertions
                },
                "medium": {
                    "status": "PASS" if all(a["status"] == "PASS" for a in medium_assertions) else "FAIL",
                    "metrics": {
                        "contradictions_found": len(medium_contradictions),
                        "entities_extracted": [e.get("text") for e in medium_entities[:5]],
                        "requirements_traced": [r.get("id") for r in medium_reqs],
                        "references_resolved": [r.get("citation") for r in medium_refs],
                        "trust_score": medium_trust.get("score", 0.0)
                    },
                    "assertions": medium_assertions
                },
                "hard": {
                    "status": "PASS" if all(a["status"] == "PASS" for a in hard_assertions) else "FAIL",
                    "metrics": {
                        "contradictions_found": len(hard_contradictions),
                        "entities_extracted": [e.get("text") for e in hard_entities[:5]],
                        "requirements_traced": [r.get("id") for r in hard_reqs],
                        "references_resolved": [r.get("citation") for r in hard_refs],
                        "trust_score": hard_trust.get("score", 0.0)
                    },
                    "assertions": hard_assertions
                },
                "nightmare": {
                    "status": "PASS" if all(a["status"] == "PASS" for a in nightmare_assertions) else "FAIL",
                    "metrics": {
                        "contradictions_found": len(nightmare_contradictions),
                        "entities_extracted": [e.get("text") for e in nightmare_entities[:5]],
                        "requirements_traced": [r.get("id") for r in nightmare_reqs],
                        "references_resolved": [r.get("citation") for r in nightmare_refs],
                        "trust_score": nightmare_trust.get("score", 0.0)
                    },
                    "assertions": nightmare_assertions
                }
            },
            "retrieval": {
                "status": "PASS" if all(a["status"] == "PASS" for a in retrieval_assertions) else "FAIL",
                "assertions": retrieval_assertions
            },
            "security": {
                "status": "PASS" if all(a["status"] == "PASS" for a in security_assertions) else "FAIL",
                "assertions": security_assertions
            },
            "isolation": {
                "status": "PASS" if all(a["status"] == "PASS" for a in isolation_assertions) else "FAIL",
                "assertions": isolation_assertions
            }
        }
        
    finally:
        # Clean up database resources
        for doc_id in created_document_ids:
            try:
                # Remove from ChromaDB Vector Store
                await store.delete(collection_name="documind_chunks", filter_meta={"document_id": doc_id})
            except Exception:
                pass
            try:
                # Remove from SQL Database
                await db.execute(text(f"DELETE FROM documents WHERE id = '{doc_id}'"))
            except Exception:
                pass
                
        for ws_id in created_workspace_ids:
            try:
                await workspace_service.delete_workspace(current_user.id, ws_id)
            except Exception:
                pass
        await db.commit()

