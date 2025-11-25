"""Education models for AI-generated investment lessons"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class LevelType(str, enum.Enum):
    """Education level types"""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CategoryType(str, enum.Enum):
    """Education category types"""
    TERM = "용어"
    TIP = "팁"
    ANALYSIS = "분석기법"


class EducationArticle(Base):
    """AI-generated education article"""

    __tablename__ = "education_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # 용어, 팁, 분석기법
    level = Column(String(50), nullable=False)  # beginner, elementary, intermediate, advanced
    content = Column(Text, nullable=False)  # JSON string of conversation messages
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<EducationArticle(id={self.id}, title={self.title}, level={self.level})>"


class UserProgress(Base):
    """Track user's education progress"""

    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # nullable for guest users
    article_id = Column(Integer, nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, article_id={self.article_id})>"
