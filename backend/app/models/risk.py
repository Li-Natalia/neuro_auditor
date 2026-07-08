"""Risk model (entries linked to an analysis)."""
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis


class RiskLevel(str, enum.Enum):
    critical = "critical"
    medium = "medium"
    low = "low"


class Risk(Base, TimestampMixin):
    __tablename__ = "risks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), nullable=False)
    level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    metric: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="risks")
