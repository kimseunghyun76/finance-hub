"""add_model_type_to_predictions

Revision ID: e0e8f6319347
Revises: ec11e7a3f1da
Create Date: 2025-11-13 05:52:16.740845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0e8f6319347'
down_revision = 'ec11e7a3f1da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add model_type column with LSTM as default
    op.add_column('predictions',
        sa.Column('model_type',
                  sa.Enum('LSTM', 'GRU', 'TRANSFORMER', 'CNN_LSTM', 'ENSEMBLE', 'PROPHET', 'XGBOOST', name='modeltype'),
                  nullable=False,
                  server_default='LSTM'))


def downgrade() -> None:
    # Remove model_type column
    op.drop_column('predictions', 'model_type')
