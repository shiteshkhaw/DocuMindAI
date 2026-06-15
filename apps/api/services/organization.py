import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.organization import OrganizationModel, OrganizationMemberModel
from models.workspace import WorkspaceModel

class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, name: str, creator_user_id: str) -> OrganizationModel:
        org_id = f"org-{uuid.uuid4()}"
        org = OrganizationModel(
            id=org_id,
            name=name,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(org)
        await self.db.flush()
        
        # Creator automatically becomes Admin
        member = OrganizationMemberModel(
            id=f"mem-{uuid.uuid4()}",
            organization_id=org_id,
            user_id=creator_user_id,
            role="admin",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def get_user_organizations(self, user_id: str) -> list[OrganizationModel]:
        query = select(OrganizationModel).join(OrganizationMemberModel).where(OrganizationMemberModel.user_id == user_id)
        res = await self.db.execute(query)
        return list(res.scalars().all())

    async def add_member(self, org_id: str, user_id: str, role: str = "member") -> OrganizationMemberModel:
        # Check if already a member
        query = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org_id,
            OrganizationMemberModel.user_id == user_id
        )
        res = await self.db.execute(query)
        existing = res.scalar_one_or_none()
        if existing:
            return existing

        member = OrganizationMemberModel(
            id=f"mem-{uuid.uuid4()}",
            organization_id=org_id,
            user_id=user_id,
            role=role,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(member)
        await self.db.commit()
        return member

    async def update_member_role(self, org_id: str, user_id: str, role: str) -> OrganizationMemberModel | None:
        query = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org_id,
            OrganizationMemberModel.user_id == user_id
        )
        res = await self.db.execute(query)
        member = res.scalar_one_or_none()
        if member:
            member.role = role
            await self.db.commit()
            await self.db.refresh(member)
            return member
        return None

    async def get_members(self, org_id: str) -> list[dict]:
        from models.auth import UserModel
        query = select(OrganizationMemberModel, UserModel).join(UserModel, OrganizationMemberModel.user_id == UserModel.id).where(
            OrganizationMemberModel.organization_id == org_id
        )
        res = await self.db.execute(query)
        rows = res.all()
        return [
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "role": mem.role,
                "joined_at": mem.created_at
            } for mem, user in rows
        ]

    async def get_user_role_for_workspace(self, workspace_id: str, user_id: str) -> str | None:
        """
        Retrieves the user role for a workspace.
        If it's a personal workspace, returns 'admin' if the user is the owner, else None.
        If it belongs to an organization, returns the user's role in that organization.
        """
        query = select(WorkspaceModel).where(WorkspaceModel.id == workspace_id)
        res = await self.db.execute(query)
        workspace = res.scalar_one_or_none()
        if not workspace:
            return None

        # Personal workspace check
        if not workspace.organization_id:
            return "admin" if workspace.user_id == user_id else None

        # Organization membership check
        query = select(OrganizationMemberModel.role).where(
            OrganizationMemberModel.organization_id == workspace.organization_id,
            OrganizationMemberModel.user_id == user_id
        )
        res = await self.db.execute(query)
        return res.scalar_one_or_none()
