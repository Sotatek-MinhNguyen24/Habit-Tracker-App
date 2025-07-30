"""add phone column to users

Revision ID: 68adbf4b422b
Revises: 
Create Date: 2025-07-29 10:59:19.037454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68adbf4b422b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))



def downgrade() -> None:
    """Downgrade schema."""
    pass
