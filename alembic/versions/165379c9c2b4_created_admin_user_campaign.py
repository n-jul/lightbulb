"""created admin user campaign.

Revision ID: 165379c9c2b4
Revises: cc1c537ff35a
Create Date: 2025-02-03 14:39:49.249741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func



# revision identifiers, used by Alembic.
revision: str = '165379c9c2b4'
down_revision: Union[str, None] = 'cc1c537ff35a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the table 'admin_user_campaign'
    op.create_table(
        'admin_user_campaign',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop the 'admin_user_campaign' table if downgrading
    op.drop_table('admin_user_campaign')