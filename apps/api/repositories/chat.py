from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import ChatSessionModel, MessageModel
from repositories.base import BaseRepository

class ChatSessionRepository(BaseRepository[ChatSessionModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatSessionModel, db)

class MessageRepository(BaseRepository[MessageModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(MessageModel, db)

    async def get_session_messages(self, session_id: str) -> list[MessageModel]:
        result = await self.db.execute(
            select(self.model)
            .where(self.model.session_id == session_id)
            .order_by(self.model.created_at.asc())
        )
        return list(result.scalars().all())
