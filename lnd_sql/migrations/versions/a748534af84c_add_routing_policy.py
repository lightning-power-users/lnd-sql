"""add routing policy

Revision ID: a748534af84c
Revises: 9434b12b1df3
Create Date: 2019-03-24 12:39:55.736381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a748534af84c'
down_revision = '9434b12b1df3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('etl_routing_policies',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('pubkey', sa.String(), nullable=True),
    sa.Column('channel_id', sa.BIGINT(), nullable=True),
    sa.Column('last_update', sa.DateTime(timezone=True), nullable=True),
    sa.Column('time_lock_delta', sa.BIGINT(), nullable=True),
    sa.Column('min_htlc', sa.BIGINT(), nullable=True),
    sa.Column('fee_base_msat', sa.BIGINT(), nullable=True),
    sa.Column('fee_rate_milli_msat', sa.BIGINT(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('max_htlc_msat', sa.BIGINT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('routing_policies',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('pubkey', sa.String(), nullable=True),
    sa.Column('channel_id', sa.BIGINT(), nullable=True),
    sa.Column('last_update', sa.DateTime(timezone=True), nullable=True),
    sa.Column('time_lock_delta', sa.BIGINT(), nullable=True),
    sa.Column('min_htlc', sa.BIGINT(), nullable=True),
    sa.Column('fee_base_msat', sa.BIGINT(), nullable=True),
    sa.Column('fee_rate_milli_msat', sa.BIGINT(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('max_htlc_msat', sa.BIGINT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('routing_policies')
    op.drop_table('etl_routing_policies')
    # ### end Alembic commands ###
