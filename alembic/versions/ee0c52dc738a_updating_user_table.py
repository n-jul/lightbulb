"""Updating user table.

Revision ID: ee0c52dc738a
Revises: f53f288cd4fb
Create Date: 2025-01-24 13:06:23.759868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee0c52dc738a'
down_revision: Union[str, None] = 'f53f288cd4fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'user_message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('is_selected', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['auth_user.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('user_message')
