from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from db.session import get_db
from orchestration.contradiction import ContradictionOrchestrator
from schemas.contradiction import ContradictionInsightSchema
from routers.auth import get_current_user
from models.auth import UserModel
from services.document import DocumentService

router = APIRouter(tags=["Contradictions"])

async def event_generator(document_id: str, model: str, db: AsyncSession):
    orchestrator = ContradictionOrchestrator(db)
    try:
        async for event in orchestrator.execute_stream(document_id, model):
            yield f"data: {json.dumps(event)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    yield "data: [DONE]\n\n"

@router.get("/documents/{document_id}/contradictions/stream")
async def stream_contradictions(
    document_id: str,
    model: str = "documind-v3",
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    SSE endpoint to stream contradiction analysis findings dynamically as they are evaluated.
    Secured with authentication and document ownership validation.
    """
    doc_service = DocumentService(db)
    doc = await doc_service.get_document(document_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or access denied")
        
    return StreamingResponse(
        event_generator(document_id, model, db),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
        }
    )

@router.get("/documents/{document_id}/contradictions", response_model=list[ContradictionInsightSchema])
async def get_contradictions(
    document_id: str,
    model: str = "documind-v3",
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Static REST endpoint to retrieve all contradiction findings for a document.
    Secured with authentication and document ownership validation.
    """
    doc_service = DocumentService(db)
    doc = await doc_service.get_document(document_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or access denied")
        
    orchestrator = ContradictionOrchestrator(db)
    insights = []
    async for event in orchestrator.execute_stream(document_id, model):
        if event["type"] == "insight":
            insights.append(event["insight"])
        elif event["type"] == "error":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=event["message"])
    return insights
