"""added is_deleted in user cammapaign for soft deleteion.

Revision ID: efaa1df86f1d
Revises: 28c2dcfc717b
Create Date: 2025-02-05 16:42:16.430059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efaa1df86f1d'
down_revision: Union[str, None] = '28c2dcfc717b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_campaign', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('user_campaign', 'is_deleted')

