"""Prediction validation model for tracking accuracy"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PredictionValidation(Base):
    """Daily validation of predictions against actual prices"""

    __tablename__ = "prediction_validations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)

    # Actual data
    actual_price = Column(Float, nullable=False)
    validation_date = Column(Date, nullable=False, index=True)  # Date when validation occurred

    # Accuracy metrics
    price_error = Column(Float, nullable=False)  # Absolute error
    price_error_percent = Column(Float, nullable=False)  # Percentage error
    direction_correct = Column(Boolean, nullable=False)  # Did we predict up/down correctly?

    # Metadata
    validated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    prediction = relationship("Prediction", backref="validations")

    def __repr__(self):
        return f"<PredictionValidation(prediction_id={self.prediction_id}, error={self.price_error_percent:.2f}%)>"


class ModelAccuracy(Base):
    """Aggregated accuracy metrics per model and ticker"""

    __tablename__ = "model_accuracy"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    model_type = Column(String, nullable=False)  # LSTM, GRU, etc.
    model_version = Column(String, nullable=False)

    # Aggregated metrics (last 30 days)
    total_predictions = Column(Integer, default=0)
    correct_direction = Column(Integer, default=0)  # How many times direction was correct
    avg_price_error = Column(Float, default=0.0)  # Average absolute error
    avg_price_error_percent = Column(Float, default=0.0)  # Average percentage error

    # Accuracy scores (0.0 to 1.0)
    direction_accuracy = Column(Float, default=0.0)  # correct_direction / total_predictions
    price_accuracy = Column(Float, default=0.0)  # 1.0 - (avg_price_error_percent / 100)
    overall_accuracy = Column(Float, default=0.0)  # Weighted combination

    # Date range
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ModelAccuracy(ticker={self.ticker}, model={self.model_type}, accuracy={self.overall_accuracy:.2%})>"
