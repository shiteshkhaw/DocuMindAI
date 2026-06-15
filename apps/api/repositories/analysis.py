from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.analysis import DocumentAnalysisModel
from repositories.base import BaseRepository

class DocumentAnalysisRepository(BaseRepository[DocumentAnalysisModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(DocumentAnalysisModel, db)

    async def get_by_document_id(self, document_id: str) -> DocumentAnalysisModel | None:
        result = await self.db.execute(
            select(self.model).where(self.model.document_id == document_id)
        )
        return result.scalars().first()
