"""add etl open channels

Revision ID: d5149c4e2ffc
Revises: 85714e28e854
Create Date: 2019-03-05 21:29:02.487310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5149c4e2ffc'
down_revision = '85714e28e854'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('etl_open_channels',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('chan_id', sa.BIGINT(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('local_pubkey', sa.String(), nullable=True),
    sa.Column('remote_pubkey', sa.String(), nullable=True),
    sa.Column('channel_point', sa.String(), nullable=True),
    sa.Column('capacity', sa.BIGINT(), nullable=True),
    sa.Column('local_balance', sa.BIGINT(), nullable=True),
    sa.Column('remote_balance', sa.BIGINT(), nullable=True),
    sa.Column('commit_fee', sa.BIGINT(), nullable=True),
    sa.Column('commit_weight', sa.BIGINT(), nullable=True),
    sa.Column('fee_per_kw', sa.BIGINT(), nullable=True),
    sa.Column('total_satoshis_sent', sa.BIGINT(), nullable=True),
    sa.Column('num_updates', sa.BIGINT(), nullable=True),
    sa.Column('csv_delay', sa.BIGINT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('etl_open_channels')
    # ### end Alembic commands ###