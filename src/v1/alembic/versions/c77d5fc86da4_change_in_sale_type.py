"""change in_sale type

Revision ID: c77d5fc86da4
Revises: 317720a043da
Create Date: 2025-09-05 10:41:14.340953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c77d5fc86da4'
down_revision: Union[str, None] = '317720a043da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add a temporary column with Boolean type
    op.add_column('user_inventory', sa.Column('in_sale_tmp', sa.Boolean(), nullable=True))

    # 2. Copy data from old column to new column (convert string to boolean)
    op.execute("""
        UPDATE user_inventory
        SET in_sale_tmp = CASE
            WHEN in_sale IN ('1', 'true', 'True') THEN 1
            ELSE 0
        END
    """)

    # 3. Drop the old column
    op.drop_column('user_inventory', 'in_sale')

    # 4. Rename the new column to original name
    op.alter_column('user_inventory', 'in_sale_tmp', new_column_name='in_sale')



def downgrade() -> None:
    # 1. Add a temporary column with VARCHAR type
    op.add_column('user_inventory', sa.Column('in_sale_tmp', sa.VARCHAR(), nullable=True))

    # 2. Copy data from Boolean column to VARCHAR
    op.execute("""
        UPDATE user_inventory
        SET in_sale_tmp = CASE
            WHEN in_sale = 1 THEN 'true'
            ELSE 'false'
        END
    """)

    # 3. Drop the Boolean column
    op.drop_column('user_inventory', 'in_sale')

    # 4. Rename temporary column to original name
    op.alter_column('user_inventory', 'in_sale_tmp', new_column_name='in_sale')

