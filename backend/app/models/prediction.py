"""Prediction model for ML results"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum


class ActionType(str, enum.Enum):
    """Trading action types"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ModelType(str, enum.Enum):
    """ML model types"""

    LSTM = "LSTM"
    GRU = "GRU"
    TRANSFORMER = "TRANSFORMER"
    CNN_LSTM = "CNN_LSTM"
    ENSEMBLE = "ENSEMBLE"
    PROPHET = "PROPHET"
    XGBOOST = "XGBOOST"


class Prediction(Base):
    """ML prediction results"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    prediction_date = Column(Date, index=True, nullable=False)  # When prediction was made
    target_date = Column(Date, nullable=False)  # Target prediction date
    predicted_price = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    action = Column(Enum(ActionType), nullable=False)
    model_version = Column(String, nullable=False)
    model_type = Column(Enum(ModelType), nullable=False, server_default="LSTM")  # Model type used
    features = Column(JSON, nullable=True)  # Technical indicators used
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Prediction(ticker={self.ticker}, action={self.action}, confidence={self.confidence})>"
