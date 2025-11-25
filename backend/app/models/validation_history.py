"""
Validation History Model
Stores validation run history for tracking accuracy over time
"""
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ValidationHistory(Base):
    """Tracks each validation run with aggregated metrics"""

    __tablename__ = "validation_history"

    id = Column(Integer, primary_key=True, index=True)

    # Validation metrics
    validation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    predictions_validated = Column(Integer, nullable=False, default=0)
    predictions_skipped = Column(Integer, nullable=False, default=0)

    # Success metrics
    direction_correct = Column(Integer, nullable=False, default=0)
    direction_incorrect = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=False, default=0.0)

    # Price error metrics
    avg_price_error = Column(Float, nullable=True)
    avg_price_error_percent = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ValidationHistory(date={self.validation_date}, validated={self.predictions_validated}, success_rate={self.success_rate:.2f}%)>"
