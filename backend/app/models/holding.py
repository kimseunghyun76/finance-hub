"""Holding model"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MarketType(str, enum.Enum):
    """Stock market types"""

    KRX = "KRX"  # Korean Exchange
    NYSE = "NYSE"  # New York Stock Exchange
    NASDAQ = "NASDAQ"  # NASDAQ


class Holding(Base):
    """Stock holding model"""

    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    ticker = Column(String, index=True, nullable=False)  # e.g., "005930.KS" for Samsung
    company_name = Column(String, nullable=True)
    market = Column(Enum(MarketType), nullable=False)
    quantity = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)  # Average purchase price
    purchase_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")

    def __repr__(self):
        return f"<Holding(id={self.id}, ticker={self.ticker}, quantity={self.quantity})>"
