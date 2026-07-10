"""Analysis business logic and orchestration of document processing."""
from __future__ import annotations

import logging
from typing import Any

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.document import Document, DocumentStatus
from app.models.risk import Risk, RiskLevel

logger = logging.getLogger("fin-auditor")

# Lazily-created shared synchronous engine, reused across sync-fallback runs so
# we don't build (and leak) a fresh connection pool on every upload.
_sync_engine = None


def _get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        from sqlalchemy import create_engine

        from app.core.config import settings

        _sync_engine = create_engine(
            settings.DATABASE_URL_SYNC, pool_pre_ping=True, future=True
        )
    return _sync_engine


async def list_analyses(db: AsyncSession, user) -> list[Analysis]:
    result = await db.execute(
        select(Analysis)
        .join(Document, Document.id == Analysis.document_id)
        .where(Document.uploaded_by_id == user.id)
        .order_by(Analysis.created_at.desc())
    )
    return list(result.scalars().all())


async def get_analysis_by_id(db: AsyncSession, analysis_id: int, user) -> Analysis | None:
    result = await db.execute(
        select(Analysis)
        .join(Document, Document.id == Analysis.document_id)
        .where(Analysis.id == analysis_id, Document.uploaded_by_id == user.id)
    )
    return result.scalar_one_or_none()


async def get_analysis_by_document(db: AsyncSession, document_id: int, user) -> Analysis | None:
    result = await db.execute(
        select(Analysis)
        .join(Document, Document.id == Analysis.document_id)
        .where(Analysis.document_id == document_id, Document.uploaded_by_id == user.id)
    )
    return result.scalar_one_or_none()


async def get_summary(db: AsyncSession, user) -> dict[str, Any]:
    analyses = await list_analyses(db, user)
    total_risks = 0
    critical = 0
    total_score = 0.0
    for a in analyses:
        risks = a.risks or []
        total_risks += len(risks)
        critical += sum(1 for r in risks if r.level == RiskLevel.critical)
        total_score += sum(
            {"critical": 3, "medium": 2, "low": 1}.get(r.level, 0) if isinstance(r.level, str)
            else {"critical": 3, "medium": 2, "low": 1}.get(r.level.value, 0)
            for r in risks
        )
    avg = total_score / len(analyses) if analyses else 0.0
    return {
        "totalDocuments": len(analyses),
        "totalRisks": total_risks,
        "criticalRisks": critical,
        "averageRiskScore": round(avg, 2),
        "trend": [],
    }


async def process_document(document_id: int, use_celery: bool = True) -> dict:
    """Run analysis for a document, preferring Celery when available.

    Falls back to synchronous in-process processing when the broker is not
    reachable so the API stays functional in development without Redis.
    """
    if use_celery:
        try:
            from app.tasks.analysis_tasks import process_document_task

            result = process_document_task.delay(document_id)
            return {"status": "queued", "task_id": result.id}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Celery unavailable, running analysis in-process: %s", exc)

    # Sync fallback — offload the blocking DB + Excel work off the event loop.
    return await run_in_threadpool(_process_document_sync, document_id)


def _process_document_sync(document_id: int) -> dict:
    from sqlalchemy.orm import Session

    from app.models.analysis import Analysis as AnalysisModel
    from app.models.document import Document as DocumentModel
    from app.models.risk import Risk as RiskModel
    from app.processors.excel_parser import parse_workbook
    from app.processors.financial_analyzer import build_summary, compute_ratios
    from app.processors.risk_analyzer import detect_risks

    with Session(_get_sync_engine()) as db:
        doc = db.get(DocumentModel, document_id)
        if not doc:
            return {"status": "not_found"}
        doc.status = DocumentStatus.processing
        doc.processing_progress = 50.0
        db.commit()
        try:
            parsed = parse_workbook(doc.file_path)
            ratios = compute_ratios(parsed["balance"], parsed["income"])
            risks_data = detect_risks(parsed["balance"], parsed["income"], ratios)
            summary = build_summary(parsed["balance"], parsed["income"], ratios)

            analysis = AnalysisModel(
                document_id=doc.id,
                balance_sheet=parsed["balance"],
                income_statement=parsed["income"],
                cash_flow_statement=parsed["cashflow"],
                ratios=ratios,
                summary=summary,
            )
            db.add(analysis)
            db.flush()
            for r in risks_data:
                db.add(
                    RiskModel(
                        analysis_id=analysis.id,
                        level=r["level"],
                        title=r["title"],
                        description=r["description"],
                        recommendation=r["recommendation"],
                        metric=r.get("metric"),
                        value=r.get("value"),
                        threshold=r.get("threshold"),
                    )
                )
            doc.status = DocumentStatus.completed
            doc.processing_progress = 100.0
            doc.analysis = analysis
            db.commit()
            return {"status": "completed", "analysis_id": analysis.id}
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            doc.status = DocumentStatus.failed
            doc.error_message = str(exc)
            db.commit()
            return {"status": "failed", "error": str(exc)}
