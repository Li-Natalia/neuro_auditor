"""Document housekeeping tasks (cleanup, periodic jobs)."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="cleanup_old_documents")
def cleanup_old_documents_task(days: int = 90):
    """Placeholder cleanup task — remove document files older than `days`.

    Implement file system + DB cleanup based on document.created_at.
    """
    return {"status": "ok", "removed": 0}
