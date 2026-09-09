"""Chat service: answer generation + session/message persistence."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chatbot_model import (
    CI_DISABLED_MESSAGE,
    ERROR_MESSAGE,
    ChatReply,
    FileUnavailableError,
    generate_answer,
)
from app.ai.mode_router import wants_code_interpreter
from app.ai.yandex_client import code_interpreter_enabled, get_yandex_client, yandex_configured
from app.core.config import settings
from app.models.chat_history import ChatArtifact, ChatMessage, ChatSession, MessageRole
from app.models.document import Document
from app.models.user import User

logger = logging.getLogger("fin-auditor")


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
    file_ids = [a.file_id for m in (session.messages or []) for a in (m.artifacts or [])]
    await db.delete(session)
    if file_ids and yandex_configured():
        # best-effort cleanup of the Code Interpreter outputs on the Yandex side
        client = get_yandex_client()
        for file_id in file_ids:
            await run_in_threadpool(client.delete_file, file_id)
    return True


# --------------------------------------------------------------- Code Interpreter

async def _ensure_yc_file(db: AsyncSession, doc: Document) -> str | None:
    """Upload the document's workbook to the Yandex Files API once and cache the id.

    Tries the configured ``purpose`` first and falls back to ``assistants`` (both are
    valid for Code Interpreter containers). Returns None if the upload fails.
    """
    if doc.yc_file_id:
        return doc.yc_file_id

    client = get_yandex_client()
    purposes = [settings.AI_CI_FILE_PURPOSE]
    if "assistants" not in purposes:
        purposes.append("assistants")
    for purpose in purposes:
        try:
            file_id = await run_in_threadpool(
                client.upload_file,
                doc.file_path,
                purpose=purpose,
                filename=doc.original_filename,  # the name the model sees in the container
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Files API: загрузка (purpose=%s) не удалась: %s", purpose, exc)
            continue
        doc.yc_file_id = file_id
        await db.flush()
        return file_id
    return None


async def _answer_with_code_interpreter(
    db: AsyncSession, doc: Document, message: str, context: dict, previous_response_id: str | None
) -> ChatReply:
    file_id = await _ensure_yc_file(db, doc)
    if not file_id:
        return ChatReply(ERROR_MESSAGE)

    for attempt in range(2):
        try:
            reply = await run_in_threadpool(
                generate_answer,
                message,
                context,
                previous_response_id=previous_response_id,
                mode="code_interpreter",
                file_id=file_id,
                filename=doc.original_filename,
            )
        except FileUnavailableError:
            if attempt:
                break
            # the file vanished on the Yandex side — re-upload once and retry
            logger.warning("Files API: файл %s недоступен, перезаливаю", file_id)
            doc.yc_file_id = None
            file_id = await _ensure_yc_file(db, doc)
            if not file_id:
                break
            continue
        # the model may cite the uploaded workbook itself — that's not a new artifact
        reply.artifacts = tuple(a for a in reply.artifacts if a.file_id != file_id)
        return reply
    return ChatReply(ERROR_MESSAGE)


# --------------------------------------------------------------------------- ask

async def ask(
    db: AsyncSession,
    user: User,
    message: str,
    document_id: int | None = None,
    session_id: str | None = None,
    mode: str = "auto",
) -> dict[str, Any]:
    # Validate the document up-front: prevents a FK-violation 500 and stops a
    # user attaching another user's document to their chat session.
    from app.services.document_service import get_document

    doc: Document | None = None
    if document_id is not None:
        doc = await get_document(db, document_id, user)
        if not doc:
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
    elif document_id is not None and session.document_id != document_id:
        # The user switched documents mid-session: restart the dialog chain so the
        # model doesn't carry the previous document's context.
        session.document_id = document_id
        session.last_response_id = None

    effective_doc_id = session.document_id
    context = await _build_context(db, effective_doc_id, user)

    # Resolve the effective mode. "auto" (the default) keeps the fast path unless the
    # question clearly needs the workbook itself (a file, table, chart, recalculation);
    # "code_interpreter" forces it and therefore needs an attached document.
    use_ci = False
    reply: ChatReply | None = None
    if mode == "code_interpreter":
        if not code_interpreter_enabled():
            reply = ChatReply(CI_DISABLED_MESSAGE)
        elif effective_doc_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Для расчёта по файлу выберите документ",
            )
        else:
            use_ci = True
    elif mode == "auto":
        use_ci = (
            code_interpreter_enabled()
            and effective_doc_id is not None
            and wants_code_interpreter(message)
        )

    if reply is None and use_ci:
        if doc is None or doc.id != effective_doc_id:
            doc = await get_document(db, effective_doc_id, user)
        if doc is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
        reply = await _answer_with_code_interpreter(
            db, doc, message, context, session.last_response_id
        )
    elif reply is None:
        # generate_answer performs a blocking network call, so run it off the event loop.
        reply = await run_in_threadpool(
            generate_answer, message, context, previous_response_id=session.last_response_id
        )
    effective_mode = "code_interpreter" if use_ci else "context"

    if reply.response_id:
        session.last_response_id = reply.response_id
    elif reply.context_reset:
        session.last_response_id = None

    db.add(
        ChatMessage(id=_new_id(), session_id=session.id, role=MessageRole.user, content=message)
    )
    db.add(
        ChatMessage(
            id=_new_id(),
            session_id=session.id,
            role=MessageRole.assistant,
            content=reply.answer,
            mode=effective_mode,
            # ownership record for downloads (see download_artifact)
            artifacts=[ChatArtifact(file_id=a.file_id, filename=a.filename) for a in reply.artifacts],
        )
    )
    await db.flush()
    return {
        "answer": reply.answer,
        "sources": [],
        "sessionId": session.id,
        "mode": effective_mode,
        "artifacts": [{"fileId": a.file_id, "filename": a.filename} for a in reply.artifacts],
    }


# --------------------------------------------------------------------- artifacts

async def get_artifact(db: AsyncSession, file_id: str, user: User) -> ChatArtifact | None:
    """The artifact row for ``file_id`` if it was produced in one of the user's sessions."""
    result = await db.execute(
        select(ChatArtifact)
        .join(ChatMessage, ChatMessage.id == ChatArtifact.message_id)
        .join(ChatSession, ChatSession.id == ChatMessage.session_id)
        .where(ChatArtifact.file_id == file_id, ChatSession.user_id == user.id)
        .limit(1)
    )
    return result.scalars().first()


def _is_not_found(exc: Exception) -> bool:
    try:
        import openai
    except Exception:  # pragma: no cover
        return False
    return isinstance(exc, openai.NotFoundError)


async def download_artifact(db: AsyncSession, file_id: str, user: User) -> tuple[bytes, str]:
    """Fetch a Code Interpreter output from the Yandex Files API for its owner.

    Yandex file ids are not tied to a user, so the ownership check against
    ``chat_artifacts`` is what stops one user from downloading another's files.
    Returns the file bytes and the name the model gave the file.
    """
    artifact = await get_artifact(db, file_id, user)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")
    if not yandex_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Подключение к Yandex AI Studio не настроено",
        )
    try:
        data = await run_in_threadpool(get_yandex_client().download_file, file_id)
    except Exception as exc:  # noqa: BLE001
        if _is_not_found(exc):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл больше недоступен в Files API",
            ) from exc
        logger.warning("Files API: не удалось скачать %s: %s", file_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось скачать файл из Files API",
        ) from exc
    return data, artifact.filename
