"""chat_artifacts: files produced by Code Interpreter, keyed to the chat message

Yandex Files API ids are not tied to a user, so the app records which session each
file was produced in and serves downloads only to that session's owner.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-08 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_artifacts",
        sa.Column("message_id", sa.String(length=64), nullable=False),
        sa.Column("file_id", sa.String(length=128), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("message_id", "file_id"),
    )
    op.create_index("ix_chat_artifacts_file_id", "chat_artifacts", ["file_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_artifacts_file_id", table_name="chat_artifacts")
    op.drop_table("chat_artifacts")
