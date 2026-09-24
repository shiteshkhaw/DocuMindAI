from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.organization import OrganizationService
from services.audit import AuditService
from routers.auth import get_current_user
from models.auth import UserModel
from pydantic import BaseModel
from observability.rate_limiter import rate_limit

router = APIRouter(prefix="/organizations", tags=["Organizations"], dependencies=[Depends(rate_limit("standard"))])

class OrgCreate(BaseModel):
    name: str

class MemberAdd(BaseModel):
    user_id: str | None = None
    email: str | None = None
    role: str = "member"

class MemberRoleUpdate(BaseModel):
    role: str

@router.post("")
async def create_org(
    req: OrgCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    org = await org_service.create_organization(req.name, current_user.id)
    await audit_service.log_action(
        user_id=current_user.id,
        action="organization_create",
        details=f"Created organization '{org.name}' ({org.id})",
        organization_id=org.id
    )
    return org

@router.get("")
async def list_orgs(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    return await org_service.get_user_organizations(current_user.id)

@router.get("/{id}/members")
async def list_org_members(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    orgs = await org_service.get_user_organizations(current_user.id)
    if not any(org["id"] == id for org in orgs):
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    return await org_service.get_members(id)

@router.post("/{id}/members")
async def add_org_member(
    id: str,
    req: MemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    members = await org_service.get_members(id)
    is_admin = any(m["user_id"] == current_user.id and m["role"] == "admin" for m in members)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only organization admins can add members")
        
    user_id = req.user_id
    if req.email:
        from models.auth import UserModel as AuthUserModel
        from sqlalchemy import select
        query = select(AuthUserModel).where(AuthUserModel.email == req.email.strip())
        res = await db.execute(query)
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email '{req.email}' not found")
        user_id = user.id

    if not user_id:
        raise HTTPException(status_code=400, detail="Must provide user_id or email")

    member = await org_service.add_member(id, user_id, req.role)
    await audit_service.log_action(
        user_id=current_user.id,
        action="member_add",
        details=f"Added member {user_id} with role '{req.role}'",
        organization_id=id
    )
    return member

@router.delete("/{id}")
async def delete_org(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    members = await org_service.get_members(id)
    is_admin = any(m["user_id"] == current_user.id and m["role"] == "admin" for m in members)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only organization admins can delete the organization")
        
    success = await org_service.delete_organization(id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    await audit_service.log_action(
        user_id=current_user.id,
        action="organization_delete",
        details=f"Deleted organization {id}",
        organization_id=id
    )
    return {"success": True}

@router.delete("/{id}/members/{user_id}")
async def remove_org_member(
    id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    members = await org_service.get_members(id)
    is_admin = any(m["user_id"] == current_user.id and m["role"] == "admin" for m in members)
    is_self = (user_id == current_user.id)
    
    if not is_admin and not is_self:
        raise HTTPException(status_code=403, detail="Only organization admins can remove members, or members can remove themselves")
        
    admins = [m for m in members if m["role"] == "admin"]
    if user_id == current_user.id and len(admins) == 1 and len(members) > 1:
        raise HTTPException(status_code=400, detail="Cannot leave organization as you are the only administrator. Please assign another admin first.")

    success = await org_service.remove_member(id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
        
    await audit_service.log_action(
        user_id=current_user.id,
        action="member_remove",
        details=f"Removed member {user_id}",
        organization_id=id
    )
    return {"success": True}

@router.patch("/{id}/members/{user_id}/role")
async def update_member_role(
    id: str,
    user_id: str,
    req: MemberRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    members = await org_service.get_members(id)
    is_admin = any(m["user_id"] == current_user.id and m["role"] == "admin" for m in members)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only organization admins can update roles")
        
    member = await org_service.update_member_role(id, user_id, req.role)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    await audit_service.log_action(
        user_id=current_user.id,
        action="member_role_update",
        details=f"Updated member {user_id} role to '{req.role}'",
        organization_id=id
    )
    return member
