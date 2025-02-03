"""Add practice table

Revision ID: cc1c537ff35a
Revises: ee0c52dc738a
Create Date: 2025-02-03 10:57:28.478367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc1c537ff35a'
down_revision: Union[str, None] = 'ee0c52dc738a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'practice',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=True)
    )
    pass


def downgrade() -> None:
    op.drop_table('practice')
    pass
