"""chat sessions: last Yandex response id for dialog context

Stores the last Responses API ``response.id`` per chat session so the next turn can
pass it as ``previous_response_id`` — Yandex AI Studio then keeps the dialog history
on its side instead of the app re-sending messages.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-08 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_sessions",
        sa.Column("last_response_id", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chat_sessions", "last_response_id")
