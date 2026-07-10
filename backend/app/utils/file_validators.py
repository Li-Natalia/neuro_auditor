"""File validation helpers."""
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def validate_upload_file(file: UploadFile) -> None:
    ext = get_extension(file.filename or "")
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Недопустимый тип файла .{ext}. Разрешены: {', '.join(settings.allowed_extensions_list)}",
        )
    if file.size and file.size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой. Максимум {settings.MAX_UPLOAD_SIZE_MB} МБ",
        )


def safe_storage_path(upload_dir: str, original_filename: str) -> Path:
    base = Path(upload_dir)
    base.mkdir(parents=True, exist_ok=True)
    # Avoid path traversal and name collisions
    safe_name = Path(original_filename).name
    stem = Path(safe_name).stem
    suffix = Path(safe_name).suffix
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique = f"{timestamp}_{stem}_{uuid.uuid4().hex}{suffix}"
    return base / unique
