from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), 
        nullable=False
    )

    members = relationship(
        "OrganizationMemberModel", 
        back_populates="organization", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )


class OrganizationMemberModel(Base):
    __tablename__ = "organization_members"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    organization_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("organizations.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    role: Mapped[str] = mapped_column(String, default="member", nullable=False)  # admin, member, viewer
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), 
        nullable=False
    )

    organization = relationship("OrganizationModel", back_populates="members", lazy="selectin")
