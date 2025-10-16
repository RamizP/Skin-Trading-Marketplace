"""changes

Revision ID: 5503968ed656
Revises: c77d5fc86da4
Create Date: 2025-09-09 15:15:30.466401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5503968ed656'
down_revision: Union[str, None] = 'c77d5fc86da4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("order", schema=None) as batch_op:
        batch_op.alter_column(
            "entity_in_inventory_id",
            existing_type=sa.INTEGER(),
            nullable=True
        )


def downgrade() -> None:
    with op.batch_alter_table("order", schema=None) as batch_op:
        batch_op.alter_column(
            "entity_in_inventory_id",
            existing_type=sa.INTEGER(),
            nullable=False
        )
