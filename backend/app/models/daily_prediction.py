"""
Daily Prediction Tracking Model
Stores daily predictions and tracks accuracy
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class DailyPrediction(Base):
    __tablename__ = "daily_predictions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False, index=True)
    target_date = Column(Date, nullable=False, index=True)

    # Prediction data
    predicted_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    predicted_change = Column(Float, nullable=False)
    predicted_change_percent = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    action = Column(String(10), nullable=False)

    # Actual results (filled after target_date)
    actual_price = Column(Float, nullable=True)
    actual_change = Column(Float, nullable=True)
    actual_change_percent = Column(Float, nullable=True)

    # Accuracy metrics
    price_error = Column(Float, nullable=True)
    price_error_percent = Column(Float, nullable=True)
    direction_correct = Column(Boolean, nullable=True)

    # Metadata
    model_type = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
