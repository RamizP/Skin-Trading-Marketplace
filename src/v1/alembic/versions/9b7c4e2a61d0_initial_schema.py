"""Create the complete initial schema.

Revision ID: 9b7c4e2a61d0
Revises:
Create Date: 2026-11-11

This baseline replaces the incomplete development migration history. Keep the
previous head ID so databases already at that revision do not replay it.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9b7c4e2a61d0"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_category_id", "category", ["id"], unique=False)

    op.create_table(
        "entity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("symbol", sa.String(255), nullable=False),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column(
            "entity_rarity",
            sa.Enum(
                "COMMON",
                "UNCOMMON",
                "RARE",
                "MYTHICAL",
                "LEGENDARY",
                "EXCEEDINGLY_RARE",
                name="entityrarity",
            ),
            nullable=True,
        ),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("sub_category_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_index("ix_entity_id", "entity", ["id"], unique=False)

    op.create_table(
        "sub_category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_sub_category_id", "sub_category", ["id"], unique=False)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("password_hashed", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("user", "admin", name="userrole"), nullable=True),
        sa.Column(
            "status", sa.Enum("active", "blocked", name="userstatus"), nullable=True
        ),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("bio", sa.String(512), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("balance", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_user_id", "user", ["id"], unique=False)

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
            "case_entity_id", "reward_entity_id", name="uq_case_drop_reward"
        ),
    )
    op.create_table(
        "free_case_cooldown",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "last_claimed_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "user_inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
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
            server_default="NONE",
            nullable=False,
        ),
        sa.Column("in_sale", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_inventory_id", "user_inventory", ["id"], unique=False)

    op.create_table(
        "order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("entity_in_inventory_id", sa.Integer(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("side", sa.Enum("SELL", "BUY", name="side"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True
        ),
        sa.CheckConstraint("price > 0", name="ck_order_price_positive"),
        sa.CheckConstraint(
            "(side = 'SELL' AND entity_in_inventory_id IS NOT NULL) "
            "OR (side = 'BUY' AND entity_in_inventory_id IS NULL)",
            name="ck_order_side_inventory",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["entity_in_inventory_id"], ["user_inventory.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_id", "order", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_order_id", table_name="order")
    op.drop_table("order")
    op.drop_index("ix_user_inventory_id", table_name="user_inventory")
    op.drop_table("user_inventory")
    op.drop_table("free_case_cooldown")
    op.drop_table("case_drop")
    op.drop_index("ix_user_id", table_name="user")
    op.drop_table("user")
    op.drop_index("ix_sub_category_id", table_name="sub_category")
    op.drop_table("sub_category")
    op.drop_index("ix_entity_id", table_name="entity")
    op.drop_table("entity")
    op.drop_index("ix_category_id", table_name="category")
    op.drop_table("category")
