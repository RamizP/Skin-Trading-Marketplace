"""Record completed trades with item snapshots.

Revision ID: c8e2f7a4d901
Revises: b6a8d104c7e2
Create Date: 2026-11-12
"""

import sqlalchemy as sa
from alembic import op

revision = "c8e2f7a4d901"
down_revision = "b6a8d104c7e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trade_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column(
            "entity_wear",
            sa.Enum(
                "NONE",
                "FACTORY_NEW",
                "MINIMAL_WEAR",
                "FIELD_TESTED",
                "WELL_WORN",
                "BATTLE_SCARRED",
                name="entitywear",
            ),
            nullable=False,
        ),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("price > 0", name="ck_trade_history_price_positive"),
        sa.CheckConstraint(
            "seller_id != buyer_id", name="ck_trade_history_different_users"
        ),
        sa.ForeignKeyConstraint(["seller_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["buyer_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(
            ["item_id"], ["user_inventory.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trade_history_id", "trade_history", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trade_history_id", table_name="trade_history")
    op.drop_table("trade_history")
