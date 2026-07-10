"""Document upload / retrieval business logic."""
from __future__ import annotations

import logging
import os

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document, DocumentStatus, DocumentTemplate
from app.models.user import User
from app.services.analysis_service import process_document
from app.utils.file_validators import safe_storage_path, validate_upload_file

logger = logging.getLogger("fin-auditor")


async def save_upload(
    db: AsyncSession, file: UploadFile, template: DocumentTemplate, user: User
) -> Document:
    validate_upload_file(file)
    storage_path = safe_storage_path(settings.UPLOAD_DIR, file.filename or "upload.xlsx")

    async with aiofiles.open(str(storage_path), "wb") as out:
        while chunk := await file.read(1024 * 1024):
            await out.write(chunk)

    doc = Document(
        name=file.filename or "document",
        original_filename=file.filename or "document",
        template=template,
        status=DocumentStatus.uploaded,
        file_size=file.size or 0,
        file_path=str(storage_path),
        uploaded_by_id=user.id,
    )
    db.add(doc)
    await db.flush()
    await db.commit()  # commit so sync fallback engine can see the row

    # Kick off analysis (Celery if available, otherwise in-process sync).
    result = await process_document(doc.id, use_celery=not settings.APP_DEBUG)
    # The sync path writes status/progress in a separate session; reload so the
    # upload response reflects the real state instead of stale "uploaded"/0.0.
    await db.refresh(doc)
    if isinstance(result, dict) and result.get("analysis_id"):
        doc.analysis_id = int(result["analysis_id"])
    return doc


async def list_documents(db: AsyncSession, user: User, skip: int = 0, limit: int = 50) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.uploaded_by_id == user.id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_document(db: AsyncSession, document_id: int, user: User) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.uploaded_by_id == user.id)
    )
    return result.scalar_one_or_none()


async def delete_document(db: AsyncSession, document_id: int, user: User) -> bool:
    doc = await get_document(db, document_id, user)
    if not doc:
        return False
    file_path = doc.file_path
    # ORM delete so cascade rules apply (analysis + risks go with the document,
    # chat sessions are detached). A Core bulk delete would bypass them.
    await db.delete(doc)
    await db.commit()
    # Best-effort file cleanup once the row is actually gone.
    if file_path:
        try:
            os.remove(file_path)
        except OSError:
            logger.warning("Не удалось удалить файл документа %s", file_path)
    return True
