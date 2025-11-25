"""Excluded Ticker Model - Stocks excluded from discovery recommendations"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ExcludedTicker(Base):
    """Tickers excluded from discovery/recommendation lists"""
    __tablename__ = "excluded_tickers"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    reason = Column(String, nullable=True)  # Optional reason for exclusion
    excluded_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ExcludedTicker(ticker={self.ticker})>"
