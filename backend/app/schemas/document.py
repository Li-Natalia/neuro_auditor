"""Document Pydantic schemas."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    name: str
    template: str
    status: str
    fileSize: int
    uploadedAt: datetime
    processingProgress: float = 0.0
    uploadedById: int
    analysisId: Optional[int] = None

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    document: DocumentOut
    message: str


class DocumentCreate(BaseModel):
    name: str = Field(min_length=1)
    template: str = "RSBU"


def doc_to_out(doc, analysis_id: int | None = None) -> DocumentOut:
    """Convert SQLAlchemy Document model to DocumentOut dict.

    Pass analysis_id explicitly to avoid lazy-load outside async context.
    """
    return DocumentOut(
        id=doc.id,
        name=doc.name,
        template=doc.template.value if hasattr(doc.template, "value") else doc.template,
        status=doc.status.value if hasattr(doc.status, "value") else doc.status,
        fileSize=doc.file_size,
        uploadedAt=doc.created_at,
        processingProgress=doc.processing_progress,
        uploadedById=doc.uploaded_by_id,
        analysisId=analysis_id,
    )
