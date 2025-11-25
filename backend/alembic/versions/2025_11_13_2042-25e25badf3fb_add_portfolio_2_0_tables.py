"""add_portfolio_2_0_tables

Revision ID: 25e25badf3fb
Revises: e0e8f6319347
Create Date: 2025-11-13 20:42:38.139584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25e25badf3fb'
down_revision = 'e0e8f6319347'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stock_info table
    op.create_table(
        'stock_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('asset_type', sa.Enum('STOCK', 'ETF', 'INDEX', 'CRYPTO', name='assettype'), nullable=False),
        sa.Column('sector', sa.Enum('TECHNOLOGY', 'FINANCE', 'HEALTHCARE', 'CONSUMER', 'ENERGY', 'INDUSTRIAL', 'MATERIALS', 'UTILITIES', 'REAL_ESTATE', 'COMMUNICATION', name='sectortype'), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_etf', sa.Integer(), nullable=True),
        sa.Column('etf_category', sa.String(), nullable=True),
        sa.Column('expense_ratio', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_info_id'), 'stock_info', ['id'], unique=False)
    op.create_index(op.f('ix_stock_info_ticker'), 'stock_info', ['ticker'], unique=True)

    # Create portfolio_analytics table
    op.create_table(
        'portfolio_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('total_value', sa.Float(), nullable=False),
        sa.Column('total_return', sa.Float(), nullable=False),
        sa.Column('daily_return', sa.Float(), nullable=True),
        sa.Column('volatility', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('beta', sa.Float(), nullable=True),
        sa.Column('alpha', sa.Float(), nullable=True),
        sa.Column('sector_diversity_score', sa.Float(), nullable=True),
        sa.Column('geographic_diversity_score', sa.Float(), nullable=True),
        sa.Column('concentration_risk', sa.Float(), nullable=True),
        sa.Column('snapshot_date', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('portfolio_id', 'snapshot_date', name='_portfolio_date_uc')
    )
    op.create_index(op.f('ix_portfolio_analytics_id'), 'portfolio_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_portfolio_analytics_snapshot_date'), 'portfolio_analytics', ['snapshot_date'], unique=False)

    # Create stock_recommendations table
    op.create_table(
        'stock_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=True),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('target_weight', sa.Float(), nullable=True),
        sa.Column('reason_category', sa.String(), nullable=False),
        sa.Column('reason_detail', sa.String(), nullable=True),
        sa.Column('ai_prediction_score', sa.Float(), nullable=True),
        sa.Column('technical_score', sa.Float(), nullable=True),
        sa.Column('fundamental_score', sa.Float(), nullable=True),
        sa.Column('diversification_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('expires_at', sa.String(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_recommendations_id'), 'stock_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_stock_recommendations_ticker'), 'stock_recommendations', ['ticker'], unique=False)

    # Create rebalance_proposals table
    op.create_table(
        'rebalance_proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('proposal_type', sa.String(), nullable=False),
        sa.Column('trigger_reason', sa.String(), nullable=False),
        sa.Column('current_risk_score', sa.Float(), nullable=True),
        sa.Column('target_risk_score', sa.Float(), nullable=True),
        sa.Column('current_diversification', sa.Float(), nullable=True),
        sa.Column('target_diversification', sa.Float(), nullable=True),
        sa.Column('proposed_actions', sa.String(), nullable=False),
        sa.Column('expected_return_change', sa.Float(), nullable=True),
        sa.Column('expected_risk_change', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('executed_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rebalance_proposals_id'), 'rebalance_proposals', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_rebalance_proposals_id'), table_name='rebalance_proposals')
    op.drop_table('rebalance_proposals')

    op.drop_index(op.f('ix_stock_recommendations_ticker'), table_name='stock_recommendations')
    op.drop_index(op.f('ix_stock_recommendations_id'), table_name='stock_recommendations')
    op.drop_table('stock_recommendations')

    op.drop_index(op.f('ix_portfolio_analytics_snapshot_date'), table_name='portfolio_analytics')
    op.drop_index(op.f('ix_portfolio_analytics_id'), table_name='portfolio_analytics')
    op.drop_table('portfolio_analytics')

    op.drop_index(op.f('ix_stock_info_ticker'), table_name='stock_info')
    op.drop_index(op.f('ix_stock_info_id'), table_name='stock_info')
    op.drop_table('stock_info')
