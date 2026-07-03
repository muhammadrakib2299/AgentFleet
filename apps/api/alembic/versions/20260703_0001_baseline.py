"""baseline — empty schema anchor

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-03

Domain tables (agent, fleet, run, step, handoff) arrive in Phase 1.
"""
from typing import Sequence, Union

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
