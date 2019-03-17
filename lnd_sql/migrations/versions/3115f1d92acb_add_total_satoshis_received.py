"""add total_satoshis_received

Revision ID: 3115f1d92acb
Revises: d5149c4e2ffc
Create Date: 2019-03-05 21:30:30.164464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3115f1d92acb'
down_revision = 'd5149c4e2ffc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('etl_open_channels', sa.Column('total_satoshis_received', sa.BIGINT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('etl_open_channels', 'total_satoshis_received')
    # ### end Alembic commands ###
