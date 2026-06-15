import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models.audit import AuditLogModel
from sqlalchemy.future import select

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        user_id: str,
        action: str,
        details: str,
        workspace_id: str | None = None,
        organization_id: str | None = None,
        ip_address: str | None = None
    ) -> AuditLogModel:
        log_entry = AuditLogModel(
            id=f"audit-{uuid.uuid4()}",
            user_id=user_id,
            workspace_id=workspace_id,
            organization_id=organization_id,
            action=action,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(log_entry)
        await self.db.commit()
        return log_entry

    async def get_logs_by_workspace(self, workspace_id: str) -> list[AuditLogModel]:
        query = select(AuditLogModel).where(AuditLogModel.workspace_id == workspace_id).order_by(AuditLogModel.timestamp.desc())
        res = await self.db.execute(query)
        return list(res.scalars().all())
