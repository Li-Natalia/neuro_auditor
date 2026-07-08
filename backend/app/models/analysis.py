"""Financial analysis result model (stores parsed figures + ratios + risks)."""
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.risk import Risk


class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)

    balance_sheet: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    income_statement: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    cash_flow_statement: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    ratios: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")

    document: Mapped["Document"] = relationship("Document", back_populates="analysis")
    risks: Mapped[list["Risk"]] = relationship(
        "Risk", back_populates="analysis", cascade="all, delete-orphan", lazy="selectin"
    )
