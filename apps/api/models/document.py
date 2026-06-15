from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class DBNameResolver:
    # Resolve helper
    pass

class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    storage_url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="queued", index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    workspace_id: Mapped[str | None] = mapped_column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    # Ingestion Status Phase 3.4
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    # lazy="selectin" is required for async SQLAlchemy — prevents MissingGreenlet errors
    analysis = relationship("DocumentAnalysisModel", back_populates="document", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    workspace = relationship("WorkspaceModel", back_populates="documents", lazy="selectin")
