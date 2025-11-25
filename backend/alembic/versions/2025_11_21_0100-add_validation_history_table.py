"""Add validation_history table

Revision ID: add_validation_history
Revises: e8d2f847d890
Create Date: 2025-11-21 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_validation_history'
down_revision: Union[str, None] = 'e8d2f847d890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'validation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('validation_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('predictions_validated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('predictions_skipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('direction_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('direction_incorrect', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_price_error', sa.Float(), nullable=True),
        sa.Column('avg_price_error_percent', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_validation_history_id'), 'validation_history', ['id'], unique=False)
    op.create_index(op.f('ix_validation_history_validation_date'), 'validation_history', ['validation_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_validation_history_validation_date'), table_name='validation_history')
    op.drop_index(op.f('ix_validation_history_id'), table_name='validation_history')
    op.drop_table('validation_history')
