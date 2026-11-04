"""add case drop table

Revision ID: a4c9d2e71f10
Revises: 5503968ed656
Create Date: 2026-11-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4c9d2e71f10"
down_revision: Union[str, None] = "5503968ed656"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "case_drop" not in inspector.get_table_names():
        op.create_table(
            "case_drop",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("case_entity_id", sa.Integer(), nullable=False),
            sa.Column("reward_entity_id", sa.Integer(), nullable=False),
            sa.Column("weight", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["case_entity_id"], ["entity.id"]),
            sa.ForeignKeyConstraint(["reward_entity_id"], ["entity.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "case_entity_id",
                "reward_entity_id",
                name="uq_case_drop_reward",
            ),
        )
        return

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
    op.drop_table("case_drop")
