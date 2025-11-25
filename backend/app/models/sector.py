"""Sector and Industry classification models"""
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SectorType(str, enum.Enum):
    """Major sector categories"""
    TECHNOLOGY = "TECHNOLOGY"
    FINANCE = "FINANCE"
    HEALTHCARE = "HEALTHCARE"
    CONSUMER = "CONSUMER"
    ENERGY = "ENERGY"
    INDUSTRIAL = "INDUSTRIAL"
    MATERIALS = "MATERIALS"
    UTILITIES = "UTILITIES"
    REAL_ESTATE = "REAL_ESTATE"
    COMMUNICATION = "COMMUNICATION"


class AssetType(str, enum.Enum):
    """Asset type classification"""
    STOCK = "STOCK"
    ETF = "ETF"
    INDEX = "INDEX"
    CRYPTO = "CRYPTO"


class StockInfo(Base):
    """Stock/ETF information and classification"""

    __tablename__ = "stock_info"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False, default=AssetType.STOCK)
    sector = Column(Enum(SectorType), nullable=True)
    industry = Column(String, nullable=True)  # More specific than sector
    country = Column(String, nullable=False, default="US")  # US, KR, etc.
    market_cap = Column(Float, nullable=True)  # in billions USD
    description = Column(String, nullable=True)

    # ETF specific fields
    is_etf = Column(Integer, default=0)  # 0 or 1 (SQLite boolean)
    etf_category = Column(String, nullable=True)  # e.g., "Technology", "Market Index"
    expense_ratio = Column(Float, nullable=True)  # For ETFs

    def __repr__(self):
        return f"<StockInfo(ticker={self.ticker}, name={self.name}, sector={self.sector})>"


class PortfolioAnalytics(Base):
    """Portfolio performance analytics (daily snapshot)"""

    __tablename__ = "portfolio_analytics"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)

    # Performance metrics
    total_value = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)  # Percentage
    daily_return = Column(Float, nullable=True)  # Daily change %

    # Risk metrics
    volatility = Column(Float, nullable=True)  # Standard deviation
    sharpe_ratio = Column(Float, nullable=True)  # Risk-adjusted return
    max_drawdown = Column(Float, nullable=True)  # Maximum decline %
    beta = Column(Float, nullable=True)  # vs. market (SPY)
    alpha = Column(Float, nullable=True)  # Excess return vs. market

    # Diversification metrics
    sector_diversity_score = Column(Float, nullable=True)  # 0-100
    geographic_diversity_score = Column(Float, nullable=True)  # 0-100
    concentration_risk = Column(Float, nullable=True)  # Top 5 holdings %

    # Timestamp
    snapshot_date = Column(String, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('portfolio_id', 'snapshot_date', name='_portfolio_date_uc'),
    )

    def __repr__(self):
        return f"<PortfolioAnalytics(portfolio_id={self.portfolio_id}, return={self.total_return:.2f}%)>"


class StockRecommendation(Base):
    """AI-generated stock recommendations"""

    __tablename__ = "stock_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)  # Null = general recommendation
    ticker = Column(String, index=True, nullable=False)

    # Recommendation details
    action = Column(String, nullable=False)  # BUY, SELL, HOLD, ADD, REDUCE
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    target_weight = Column(Float, nullable=True)  # Suggested portfolio weight %

    # Reasoning
    reason_category = Column(String, nullable=False)  # DIVERSIFICATION, AI_PREDICTION, TECHNICAL, FUNDAMENTAL
    reason_detail = Column(String, nullable=True)  # Human-readable explanation

    # Scores contributing to recommendation
    ai_prediction_score = Column(Float, nullable=True)  # From LSTM/GRU
    technical_score = Column(Float, nullable=True)  # RSI, MACD, etc.
    fundamental_score = Column(Float, nullable=True)  # PER, ROE, etc.
    diversification_score = Column(Float, nullable=True)  # How much it improves diversification

    # Metadata
    created_at = Column(String, nullable=False)
    expires_at = Column(String, nullable=False)  # Recommendations expire
    is_active = Column(Integer, default=1)  # 0 or 1

    def __repr__(self):
        return f"<StockRecommendation(ticker={self.ticker}, action={self.action}, confidence={self.confidence_score:.2f})>"


class RebalanceProposal(Base):
    """Portfolio rebalancing proposals"""

    __tablename__ = "rebalance_proposals"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)

    # Proposal details
    proposal_type = Column(String, nullable=False)  # SECTOR_REBALANCE, RISK_REDUCTION, PERIODIC
    trigger_reason = Column(String, nullable=False)  # What triggered this proposal

    # Current vs. target state
    current_risk_score = Column(Float, nullable=True)
    target_risk_score = Column(Float, nullable=True)
    current_diversification = Column(Float, nullable=True)
    target_diversification = Column(Float, nullable=True)

    # Actions (stored as JSON string)
    proposed_actions = Column(String, nullable=False)  # JSON: [{ticker, action, current_weight, target_weight}]

    # Expected impact
    expected_return_change = Column(Float, nullable=True)  # %
    expected_risk_change = Column(Float, nullable=True)  # %

    # Status
    status = Column(String, nullable=False, default="PENDING")  # PENDING, ACCEPTED, REJECTED, EXECUTED
    created_at = Column(String, nullable=False)
    executed_at = Column(String, nullable=True)

    def __repr__(self):
        return f"<RebalanceProposal(portfolio_id={self.portfolio_id}, type={self.proposal_type}, status={self.status})>"
