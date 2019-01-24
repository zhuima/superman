"""empty message

Revision ID: 7213d5f7d00c
Revises: 
Create Date: 2019-01-21 11:34:10.933121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7213d5f7d00c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_admin_username'), 'admin', ['username'], unique=False)
    op.add_column('hostinfo', sa.Column('port', sa.Integer(), nullable=True))
    op.alter_column('hostinfo', 'host',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('hostinfo', 'host',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    op.drop_column('hostinfo', 'port')
    op.drop_index(op.f('ix_admin_username'), table_name='admin')
    # ### end Alembic commands ###
