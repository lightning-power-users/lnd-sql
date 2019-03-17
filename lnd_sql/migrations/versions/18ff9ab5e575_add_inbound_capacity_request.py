"""add inbound capacity request

Revision ID: 18ff9ab5e575
Revises: 28a827cf194f
Create Date: 2019-03-09 15:16:46.779703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18ff9ab5e575'
down_revision = '28a827cf194f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inbound_capacity_request',
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(), nullable=True),
    sa.Column('remote_pubkey', sa.String(), nullable=True),
    sa.Column('remote_host', sa.String(), nullable=True),
    sa.Column('capacity', sa.BIGINT(), nullable=True),
    sa.Column('capacity_fee_rate', sa.Numeric(), nullable=True),
    sa.Column('capacity_fee', sa.BIGINT(), nullable=True),
    sa.Column('transaction_fee_rate', sa.BIGINT(), nullable=True),
    sa.Column('expected_bytes', sa.BIGINT(), nullable=True),
    sa.Column('transaction_fee', sa.BIGINT(), nullable=True),
    sa.Column('total_fee', sa.BIGINT(), nullable=True),
    sa.Column('invoice_r_hash', sa.String(), nullable=True),
    sa.Column('payment_request', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inbound_capacity_request')
    # ### end Alembic commands ###