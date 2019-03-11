"""modify invoices columns

Revision ID: 4e17591a057f
Revises: b2b495894875
Create Date: 2019-03-10 21:51:23.877777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e17591a057f'
down_revision = 'b2b495894875'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoices', sa.Column('local_pubkey', sa.String(), nullable=True))
    op.drop_column('invoices', 'invoice_state')
    op.drop_column('invoices', 'amt_paid')
    op.drop_column('invoices', 'amt_paid_msat')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoices', sa.Column('amt_paid_msat', sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column('invoices', sa.Column('amt_paid', sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column('invoices', sa.Column('invoice_state', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('invoices', 'local_pubkey')
    # ### end Alembic commands ###
