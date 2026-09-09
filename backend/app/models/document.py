"""Financial document model."""
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.analysis import Analysis


class DocumentTemplate(str, enum.Enum):
    IFRS = "IFRS"
    RSBU = "RSBU"


class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    template: Mapped[DocumentTemplate] = mapped_column(
        Enum(DocumentTemplate), nullable=False
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.uploaded, nullable=False
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    processing_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    # Yandex Files API id of the uploaded workbook (Code Interpreter chat mode);
    # uploaded once per document and reused across questions.
    yc_file_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    uploaded_by: Mapped["User"] = relationship("User", back_populates="documents")
    analysis: Mapped["Analysis | None"] = relationship(
        "Analysis", back_populates="document", uselist=False,
        cascade="all, delete-orphan", passive_deletes=True, lazy="selectin",
    )
