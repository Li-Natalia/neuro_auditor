"""Document upload and management routes."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pagination import get_pagination
from app.core.database import get_db
from app.models.document import Document, DocumentTemplate
from app.models.user import User
from app.schemas.document import DocumentOut, UploadResponse, doc_to_out
from app.services import document_service

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    template: str = Form("RSBU"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tmpl = DocumentTemplate(template)
    doc = await document_service.save_upload(db, file, tmpl, current_user)
    analysis_id = getattr(doc, "analysis_id", None)
    return UploadResponse(
        document=doc_to_out(doc, analysis_id),
        message="Файл загружен. Анализ запущен.",
    )


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    pagination=Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.analysis))
        .where(Document.uploaded_by_id == current_user.id)
        .order_by(Document.created_at.desc())
        .offset(pagination.skip)
        .limit(pagination.limit)
    )
    docs = list(result.scalars().all())
    out = []
    for d in docs:
        aid = d.analysis.id if d.analysis else None
        out.append(doc_to_out(d, aid))
    return out


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.analysis))
        .where(Document.id == document_id, Document.uploaded_by_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    aid = doc.analysis.id if doc.analysis else None
    return doc_to_out(doc, aid)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await document_service.delete_document(db, document_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
