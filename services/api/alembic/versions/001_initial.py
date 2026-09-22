"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-09-21
"""
from typing import Sequence, Union

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tables are created via SQLAlchemy metadata.create_all on startup for MVP.
    # This revision documents the baseline; generate autogenerate diffs in later work.
    pass


def downgrade() -> None:
    pass
