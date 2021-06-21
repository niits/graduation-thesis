"""empty message

Revision ID: 63b3be668a62
Revises: f5b2ab2649dc
Create Date: 2021-04-15 04:12:03.892015

"""

# revision identifiers, used by Alembic.
revision = "63b3be668a62"
down_revision = "f5b2ab2649dc"

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tracking_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tracking_codes")
    # ### end Alembic commands ###