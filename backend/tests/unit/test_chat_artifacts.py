"""Code Interpreter artifacts: downloads are served only to the owner of the chat session."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

pytest.importorskip("aiosqlite")

from app.core.database import Base  # noqa: E402
from app.models.chat_history import ChatArtifact, ChatMessage, ChatSession, MessageRole  # noqa: E402
from app.services import chat_service  # noqa: E402

# SQLite doesn't enforce the users/documents foreign keys, so only the chat tables are needed.
TABLES = [ChatSession.__table__, ChatMessage.__table__, ChatArtifact.__table__]
OWNER, STRANGER = SimpleNamespace(id=1), SimpleNamespace(id=2)


async def _db() -> AsyncSession:
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=TABLES)
    db = AsyncSession(engine, expire_on_commit=False)
    db.add_all(
        [
            ChatSession(id="s1", user_id=OWNER.id, title="ликвидность"),
            ChatMessage(
                id="m1",
                session_id="s1",
                role=MessageRole.assistant,
                content="готово",
                artifacts=[ChatArtifact(file_id="file_1", filename="ratio.csv")],
            ),
        ]
    )
    await db.commit()
    return db


async def test_artifact_is_visible_only_to_session_owner():
    db = await _db()
    found = await chat_service.get_artifact(db, "file_1", OWNER)
    assert found is not None and found.filename == "ratio.csv"
    assert await chat_service.get_artifact(db, "file_1", STRANGER) is None
    assert await chat_service.get_artifact(db, "unknown", OWNER) is None

    with pytest.raises(HTTPException) as exc:
        await chat_service.download_artifact(db, "file_1", STRANGER)
    assert exc.value.status_code == 404
    await db.close()


async def test_download_returns_bytes_and_model_filename(monkeypatch):
    db = await _db()
    monkeypatch.setattr(chat_service, "yandex_configured", lambda: True)
    monkeypatch.setattr(
        chat_service,
        "get_yandex_client",
        lambda: SimpleNamespace(download_file=lambda file_id: b"a,b\n1,2\n"),
    )
    data, filename = await chat_service.download_artifact(db, "file_1", OWNER)
    assert data == b"a,b\n1,2\n" and filename == "ratio.csv"
    await db.close()


async def test_download_of_expired_file_is_404(monkeypatch):
    openai = pytest.importorskip("openai")
    httpx = pytest.importorskip("httpx")
    db = await _db()

    def gone(file_id):
        raise openai.NotFoundError(
            "gone",
            response=httpx.Response(404, request=httpx.Request("GET", "https://example")),
            body=None,
        )

    monkeypatch.setattr(chat_service, "yandex_configured", lambda: True)
    monkeypatch.setattr(chat_service, "get_yandex_client", lambda: SimpleNamespace(download_file=gone))
    with pytest.raises(HTTPException) as exc:
        await chat_service.download_artifact(db, "file_1", OWNER)
    assert exc.value.status_code == 404
    await db.close()
