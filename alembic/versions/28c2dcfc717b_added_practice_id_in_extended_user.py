"""Added practice id in extended user.

Revision ID: 28c2dcfc717b
Revises: beb50b69a4bd
Create Date: 2025-02-03 17:00:14.870063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28c2dcfc717b'
down_revision: Union[str, None] = 'beb50b69a4bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Added practice id in extended user."""
    op.add_column('extended_user',sa.Column('practice_id',sa.Integer(),nullable=True))
    op.create_foreign_key(
        'fk_extended_user_practice_id',
        'extended_user',
        'practice',
        ['practice_id'],
        ['id'],
        ondelete="SET NULL"
    )


def downgrade() -> None:
    """Remove practice id from the extended user table."""
    op.drop_constraint('fk_extended_user_practice_id','user_campaign',type_='foreignkey')
    op.drop_column('extended_user','practice_id')
    
