"""Reports routes (history of uploaded documents / analyses)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentOut, doc_to_out

router = APIRouter()


@router.get("", response_model=list[DocumentOut])
async def list_reports(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.analysis))
        .where(Document.uploaded_by_id == current_user.id)
        .order_by(Document.created_at.desc())
        .limit(500)
    )
    docs = list(result.scalars().all())
    out = []
    for d in docs:
        aid = d.analysis.id if d.analysis else None
        out.append(doc_to_out(d, aid))
    return out
