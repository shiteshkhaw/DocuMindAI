from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EntityMention(BaseModel):
    page: int
    snippet: str


class EntitySchema(BaseModel):
    id: str
    type: str
    text: str
    confidence: float
    mentions: list[EntityMention] = Field(default_factory=list)
    frequency: int = 1
    related_entities: list[str] = Field(default_factory=list)
    boundingBox: list[float] | None = None


class EntityConflict(BaseModel):
    entity_type: str
    values: list[str]
    pages: list[int]
    description: str


class KeyValuePairSchema(BaseModel):
    id: str
    key: str
    value: str
    confidence: float


class DocumentSummarySchema(BaseModel):
    abstract: str
    keyPoints: list[str] = Field(default_factory=list)
    suggestedQuestions: list[str] = Field(default_factory=list)


# ── Phase 2: Fact Extraction ──────────────────────────────────────────────────

class FactEvidenceSpan(BaseModel):
    """Verbatim text span from the document that supports the fact."""
    text: str
    page: int
    chunk_index: int = 0


class FactSchema(BaseModel):
    """A discrete, verifiable claim extracted from the document."""
    id: str
    subject: str         # Who or what the fact is about
    predicate: str       # The relationship or property
    value: str           # The value, object, or target
    confidence: float    # 0.0-1.0 extraction confidence
    type: str            # numerical | temporal | definitional | relational | requirement
    evidence: str        # Verbatim text span
    page: int = 0        # Primary page of occurrence
    chunk_id: str | None = None


# ── Phase 2: Entity Consistency ───────────────────────────────────────────────

class EntityInconsistency(BaseModel):
    """A specific inconsistency found for a given entity across the document."""
    entity_text: str
    entity_type: str
    attribute: str       # Which attribute is conflicting (e.g. "role", "value", "name")
    conflicting_values: list[str]
    pages: list[int]
    severity: str        # low | medium | high | critical
    description: str
    confidence: float


# ── Phase 2: Semantic Conflict Discovery ─────────────────────────────────────

class SemanticConflictSchema(BaseModel):
    """A semantic-level contradiction discovered via embedding distance analysis."""
    id: str
    statement_a: str
    statement_b: str
    page_a: int
    page_b: int
    semantic_distance: float  # 0.0 (identical) to 1.0 (maximally distant)
    conflict_score: float     # composite risk score 0.0-1.0
    severity: str             # low | medium | high | critical
    conflict_type: str        # numerical | temporal | definitional | relational | logical
    explanation: str
    confidence: float


# ── Full Analysis Response ────────────────────────────────────────────────────

class DocumentAnalysisResponse(BaseModel):
    documentId: str
    summary: DocumentSummarySchema
    entities: list[EntitySchema] = Field(default_factory=list)
    keyValuePairs: list[KeyValuePairSchema] = Field(default_factory=list)
    entityConflicts: list[EntityConflict] = Field(default_factory=list)
    facts: list[FactSchema] = Field(default_factory=list)
    entityInconsistencies: list[EntityInconsistency] = Field(default_factory=list)
    semanticConflicts: list[SemanticConflictSchema] = Field(default_factory=list)
    analyzedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchQuery(BaseModel):
    query: str
    documentIds: list[str] | None = None
    limit: int = 5
    minScore: float = 0.5


class SearchResultResponse(BaseModel):
    documentId: str
    pageNumber: int
    text: str
    score: float
    highlightCoordinates: list[list[float]] | None = None
