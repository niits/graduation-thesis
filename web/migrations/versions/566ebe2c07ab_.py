"""empty message

Revision ID: 566ebe2c07ab
Revises: f3190e708dec
Create Date: 2021-04-26 14:01:06.908759

"""

# revision identifiers, used by Alembic.
revision = '566ebe2c07ab'
down_revision = 'f3190e708dec'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('zone_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('requests', 'zone_id')
    # ### end Alembic commands ###
