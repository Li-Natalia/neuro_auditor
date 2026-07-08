"""Chat Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    createdAt: datetime


class ChatSessionOut(BaseModel):
    id: str
    title: str
    documentId: Optional[int] = None
    createdAt: datetime
    messages: List[ChatMessageOut] = []


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    documentId: Optional[int] = None
    sessionId: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    sessionId: str


def session_to_out(s) -> ChatSessionOut:
    msgs = [
        ChatMessageOut(
            id=m.id,
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            content=m.content,
            createdAt=m.created_at,
        )
        for m in (s.messages or [])
    ]
    return ChatSessionOut(
        id=s.id,
        title=s.title,
        documentId=s.document_id,
        createdAt=s.created_at,
        messages=msgs,
    )
