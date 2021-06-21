"""empty message

Revision ID: cd45f661e649
Revises: dc39e93f6e34
Create Date: 2021-04-25 12:07:43.718144

"""

# revision identifiers, used by Alembic.
revision = 'cd45f661e649'
down_revision = 'dc39e93f6e34'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('referer', sa.String(length=512), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('requests', 'referer')
    # ### end Alembic commands ###