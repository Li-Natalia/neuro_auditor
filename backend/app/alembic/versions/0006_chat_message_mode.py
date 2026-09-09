"""chat_messages: mode the assistant answered in ("context" / "code_interpreter")

Shown under the answer so users know when a reply came from Code Interpreter (the
"auto" mode routes there only for questions that need the workbook itself).

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-09 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chat_messages", sa.Column("mode", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("chat_messages", "mode")
