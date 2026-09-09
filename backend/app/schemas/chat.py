"""Chat Pydantic schemas."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ChatArtifact(BaseModel):
    """A file the model produced in Code Interpreter mode.

    Downloadable through ``GET /chat/artifacts/{fileId}`` by the owner of the chat session.
    """

    fileId: str
    filename: str


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    createdAt: datetime
    # "context" | "code_interpreter" on assistant rows
    mode: Optional[str] = None
    artifacts: List[ChatArtifact] = []


class ChatSessionOut(BaseModel):
    id: str
    title: str
    documentId: Optional[int] = None
    createdAt: datetime
    messages: List[ChatMessageOut] = []


ChatMode = Literal["auto", "context", "code_interpreter"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    documentId: Optional[int] = None
    sessionId: Optional[str] = None
    # "auto" (default) — fast answer from the document's computed figures, unless the
    # question asks for a file/table/chart or a recalculation "по файлу", which routes it
    # to Code Interpreter; "context" — always the fast path; "code_interpreter" — always
    # let the model run code on the uploaded workbook (requires a document).
    mode: ChatMode = "auto"


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    sessionId: str
    mode: str = "context"  # the mode the answer was actually produced in
    artifacts: List[ChatArtifact] = []


class ChatCapabilities(BaseModel):
    codeInterpreter: bool


def session_to_out(s) -> ChatSessionOut:
    msgs = [
        ChatMessageOut(
            id=m.id,
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            content=m.content,
            createdAt=m.created_at,
            mode=m.mode,
            artifacts=[
                ChatArtifact(fileId=a.file_id, filename=a.filename) for a in (m.artifacts or [])
            ],
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
