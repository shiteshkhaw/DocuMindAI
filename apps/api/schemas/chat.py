from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class CitationSchema(BaseModel):
    documentId: str
    documentName: str
    pageNumber: int
    snippet: str
    score: float | None = None

class MessageResponse(BaseModel):
    id: str
    role: str  # user, assistant, system
    content: str
    citations: list[CitationSchema] | None = None
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    documentIds: list[str] = Field(default_factory=list)
    messages: list[MessageResponse] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CreateSessionRequest(BaseModel):
    title: str | None = None
    documentIds: list[str]

class CreateMessageRequest(BaseModel):
    sessionId: str
    content: str
    documentIds: list[str]
    stream: bool = False
    model: str | None = None

