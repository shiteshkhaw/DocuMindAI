from pydantic import BaseModel
from datetime import datetime

class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None
    organization_id: str | None = None

class WorkspaceUpdate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    organization_id: str | None = None
