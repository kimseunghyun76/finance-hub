"""Stock price cache model for performance optimization"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base


class StockPriceCache(Base):
    """Cache for stock prices to reduce API calls"""

    __tablename__ = "stock_price_cache"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)

    # Price data
    current_price = Column(Float, nullable=False)
    previous_close = Column(Float, nullable=False)

    # Metadata
    price_date = Column(Date, nullable=False, index=True)  # Trading date
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<StockPriceCache(ticker={self.ticker}, price={self.current_price}, date={self.price_date})>"


class StockMetadata(Base):
    """Static stock metadata that rarely changes"""

    __tablename__ = "stock_metadata"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)

    # Static information
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)

    # Dividend information (updates quarterly/annually)
    dividend_rate = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<StockMetadata(ticker={self.ticker}, sector={self.sector}, country={self.country})>"
