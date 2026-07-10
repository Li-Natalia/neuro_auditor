"""add ON DELETE rules to foreign keys

Without these, deleting a Document that has an Analysis (the normal case) fails
with a ForeignKeyViolation. Cascade analysis/risks with the document, detach
chat sessions (keep the user's history), cascade messages with their session.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-08 00:00:00

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # analyses.document_id -> documents.id  (delete analysis with its document)
    op.drop_constraint("analyses_document_id_fkey", "analyses", type_="foreignkey")
    op.create_foreign_key(
        "analyses_document_id_fkey", "analyses", "documents",
        ["document_id"], ["id"], ondelete="CASCADE",
    )

    # risks.analysis_id -> analyses.id  (delete risks with their analysis)
    op.drop_constraint("risks_analysis_id_fkey", "risks", type_="foreignkey")
    op.create_foreign_key(
        "risks_analysis_id_fkey", "risks", "analyses",
        ["analysis_id"], ["id"], ondelete="CASCADE",
    )

    # chat_sessions.document_id -> documents.id  (keep the session, unlink the doc)
    op.drop_constraint("chat_sessions_document_id_fkey", "chat_sessions", type_="foreignkey")
    op.create_foreign_key(
        "chat_sessions_document_id_fkey", "chat_sessions", "documents",
        ["document_id"], ["id"], ondelete="SET NULL",
    )

    # chat_messages.session_id -> chat_sessions.id  (delete messages with their session)
    op.drop_constraint("chat_messages_session_id_fkey", "chat_messages", type_="foreignkey")
    op.create_foreign_key(
        "chat_messages_session_id_fkey", "chat_messages", "chat_sessions",
        ["session_id"], ["id"], ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("chat_messages_session_id_fkey", "chat_messages", type_="foreignkey")
    op.create_foreign_key(
        "chat_messages_session_id_fkey", "chat_messages", "chat_sessions",
        ["session_id"], ["id"],
    )

    op.drop_constraint("chat_sessions_document_id_fkey", "chat_sessions", type_="foreignkey")
    op.create_foreign_key(
        "chat_sessions_document_id_fkey", "chat_sessions", "documents",
        ["document_id"], ["id"],
    )

    op.drop_constraint("risks_analysis_id_fkey", "risks", type_="foreignkey")
    op.create_foreign_key(
        "risks_analysis_id_fkey", "risks", "analyses",
        ["analysis_id"], ["id"],
    )

    op.drop_constraint("analyses_document_id_fkey", "analyses", type_="foreignkey")
    op.create_foreign_key(
        "analyses_document_id_fkey", "analyses", "documents",
        ["document_id"], ["id"],
    )
