"""

Revision ID: 2da07dd7d67b
Revises: 7cba74d7ab74
Create Date: 2020-12-10 19:50:55.354402

"""
from alembic import op
from sqlalchemy import Numeric


# revision identifiers, used by Alembic.
revision = '2da07dd7d67b'
down_revision = '7cba74d7ab74'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('subsegments', 'length_in_meters', type_=Numeric)
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###