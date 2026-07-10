"""Chat service: answer generation + session/message persistence."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chatbot_model import generate_answer
from app.models.analysis import Analysis
from app.models.chat_history import ChatMessage, ChatSession, MessageRole
from app.models.user import User


def _new_id() -> str:
    return uuid.uuid4().hex


async def _build_context(db: AsyncSession, document_id: int | None, user: User) -> dict:
    if not document_id:
        return {}
    from app.services.analysis_service import get_analysis_by_document

    analysis = await get_analysis_by_document(db, document_id, user)
    if not analysis:
        return {}
    return {
        "balance": analysis.balance_sheet,
        "income": analysis.income_statement,
        "ratios": analysis.ratios,
        "risks": [
            {
                "level": r.level.value if hasattr(r.level, "value") else r.level,
                "title": r.title,
            }
            for r in (analysis.risks or [])
        ],
    }


async def list_sessions(db: AsyncSession, user: User) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.created_at.desc())
    )
    return list(result.scalars().all())


async def get_session(db: AsyncSession, session_id: str, user: User) -> ChatSession | None:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, session_id: str, user: User) -> bool:
    session = await get_session(db, session_id, user)
    if not session:
        return False
    await db.delete(session)
    return True


async def ask(
    db: AsyncSession, user: User, message: str, document_id: int | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    # Validate the document up-front: prevents a FK-violation 500 and stops a
    # user attaching another user's document to their chat session.
    if document_id is not None:
        from fastapi import HTTPException, status

        from app.services.document_service import get_document

        if not await get_document(db, document_id, user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")

    session: ChatSession | None = None
    if session_id:
        session = await get_session(db, session_id, user)
    if not session:
        session = ChatSession(
            id=_new_id(),
            user_id=user.id,
            document_id=document_id,
            title=message[:60],
        )
        db.add(session)
        await db.flush()

    context = await _build_context(db, session.document_id or document_id, user)
    # generate_answer may perform a blocking network call to the LLM provider,
    # so run it off the event loop.
    answer = await run_in_threadpool(generate_answer, message, context)

    db.add(
        ChatMessage(id=_new_id(), session_id=session.id, role=MessageRole.user, content=message)
    )
    db.add(
        ChatMessage(id=_new_id(), session_id=session.id, role=MessageRole.assistant, content=answer)
    )
    await db.flush()
    return {"answer": answer, "sources": [], "sessionId": session.id}
