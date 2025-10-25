"""Add quiz_links table for UUID-based links

Revision ID: 003
Revises: f834eaa16412
Create Date: 2025-10-25 00:48:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = 'f834eaa16412'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'quiz_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('link_uuid', sa.String(length=36), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_links_is_active'), 'quiz_links', ['is_active'], unique=False)
    op.create_index(op.f('ix_quiz_links_link_uuid'), 'quiz_links', ['link_uuid'], unique=True)
    op.create_index(op.f('ix_quiz_links_quiz_id'), 'quiz_links', ['quiz_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_quiz_links_quiz_id'), table_name='quiz_links')
    op.drop_index(op.f('ix_quiz_links_link_uuid'), table_name='quiz_links')
    op.drop_index(op.f('ix_quiz_links_is_active'), table_name='quiz_links')
    op.drop_table('quiz_links')
