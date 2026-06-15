from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import DocumentModel
from repositories.base import BaseRepository

class DocumentRepository(BaseRepository[DocumentModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(DocumentModel, db)

    async def list_by_user_and_workspace(self, user_id: str, workspace_id: str | None = None) -> list[DocumentModel]:
        query = select(self.model).where(self.model.user_id == user_id)
        if workspace_id:
            query = query.where(self.model.workspace_id == workspace_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
