"""Prediction cache model for storing ML prediction results"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timedelta
from app.database import Base


class PredictionCache(Base):
    """Cache table for storing ML prediction results"""

    __tablename__ = "prediction_cache"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    predicted_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    action = Column(String, nullable=False)  # BUY, SELL, HOLD
    forecast_days = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.utcnow() > self.expires_at

    @classmethod
    def get_cache_duration(cls) -> timedelta:
        """
        Get cache duration for predictions
        Predictions are cached for 24 hours (1 day) to reduce API calls
        """
        return timedelta(hours=24)

    def to_dict(self):
        """Convert cache entry to prediction response dict"""
        return {
            "ticker": self.ticker,
            "prediction": {
                "predicted_price": self.predicted_price,
                "current_price": self.current_price,
                "change": self.change,
                "change_percent": self.change_percent,
                "confidence": self.confidence,
                "forecast_days": self.forecast_days,
            },
            "action": self.action,
            "timestamp": self.created_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }
