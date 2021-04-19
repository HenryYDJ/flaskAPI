"""empty message

Revision ID: fd2db22f19f9
Revises: 7d0cb4cbf1a3
Create Date: 2021-04-04 17:16:41.580684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd2db22f19f9'
down_revision = '7d0cb4cbf1a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('students', sa.Column('creator_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'students', 'users', ['creator_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'students', type_='foreignkey')
    op.drop_column('students', 'creator_id')
    # ### end Alembic commands ###