"""Manually add user_message table

Revision ID: f53f288cd4fb
Revises: xxxxxx
Create Date: 2025-01-23 11:47:08.544364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f53f288cd4fb'
down_revision: Union[str, None] = 'xxxxxx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_message',
        sa.Column('id',sa.BigInteger(),autoincrement=True,nullable=False),
        sa.Column('campaign_id',sa.BigInteger(),nullable=False),
        sa.Column('user_id',sa.BigInteger(),nullable=False),
        sa.Column('is_select',sa.Boolean(),default=True,server_default='true',nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'],['user_campaign.id'], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(['user_id'],['public.auth_user.id'], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table("user_message")
