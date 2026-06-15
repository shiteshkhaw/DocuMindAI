from fastapi import APIRouter, Depends
from schemas.analysis import SearchQuery, SearchResultResponse
from services.dependencies import get_retrieval_service
from retrieval.service import RetrievalService
from routers.auth import get_current_user
from models.auth import UserModel
from observability.rate_limiter import rate_limit

router = APIRouter(prefix="/search", tags=["Search"], dependencies=[Depends(rate_limit("heavy"))])

@router.post("", response_model=list[SearchResultResponse])
async def search_documents(
    query: SearchQuery,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Executes a semantic vector similarity search against the document corpus.
    Generates embedding coordinates on-the-fly and filters by threshold rules.
    """
    retrieval_res = await retrieval_service.retrieve(
        query=query.query,
        document_ids=query.documentIds,
        limit=query.limit,
        min_score=query.minScore,
        user_id=current_user.id
    )
    
    return [
        SearchResultResponse(
            documentId=item.document_id,
            pageNumber=item.page_number,
            text=item.text,
            score=item.score,
            highlightCoordinates=None
        )
        for item in retrieval_res.results
    ]

