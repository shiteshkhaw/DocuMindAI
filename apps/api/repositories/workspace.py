from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.workspace import WorkspaceModel
from repositories.base import BaseRepository

class WorkspaceRepository(BaseRepository[WorkspaceModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(WorkspaceModel, db)

    async def list_by_user(self, user_id: str) -> list[WorkspaceModel]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
