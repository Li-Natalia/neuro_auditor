"""Analysis routes."""
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analysis import AnalysisResultSchema, AnalysisSummarySchema, analysis_to_out
from app.services import analysis_service
from app.utils.report_generators import generate_analysis_pdf

router = APIRouter()


@router.get("", response_model=list[AnalysisResultSchema])
async def list_analyses(db=Depends(get_db), current_user: User = Depends(get_current_user)):
    analyses = await analysis_service.list_analyses(db, current_user)
    return [analysis_to_out(a) for a in analyses]


@router.get("/summary", response_model=AnalysisSummarySchema)
async def analysis_summary(db=Depends(get_db), current_user: User = Depends(get_current_user)):
    return await analysis_service.get_summary(db, current_user)


@router.get("/by-document/{document_id}", response_model=AnalysisResultSchema)
async def get_analysis_by_document(
    document_id: int, db=Depends(get_db), current_user: User = Depends(get_current_user)
):
    a = await analysis_service.get_analysis_by_document(db, document_id, current_user)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Анализ не найден")
    return analysis_to_out(a)


@router.get("/{analysis_id}/report")
async def download_report(
    analysis_id: int, db=Depends(get_db), current_user: User = Depends(get_current_user)
):
    a = await analysis_service.get_analysis_by_id(db, analysis_id, current_user)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Анализ не найден")
    pdf_bytes = await run_in_threadpool(generate_analysis_pdf, a)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{analysis_id}.pdf"},
    )


@router.get("/{analysis_id}", response_model=AnalysisResultSchema)
async def get_analysis(
    analysis_id: int, db=Depends(get_db), current_user: User = Depends(get_current_user)
):
    a = await analysis_service.get_analysis_by_id(db, analysis_id, current_user)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Анализ не найден")
    return analysis_to_out(a)
