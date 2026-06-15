from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from services.workspace import WorkspaceService
from routers.auth import get_current_user
from models.auth import UserModel

from services.organization import OrganizationService
from services.audit import AuditService
from observability.rate_limiter import rate_limit

router = APIRouter(prefix="/workspaces", tags=["Workspaces"], dependencies=[Depends(rate_limit("standard"))])

@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    service = WorkspaceService(db)
    workspaces = await service.list_workspaces(current_user.id)
    return [
        WorkspaceResponse(
            id=w.id,
            name=w.name,
            description=w.description,
            created_at=w.created_at,
            organization_id=w.organization_id
        ) for w in workspaces
    ]

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(req: WorkspaceCreate, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    # Check if creating under an organization
    if req.organization_id:
        members = await org_service.get_members(req.organization_id)
        user_mem = next((m for m in members if m["user_id"] == current_user.id), None)
        if not user_mem:
            raise HTTPException(status_code=403, detail="Not a member of this organization")
        if user_mem["role"] not in ("admin", "member"):
            raise HTTPException(status_code=403, detail="Viewer role cannot create workspaces")
            
    service = WorkspaceService(db)
    w = await service.create_workspace(current_user.id, req.name, req.description, req.organization_id)
    
    await audit_service.log_action(
        user_id=current_user.id,
        action="workspace_create",
        details=f"Created workspace '{w.name}' under org {w.organization_id or 'personal'}",
        workspace_id=w.id,
        organization_id=w.organization_id
    )
    
    return WorkspaceResponse(
        id=w.id,
        name=w.name,
        description=w.description,
        created_at=w.created_at,
        organization_id=w.organization_id
    )

@router.delete("/{id}")
async def delete_workspace(id: str, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    role = await org_service.get_user_role_for_workspace(id, current_user.id)
    if role is None:
        raise HTTPException(status_code=404, detail="Workspace not found or no access")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only workspace administrators can delete this workspace")
        
    service = WorkspaceService(db)
    success = await service.delete_workspace(current_user.id, id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    await audit_service.log_action(
        user_id=current_user.id,
        action="workspace_delete",
        details=f"Deleted workspace {id}",
        workspace_id=id
    )
    return {"success": True}

@router.patch("/{id}", response_model=WorkspaceResponse)
async def update_workspace(id: str, req: WorkspaceUpdate, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    role = await org_service.get_user_role_for_workspace(id, current_user.id)
    if role is None:
        raise HTTPException(status_code=404, detail="Workspace not found or no access")
    if role not in ("admin", "member"):
        raise HTTPException(status_code=403, detail="View-only members cannot rename workspaces")
        
    service = WorkspaceService(db)
    w = await service.rename_workspace(current_user.id, id, req.name)
    if not w:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    await audit_service.log_action(
        user_id=current_user.id,
        action="workspace_rename",
        details=f"Renamed workspace {id} to '{w.name}'",
        workspace_id=id,
        organization_id=w.organization_id
    )
    
    return WorkspaceResponse(
        id=w.id,
        name=w.name,
        description=w.description,
        created_at=w.created_at,
        organization_id=w.organization_id
    )

@router.get("/{id}/audit")
async def get_workspace_audit_logs(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    audit_service = AuditService(db)
    
    role = await org_service.get_user_role_for_workspace(id, current_user.id)
    if role is None:
        raise HTTPException(status_code=404, detail="Workspace not found or no access")
    if role not in ("admin", "member"):
        raise HTTPException(status_code=403, detail="Viewer role cannot view audit trails")
        
    return await audit_service.get_logs_by_workspace(id)
