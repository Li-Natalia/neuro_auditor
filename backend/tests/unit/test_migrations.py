"""Startup migrations must not let alembic.ini reconfigure the app's logging."""
from app.core import migrations


def test_run_migrations_keeps_app_logging(monkeypatch):
    captured = {}

    def fake_upgrade(cfg, revision):
        captured["cfg"] = cfg
        captured["revision"] = revision

    monkeypatch.setattr("alembic.command.upgrade", fake_upgrade)
    migrations.run_migrations()

    assert captured["revision"] == "head"
    # env.py checks this flag before calling fileConfig(alembic.ini); without it every
    # logger created before the migrations (the app's, uvicorn's) would be disabled.
    assert captured["cfg"].attributes["configure_logger"] is False
