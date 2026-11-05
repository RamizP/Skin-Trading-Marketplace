"""make order entity required

Revision ID: 8674098ec994
Revises: d7e6c5b4a3f2
Create Date: 2026-11-05 13:37:08.740001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8674098ec994'
down_revision: Union[str, None] = 'd7e6c5b4a3f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("order") as batch_op:
        batch_op.alter_column(
            "entity_id",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("order") as batch_op:
        batch_op.alter_column(
            "entity_id",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
        )