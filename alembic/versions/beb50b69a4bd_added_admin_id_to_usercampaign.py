"""Added admin_id to UserCampaign.

Revision ID: beb50b69a4bd
Revises: 165379c9c2b4
Create Date: 2025-02-03 15:35:34.170884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'beb50b69a4bd'
down_revision: Union[str, None] = '165379c9c2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Add admin_id column to user_campaign table"""
    op.add_column('user_campaign', sa.Column('admin_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        'fk_user_campaign_admin_id',  # Foreign key constraint name
        'user_campaign',  # Source table
        'extended_user',  # Target table
        ['admin_id'],  # Source column
        ['id'],  # Target column
        ondelete="SET NULL"  # Optional: Sets admin_id to NULL if the referenced user is deleted
    )

def downgrade():
    """Remove admin_id column from user_campaign table"""
    op.drop_constraint('fk_user_campaign_admin_id', 'user_campaign', type_='foreignkey')
    op.drop_column('user_campaign', 'admin_id')
