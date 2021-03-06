"""add foreign key relationship between Peers and Open Channels

Revision ID: 28a827cf194f
Revises: 90bf02c89750
Create Date: 2019-03-08 15:09:14.595816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28a827cf194f'
down_revision = '90bf02c89750'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'open_channels', 'peers', ['local_pubkey'], ['pubkey'])
    op.create_foreign_key(None, 'open_channels', 'peers', ['remote_pubkey'], ['pubkey'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'open_channels', type_='foreignkey')
    op.drop_constraint(None, 'open_channels', type_='foreignkey')
    # ### end Alembic commands ###
