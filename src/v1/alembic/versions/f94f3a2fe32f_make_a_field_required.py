import sqlalchemy as sa
from alembic import op

revision = "f94f3a2fe32f"
down_revision = "37d6f44b1f73"
branch_labels = None
depends_on = None


def upgrade():
    # Rename the old table
    op.rename_table("order", "order_old")

    # Recreate the table with NOT NULL
    op.create_table(
        "order",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("entity_in_inventory_id", sa.Integer, nullable=False),
        # add other columns here exactly as in your old table
    )

    # Copy the data (assuming no NULLs already exist in entity_in_inventory_id)
    op.execute("""
        INSERT INTO "order" (id, entity_in_inventory_id)
        SELECT id, entity_in_inventory_id
        FROM order_old
    """)

    # Drop the old table
    op.drop_table("order_old")


def downgrade():
    # Reverse of upgrade: make the column nullable
    op.rename_table("order", "order_old")

    op.create_table(
        "order",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("entity_in_inventory_id", sa.Integer, nullable=True),
        # same other columns
    )

    op.execute("""
        INSERT INTO "order" (id, entity_in_inventory_id)
        SELECT id, entity_in_inventory_id
        FROM order_old
    """)

    op.drop_table("order_old")
