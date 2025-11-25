"""Portfolio snapshot model for historical tracking"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PortfolioSnapshot(Base):
    """Daily snapshot of portfolio performance for historical tracking"""

    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)

    # Portfolio values
    total_value = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    total_gain_loss = Column(Float, nullable=False)
    total_return_percent = Column(Float, nullable=False)

    # Daily changes
    daily_change = Column(Float, nullable=False)
    daily_change_percent = Column(Float, nullable=False)

    # Holdings count
    holdings_count = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    portfolio = relationship("Portfolio", back_populates="snapshots")

    def __repr__(self):
        return f"<PortfolioSnapshot(portfolio_id={self.portfolio_id}, date={self.snapshot_date}, value={self.total_value})>"
