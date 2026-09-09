"""documents: Yandex Files API id for Code Interpreter mode

The uploaded workbook is sent to the Yandex Files API once per document; the returned
file id is stored here and reused by every Code Interpreter chat request.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-08 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("yc_file_id", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "yc_file_id")
