from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from models.workspace import WorkspaceModel
import uuid
from datetime import datetime

class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_workspaces(self, user_id: str) -> list[WorkspaceModel]:
        from models.organization import OrganizationMemberModel
        orgs_subquery = select(OrganizationMemberModel.organization_id).where(OrganizationMemberModel.user_id == user_id)
        query = select(WorkspaceModel).where(
            (WorkspaceModel.user_id == user_id) | 
            (WorkspaceModel.organization_id.in_(orgs_subquery))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_workspace(self, user_id: str, name: str, description: str | None = None, organization_id: str | None = None) -> WorkspaceModel:
        workspace = WorkspaceModel(
            id=f"ws-{uuid.uuid4()}",
            user_id=user_id,
            organization_id=organization_id,
            name=name,
            description=description
        )
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def delete_workspace(self, user_id: str, id: str) -> bool:
        query = select(WorkspaceModel).where(WorkspaceModel.id == id, WorkspaceModel.user_id == user_id)
        result = await self.db.execute(query)
        workspace = result.scalar_one_or_none()
        if workspace:
            await self.db.delete(workspace)
            await self.db.commit()
            return True
        return False

    async def rename_workspace(self, user_id: str, id: str, name: str) -> WorkspaceModel | None:
        query = select(WorkspaceModel).where(WorkspaceModel.id == id, WorkspaceModel.user_id == user_id)
        result = await self.db.execute(query)
        workspace = result.scalar_one_or_none()
        if workspace:
            workspace.name = name
            await self.db.commit()
            await self.db.refresh(workspace)
            return workspace
        return None
