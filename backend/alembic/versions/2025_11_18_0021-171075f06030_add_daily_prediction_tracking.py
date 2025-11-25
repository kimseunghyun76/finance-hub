"""add daily prediction tracking

Revision ID: 171075f06030
Revises: 25e25badf3fb
Create Date: 2025-11-18 00:21:52.285478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '171075f06030'
down_revision = '25e25badf3fb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create daily_predictions table
    op.create_table(
        'daily_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(20), nullable=False),
        sa.Column('prediction_date', sa.Date(), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),

        # Prediction data
        sa.Column('predicted_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('predicted_change', sa.Float(), nullable=False),
        sa.Column('predicted_change_percent', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('action', sa.String(10), nullable=False),

        # Actual results (filled after target_date)
        sa.Column('actual_price', sa.Float(), nullable=True),
        sa.Column('actual_change', sa.Float(), nullable=True),
        sa.Column('actual_change_percent', sa.Float(), nullable=True),

        # Accuracy metrics
        sa.Column('price_error', sa.Float(), nullable=True),
        sa.Column('price_error_percent', sa.Float(), nullable=True),
        sa.Column('direction_correct', sa.Boolean(), nullable=True),

        # Metadata
        sa.Column('model_type', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', 'prediction_date', 'target_date', name='uix_ticker_pred_target_date')
    )

    # Create indexes
    op.create_index('idx_daily_predictions_ticker', 'daily_predictions', ['ticker'])
    op.create_index('idx_daily_predictions_prediction_date', 'daily_predictions', ['prediction_date'])
    op.create_index('idx_daily_predictions_target_date', 'daily_predictions', ['target_date'])


def downgrade() -> None:
    op.drop_index('idx_daily_predictions_target_date', table_name='daily_predictions')
    op.drop_index('idx_daily_predictions_prediction_date', table_name='daily_predictions')
    op.drop_index('idx_daily_predictions_ticker', table_name='daily_predictions')
    op.drop_table('daily_predictions')
