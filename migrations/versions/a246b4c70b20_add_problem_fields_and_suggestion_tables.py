"""add problem fields and suggestion tables

Revision ID: a246b4c70b20
Revises: fc1729658468
Create Date: 2026-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a246b4c70b20'
down_revision = 'fc1729658468'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('post', sa.Column('industry', sa.String(length=50), server_default='Other', nullable=False))
    op.add_column('post', sa.Column('country', sa.String(length=100), server_default='General', nullable=False))
    op.add_column('post', sa.Column('status', sa.String(length=20), server_default='open', nullable=False))
    op.create_table('suggestion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['problem_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('suggestion_vote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('suggestion_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('is_good', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['suggestion_id'], ['suggestion.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('suggestion_id', 'user_id', name='uq_suggestion_vote_user')
    )


def downgrade():
    op.drop_table('suggestion_vote')
    op.drop_table('suggestion')
    op.drop_column('post', 'status')
    op.drop_column('post', 'country')
    op.drop_column('post', 'industry')