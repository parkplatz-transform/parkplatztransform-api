"""

Revision ID: 32dd5093e5d1
Revises: ad12fb2be56b
Create Date: 2021-01-15 12:52:49.074383

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '32dd5093e5d1'
down_revision = 'ad12fb2be56b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    user_restriction = postgresql.ENUM('handicap', 'residents', 'car_sharing', 'gender', 'electric_cars', 'other', name='userrestriction')
    user_restriction.create(op.get_bind())
    alternative_usage_reason = postgresql.ENUM('bus_stop', 'bus_lane', 'market', 'lane', 'taxi', 'other', name='alternativeusagereason')
    alternative_usage_reason.create(op.get_bind())

    op.add_column('subsegments', sa.Column('user_restrictions', sa.Enum('handicap', 'residents', 'car_sharing', 'gender', 'electric_cars', 'other', name='userrestriction'), nullable=True))
    op.drop_column('subsegments', 'usage_restrictions')

    op.add_column('subsegments', sa.Column('alternative_usage_reason', sa.Enum('bus_stop', 'bus_lane', 'market', 'lane', 'taxi', 'other', name='alternativeusagereason'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subsegments', sa.Column('usage_restrictions', postgresql.ARRAY(postgresql.ENUM('handicap', 'residents', 'car_sharing', 'gender', 'electric_cars', 'other', name='usagerestriction')), autoincrement=False, nullable=True))
    op.drop_column('subsegments', 'user_restrictions')
    op.drop_column('subsegments', 'alternative_usage_reason')
    # ### end Alembic commands ###