"""Chat routes."""
import mimetypes
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.yandex_client import code_interpreter_enabled
from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatCapabilities,
    ChatRequest,
    ChatResponse,
    ChatSessionOut,
    session_to_out,
)
from app.services import chat_service
from app.utils.http import content_disposition

router = APIRouter()


@router.get("/artifacts/{file_id}")
async def download_artifact(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a file produced by Code Interpreter (only for the owner of the chat session)."""
    data, filename = await chat_service.download_artifact(db, file_id, current_user)
    media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return StreamingResponse(
        BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": content_disposition(filename)},
    )


@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await chat_service.ask(
        db, current_user, data.message, data.documentId, data.sessionId, mode=data.mode
    )
    return ChatResponse(**result)


@router.get("/capabilities", response_model=ChatCapabilities)
async def capabilities(current_user: User = Depends(get_current_user)):
    """Which optional chat modes the server has enabled (drives the UI toggle)."""
    return ChatCapabilities(codeInterpreter=code_interpreter_enabled())


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    sessions = await chat_service.list_sessions(db, current_user)
    return [session_to_out(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = await chat_service.get_session(db, session_id, current_user)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    return session_to_out(s)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await chat_service.delete_session(db, session_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
