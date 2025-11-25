"""Notification model for user alerts"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    """User notification model"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # None for system-wide
    ticker = Column(String, nullable=True, index=True)
    type = Column(String, nullable=False, index=True)  # 'price_alert', 'prediction_update', 'rebalance_needed', 'news', 'portfolio_goal'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, default='info')  # 'info', 'warning', 'success', 'error'
    is_read = Column(Boolean, default=False, index=True)
    data = Column(Text, nullable=True)  # JSON data for additional info
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)


class NotificationSetting(Base):
    """User notification preferences"""
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, unique=True, index=True)

    # Alert types enabled/disabled
    price_alert_enabled = Column(Boolean, default=True)
    prediction_update_enabled = Column(Boolean, default=True)
    rebalance_alert_enabled = Column(Boolean, default=True)
    news_alert_enabled = Column(Boolean, default=False)
    portfolio_goal_enabled = Column(Boolean, default=True)

    # Thresholds
    price_change_threshold = Column(Float, default=5.0)  # ±5%
    rebalance_threshold = Column(Float, default=5.0)  # 5% deviation

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
