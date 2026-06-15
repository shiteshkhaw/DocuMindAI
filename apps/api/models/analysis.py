from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class DocumentAnalysisModel(Base):
    __tablename__ = "document_analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary_json: Mapped[dict] = mapped_column(JSON, nullable=False)  # includes abstract, keyPoints, suggestedQuestions
    entities_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    kv_pairs_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    entity_conflicts_json: Mapped[list] = mapped_column(JSON, default=list, nullable=True)   # EntityConflict[]
    facts_json: Mapped[list] = mapped_column(JSON, default=list, nullable=True)              # ExtractedFact[]
    semantic_conflicts_json: Mapped[list] = mapped_column(JSON, default=list, nullable=True) # SemanticConflict[]
    ambiguities_json: Mapped[list] = mapped_column(JSON, default=list, nullable=True)
    references_json: Mapped[list] = mapped_column(JSON, default=list, nullable=True)
    requirements_json: Mapped[list] = mapped_column(JSON, default=list, nullable=True)
    trust_score_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)
    executive_summary_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)
    review_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    # lazy="selectin" is required for async SQLAlchemy — prevents MissingGreenlet errors
    document = relationship("DocumentModel", back_populates="analysis", lazy="selectin")
