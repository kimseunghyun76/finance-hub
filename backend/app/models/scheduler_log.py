"""Scheduler log model for storing job execution history"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from app.database import Base


class SchedulerLog(Base):
    """Log table for storing scheduler job execution history"""

    __tablename__ = "scheduler_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=False)  # e.g., 'collect_prices', 'train_portfolio'
    job_name = Column(String, nullable=False)  # Human readable name
    status = Column(String, nullable=False)  # 'started', 'completed', 'failed'
    message = Column(Text, nullable=True)  # Detailed message or error
    success_count = Column(Integer, default=0)  # Number of successful operations
    failed_count = Column(Integer, default=0)  # Number of failed operations
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Execution duration

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_name": self.job_name,
            "status": self.status,
            "message": self.message,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }
