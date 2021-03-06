"""add private

Revision ID: f90d89c9fdb2
Revises: 3115f1d92acb
Create Date: 2019-03-05 21:31:02.423377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f90d89c9fdb2'
down_revision = '3115f1d92acb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('etl_open_channels', sa.Column('private', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('etl_open_channels', 'private')
    # ### end Alembic commands ###
