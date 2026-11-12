"""Track first-start demo initialization.

Revision ID: b6a8d104c7e2
Revises: 9b7c4e2a61d0
Create Date: 2026-11-11
"""

import sqlalchemy as sa
from alembic import op

revision = "b6a8d104c7e2"
down_revision = "9b7c4e2a61d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "demo_initialization",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "initialized_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("demo_initialization")
