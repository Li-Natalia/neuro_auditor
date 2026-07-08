"""Document-related background tasks (async file processing).

Runs synchronously inside the Celery worker (separate process), so it uses a
sync DB session and the sync database URL.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.analysis import Analysis
from app.models.document import Document, DocumentStatus
from app.models.risk import Risk
from app.processors.excel_parser import parse_workbook
from app.processors.financial_analyzer import build_summary, compute_ratios
from app.processors.risk_analyzer import detect_risks
from app.tasks.celery_app import celery_app

_sync_engine = create_engine(settings.DATABASE_URL_SYNC, pool_pre_ping=True, future=True)


def _sync_session() -> Session:
    return Session(_sync_engine)


@celery_app.task(name="process_document", bind=True)
def process_document_task(self, document_id: int):
    """Parse an uploaded document and store the analysis + risks."""
    with _sync_session() as db:
        doc = db.get(Document, document_id)
        if not doc:
            return {"status": "not_found"}

        doc.status = DocumentStatus.processing
        doc.processing_progress = 10.0
        db.commit()

        try:
            parsed = parse_workbook(doc.file_path)
            doc.processing_progress = 50.0
            db.commit()

            ratios = compute_ratios(parsed["balance"], parsed["income"])
            risks_data = detect_risks(parsed["balance"], parsed["income"], ratios)
            summary = build_summary(parsed["balance"], parsed["income"], ratios)

            analysis = Analysis(
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
                    Risk(
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
            doc.status = DocumentStatus.failed
            doc.error_message = str(exc)
            doc.processing_progress = 0.0
            db.commit()
            return {"status": "failed", "error": str(exc)}
