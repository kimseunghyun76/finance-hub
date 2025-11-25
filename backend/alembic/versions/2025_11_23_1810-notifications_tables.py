"""Add notification and notification_settings tables

Revision ID: notifications_001
Revises: 09b4be1be729
Create Date: 2025-11-23 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'notifications_001'
down_revision = '09b4be1be729'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=True, index=True),
        sa.Column('ticker', sa.String(), nullable=True, index=True),
        sa.Column('type', sa.String(), nullable=False, index=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='info'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0', index=True),
        sa.Column('data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), index=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Create notification_settings table
    op.create_table(
        'notification_settings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=True, unique=True, index=True),
        sa.Column('price_alert_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('prediction_update_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('rebalance_alert_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('news_alert_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('portfolio_goal_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('price_change_threshold', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('rebalance_threshold', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now())
    )


def downgrade() -> None:
    op.drop_table('notification_settings')
    op.drop_table('notifications')
