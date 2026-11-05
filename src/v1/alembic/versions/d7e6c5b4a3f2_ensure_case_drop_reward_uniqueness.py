"""ensure case drop reward uniqueness

Revision ID: d7e6c5b4a3f2
Revises: c2f8e4a1d9b7
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7e6c5b4a3f2"
down_revision: str | None = "c2f8e4a1d9b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    unique_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("case_drop")
    }
    if "uq_case_drop_reward" not in unique_constraints:
        with op.batch_alter_table("case_drop") as batch_op:
            batch_op.create_unique_constraint(
                "uq_case_drop_reward",
                ["case_entity_id", "reward_entity_id"],
            )


def downgrade() -> None:
    with op.batch_alter_table("case_drop") as batch_op:
        batch_op.drop_constraint("uq_case_drop_reward", type_="unique")
