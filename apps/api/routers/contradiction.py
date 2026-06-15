from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from db.session import get_db
from orchestration.contradiction import ContradictionOrchestrator
from schemas.contradiction import ContradictionInsightSchema

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
    db: AsyncSession = Depends(get_db)
):
    """
    SSE endpoint to stream contradiction analysis findings dynamically as they are evaluated.
    """
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
    db: AsyncSession = Depends(get_db)
):
    """
    Static REST endpoint to retrieve all contradiction findings for a document.
    """
    orchestrator = ContradictionOrchestrator(db)
    insights = []
    async for event in orchestrator.execute_stream(document_id, model):
        if event["type"] == "insight":
            insights.append(event["insight"])
        elif event["type"] == "error":
            raise HTTPException(status_code=500, detail=event["message"])
    return insights
