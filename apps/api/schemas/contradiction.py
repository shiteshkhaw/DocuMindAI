from pydantic import BaseModel, Field, ConfigDict

class ConflictingStatementSchema(BaseModel):
    text: str
    page: int
    documentId: str

class CitationSchema(BaseModel):
    documentId: str
    documentName: str
    pageNumber: int
    snippet: str
    score: float | None = None

class ContradictionInsightSchema(BaseModel):
    id: str
    type: str  # timeline, statement, numerical, logical, requirement, entity
    severity: str  # low, medium, high, critical
    confidence: float
    summary: str
    explanation: str
    conflictingStatements: list[ConflictingStatementSchema] = Field(default_factory=list)
    citations: list[CitationSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ContradictionTelemetrySchema(BaseModel):
    retrievalCount: int
    contradictionCount: int
    reasoningLatency: float
    orchestrationLatency: float
    providerLatency: float
