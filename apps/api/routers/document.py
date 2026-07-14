from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.document import DocumentService
from services.analysis import AnalysisService
from schemas.document import DocumentResponse
from schemas.analysis import DocumentAnalysisResponse
from routers.auth import get_current_user
from models.auth import UserModel

router = APIRouter(prefix="/documents", tags=["Documents"])


async def _get_owned_document(id: str, db: AsyncSession, current_user: UserModel):
    """Fetch document and assert ownership — raises 404 if not found or not owned."""
    service = DocumentService(db)
    d = await service.get_document(id)
    if not d or d.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return d

@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    workspace_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = DocumentService(db)
    docs = await service.list_documents(user_id=current_user.id, workspace_id=workspace_id)
    # Format schemas compatible with frontend
    return [
        DocumentResponse(
            id=d.id,
            name=d.name,
            storageUrl=d.storage_url,
            status=d.status,  # type: ignore
            metadata=d.metadata_json,  # type: ignore
            createdAt=d.created_at,
            updatedAt=d.updated_at,
            userId=d.user_id,
            error=d.error
        ) for d in docs
    ]

@router.get("/{id}", response_model=DocumentResponse)
async def get_document(
    id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = DocumentService(db)
    d = await service.get_document(id)
    if not d or d.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=d.id,
        name=d.name,
        storageUrl=d.storage_url,
        status=d.status,  # type: ignore
        metadata=d.metadata_json,  # type: ignore
        createdAt=d.created_at,
        updatedAt=d.updated_at,
        userId=d.user_id,
        error=d.error
    )

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...), 
    workspace_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if workspace_id:
        from services.organization import OrganizationService
        org_service = OrganizationService(db)
        role = await org_service.get_user_role_for_workspace(workspace_id, current_user.id)
        if role is None or role == "viewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace access denied or insufficient permissions."
            )
            
    service = DocumentService(db)
    try:
        d = await service.upload_document(file, user_id=current_user.id, workspace_id=workspace_id)
        return DocumentResponse(
            id=d.id,
            name=d.name,
            storageUrl=d.storage_url,
            status=d.status,  # type: ignore
            metadata=d.metadata_json,  # type: ignore
            createdAt=d.created_at,
            updatedAt=d.updated_at,
            userId=d.user_id,
            error=d.error
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def delete_document(
    id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = DocumentService(db)
    d = await service.get_document(id)
    if not d or d.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    success = await service.delete_document(id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True}

from schemas.analysis import (
    DocumentAnalysisResponse,
    EntityMention,
    EntitySchema,
    KeyValuePairSchema,
    EntityConflict,
    FactSchema,
    EntityInconsistency,
    SemanticConflictSchema,
    DocumentSummarySchema
)
import uuid

@router.get("/{id}/analysis", response_model=DocumentAnalysisResponse)
async def get_document_analysis(
    id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    doc_service = DocumentService(db)
    d = await doc_service.get_document(id)
    if not d or d.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)

    # 1. Map Summary Schema
    raw_summary = a.summary_json or {}
    summary = DocumentSummarySchema(
        abstract=raw_summary.get("abstract") or "",
        keyPoints=raw_summary.get("keyPoints") or [],
        suggestedQuestions=raw_summary.get("suggestedQuestions") or []
    )

    # 2. Map Key-Value Pairs
    raw_kv = a.kv_pairs_json or []
    keyValuePairs = []
    for kv in raw_kv:
        if isinstance(kv, dict):
            try:
                conf = float(kv.get("confidence") if kv.get("confidence") is not None else 1.0)
            except Exception:
                conf = 1.0
            keyValuePairs.append(
                KeyValuePairSchema(
                    id=kv.get("id") or f"kv-{uuid.uuid4()}",
                    key=kv.get("key") or "key",
                    value=kv.get("value") or "value",
                    confidence=conf
                )
            )

    # 3. Map Entities
    raw_entities = a.entities_json or []
    entities = []
    for ent in raw_entities:
        if isinstance(ent, dict):
            try:
                conf = float(ent.get("confidence") if ent.get("confidence") is not None else 1.0)
            except Exception:
                conf = 1.0
            mentions = []
            for m in ent.get("mentions") or []:
                if isinstance(m, dict):
                    mentions.append(
                        EntityMention(
                            page=m.get("page") or 1,
                            snippet=m.get("snippet") or ""
                        )
                    )
            entities.append(
                EntitySchema(
                    id=ent.get("id") or f"ent-{uuid.uuid4()}",
                    type=ent.get("type") or "ENTITY",
                    text=ent.get("text") or "entity",
                    confidence=conf,
                    mentions=mentions,
                    frequency=ent.get("frequency") or len(mentions) or 1,
                    related_entities=ent.get("related_entities") or [],
                    boundingBox=ent.get("boundingBox")
                )
            )

    # 4. Map Facts
    raw_facts = a.facts_json or []
    facts = []
    for f in raw_facts:
        if isinstance(f, dict):
            try:
                conf = float(f.get("confidence") if f.get("confidence") is not None else 1.0)
            except Exception:
                conf = 1.0
            facts.append(
                FactSchema(
                    id=f.get("id") or f"fact-{uuid.uuid4()}",
                    subject=f.get("subject") or "subject",
                    predicate=f.get("predicate") or "predicate",
                    value=f.get("value") or f.get("object_value") or "value",
                    confidence=conf,
                    type=f.get("type") or "definitional",
                    evidence=f.get("evidence") or "",
                    page=f.get("page") or 1,
                    chunk_id=f.get("chunk_id")
                )
            )

    # 5. Map Entity Conflicts (converting legacy inconsistency structure)
    raw_conflicts = getattr(a, "entity_conflicts_json", None) or []
    entityConflicts = []
    for c in raw_conflicts:
        if isinstance(c, dict):
            e_type = c.get("entity_type") or c.get("entity") or "ENTITY"
            vals = c.get("values") or [c.get("value_a", ""), c.get("value_b", "")]
            pages = c.get("pages") or []
            desc = c.get("description") or c.get("evidence") or ""
            entityConflicts.append(
                EntityConflict(
                    entity_type=e_type,
                    values=vals,
                    pages=pages,
                    description=desc
                )
            )

    # 6. Map Entity Inconsistencies
    entityInconsistencies = []
    for c in raw_conflicts:
        if isinstance(c, dict):
            entityInconsistencies.append(
                EntityInconsistency(
                    entity_text=c.get("entity") or c.get("entity_text") or "Entity",
                    entity_type=c.get("entity_type") or "ENTITY",
                    attribute=c.get("attribute") or "attribute",
                    conflicting_values=c.get("values") or [c.get("value_a", ""), c.get("value_b", "")],
                    pages=c.get("pages") or [],
                    severity=c.get("severity") or "medium",
                    description=c.get("description") or c.get("evidence") or "",
                    confidence=c.get("confidence") or 0.8
                )
            )

    # 7. Map Semantic Conflicts
    raw_conflicts_sem = getattr(a, "semantic_conflicts_json", None) or []
    semanticConflicts = []
    for c in raw_conflicts_sem:
        if isinstance(c, dict):
            try:
                dist = float(c.get("semantic_distance") if c.get("semantic_distance") is not None else 0.5)
            except Exception:
                dist = 0.5
            try:
                score = float(c.get("conflict_score") if c.get("conflict_score") is not None else 0.5)
            except Exception:
                score = 0.5
            try:
                conf = float(c.get("confidence") if c.get("confidence") is not None else 1.0)
            except Exception:
                conf = 1.0
            semanticConflicts.append(
                SemanticConflictSchema(
                    id=c.get("id") or f"sem-{uuid.uuid4()}",
                    statement_a=c.get("statement_a") or "statement a",
                    statement_b=c.get("statement_b") or "statement b",
                    page_a=c.get("page_a") or 1,
                    page_b=c.get("page_b") or 1,
                    semantic_distance=dist,
                    conflict_score=score,
                    severity=c.get("severity") or "medium",
                    conflict_type=c.get("conflict_type") or "logical",
                    explanation=c.get("explanation") or "",
                    confidence=conf
                )
            )

    return DocumentAnalysisResponse(
        documentId=a.document_id,
        summary=summary,
        entities=entities,
        keyValuePairs=keyValuePairs,
        entityConflicts=entityConflicts,
        facts=facts,
        entityInconsistencies=entityInconsistencies,
        semanticConflicts=semanticConflicts,
        analyzedAt=a.analyzed_at
    )



@router.get("/{id}/facts")
async def get_document_facts(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "facts_json", []) or []


@router.get("/{id}/entity-conflicts")
async def get_document_entity_conflicts(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "entity_conflicts_json", []) or []


@router.get("/{id}/ambiguities")
async def get_document_ambiguities(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "ambiguities_json", []) or []


@router.get("/{id}/references")
async def get_document_references(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "references_json", []) or []


@router.get("/{id}/requirements")
async def get_document_requirements(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "requirements_json", []) or []


@router.get("/{id}/trust-score")
async def get_document_trust_score(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "trust_score_json", {}) or {}


@router.get("/{id}/executive-summary")
async def get_document_executive_summary(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "executive_summary_json", {}) or {}


@router.get("/{id}/review")
async def get_document_review(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    await _get_owned_document(id, db, current_user)
    analysis_service = AnalysisService(db)
    a = await analysis_service.get_or_create_analysis(id)
    return getattr(a, "review_json", {}) or {}
