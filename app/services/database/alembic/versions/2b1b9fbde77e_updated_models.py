"""Updated models

Revision ID: 2b1b9fbde77e
Revises: f8342fb73fba
Create Date: 2024-08-16 19:15:42.718625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b1b9fbde77e'
down_revision: Union[str, None] = 'f8342fb73fba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('economic_calendar_alerts', sa.Column('event_execution', sa.DateTime(), nullable=False))
    op.drop_column('economic_calendar_alerts', 'event_exevution')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('economic_calendar_alerts', sa.Column('event_exevution', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_column('economic_calendar_alerts', 'event_execution')
    # ### end Alembic commands ###
