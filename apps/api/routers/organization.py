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
    user_id: str
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
    if not any(org.id == id for org in orgs):
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
        
    member = await org_service.add_member(id, req.user_id, req.role)
    await audit_service.log_action(
        user_id=current_user.id,
        action="member_add",
        details=f"Added member {req.user_id} with role '{req.role}'",
        organization_id=id
    )
    return member

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
