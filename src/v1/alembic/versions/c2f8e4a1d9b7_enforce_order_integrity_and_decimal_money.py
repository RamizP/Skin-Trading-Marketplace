"""enforce order integrity and decimal money

Revision ID: c2f8e4a1d9b7
Revises: a4c9d2e71f10
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c2f8e4a1d9b7"
down_revision: str | None = "a4c9d2e71f10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('UPDATE "user" SET balance = 0 WHERE balance IS NULL')

    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column(
            "balance",
            existing_type=sa.INTEGER(),
            type_=sa.Numeric(12, 2),
            existing_nullable=True,
            nullable=False,
            server_default=sa.text("0"),
        )

    with op.batch_alter_table("order") as batch_op:
        batch_op.alter_column(
            "price",
            existing_type=sa.FLOAT(),
            type_=sa.Numeric(12, 2),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "side",
            existing_type=sa.VARCHAR(length=4),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_order_user_id_user", "user", ["user_id"], ["id"]
        )
        batch_op.create_foreign_key(
            "fk_order_entity_id_entity", "entity", ["entity_id"], ["id"]
        )
        batch_op.create_foreign_key(
            "fk_order_inventory_id_user_inventory",
            "user_inventory",
            ["entity_in_inventory_id"],
            ["id"],
        )
        batch_op.create_check_constraint("ck_order_price_positive", "price > 0")
        batch_op.create_check_constraint(
            "ck_order_side_inventory",
            "(side = 'SELL' AND entity_in_inventory_id IS NOT NULL) "
            "OR (side = 'BUY' AND entity_in_inventory_id IS NULL)",
        )


def downgrade() -> None:
    with op.batch_alter_table("order") as batch_op:
        batch_op.drop_constraint("ck_order_side_inventory", type_="check")
        batch_op.drop_constraint("ck_order_price_positive", type_="check")
        batch_op.drop_constraint("fk_order_inventory_id_user_inventory", type_="foreignkey")
        batch_op.drop_constraint("fk_order_entity_id_entity", type_="foreignkey")
        batch_op.drop_constraint("fk_order_user_id_user", type_="foreignkey")
        batch_op.alter_column(
            "side",
            existing_type=sa.VARCHAR(length=4),
            nullable=True,
        )
        batch_op.alter_column(
            "price",
            existing_type=sa.Numeric(12, 2),
            type_=sa.FLOAT(),
            existing_nullable=False,
        )

    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column(
            "balance",
            existing_type=sa.Numeric(12, 2),
            type_=sa.INTEGER(),
            existing_nullable=False,
            nullable=True,
            server_default=None,
        )
