"""add total satoshis received

Revision ID: 0d10a4e705d2
Revises: 96669fcbff54
Create Date: 2019-03-08 15:00:20.149863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d10a4e705d2'
down_revision = '96669fcbff54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('open_channels', sa.Column('total_satoshis_received', sa.BIGINT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('open_channels', 'total_satoshis_received')
    # ### end Alembic commands ###
