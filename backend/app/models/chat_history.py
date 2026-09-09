"""Chat session, message and artifact models."""
import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum as SAEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Новая сессия")
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    # Last Yandex Responses API `response.id`; sent as previous_response_id on the next turn
    # so the model keeps the dialog history.
    last_response_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session",
        cascade="all, delete-orphan", passive_deletes=True,
        order_by="ChatMessage.created_at", lazy="selectin",
    )


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(SAEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # How the assistant answered: "context" (fast path) or "code_interpreter"; None on user rows.
    mode: Mapped[str | None] = mapped_column(String(32), nullable=True)

    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="messages")
    # Files the model produced in Code Interpreter mode (downloadable by the session owner).
    artifacts: Mapped[List["ChatArtifact"]] = relationship(
        "ChatArtifact", back_populates="message",
        cascade="all, delete-orphan", passive_deletes=True, lazy="selectin",
    )


class ChatArtifact(Base, TimestampMixin):
    """A Yandex Files API file created by Code Interpreter for an assistant message.

    Yandex file ids are not tied to a user, so this table is the ownership record for
    downloads: the app serves a file only to the owner of the chat session it was
    produced in.
    """

    __tablename__ = "chat_artifacts"
    __table_args__ = (Index("ix_chat_artifacts_file_id", "file_id"),)

    message_id: Mapped[str] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"), primary_key=True
    )
    file_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)

    message: Mapped[ChatMessage] = relationship("ChatMessage", back_populates="artifacts")
