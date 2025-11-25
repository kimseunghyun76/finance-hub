"""News and sentiment analysis models"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class SentimentType(str, enum.Enum):
    """Sentiment types"""
    VERY_POSITIVE = "VERY_POSITIVE"
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    VERY_NEGATIVE = "VERY_NEGATIVE"


class NewsSource(str, enum.Enum):
    """News sources"""
    YAHOO_FINANCE = "YAHOO_FINANCE"
    GOOGLE_NEWS = "GOOGLE_NEWS"
    REUTERS = "REUTERS"
    BLOOMBERG = "BLOOMBERG"
    SEEKING_ALPHA = "SEEKING_ALPHA"
    FINVIZ = "FINVIZ"
    MANUAL = "MANUAL"


class NewsArticle(Base):
    """News article model"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)

    # Article info
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(Enum(NewsSource), nullable=False)
    author = Column(String(200))
    published_at = Column(DateTime, nullable=False)

    # Content
    summary = Column(Text)
    content = Column(Text)

    # Sentiment analysis
    sentiment = Column(Enum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0

    # Keywords and tags
    keywords = Column(Text)  # JSON array
    category = Column(String(100))  # earnings, merger, scandal, etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Impact tracking
    views_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.5)  # 0.0 to 1.0

    def __repr__(self):
        return f"<NewsArticle {self.ticker}: {self.title[:50]}>"


class SentimentHistory(Base):
    """Historical sentiment tracking for tickers"""
    __tablename__ = "sentiment_history"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)

    # Aggregated sentiment metrics
    overall_sentiment = Column(Enum(SentimentType), nullable=False)
    sentiment_score = Column(Float, nullable=False)  # -1.0 to 1.0
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0

    # Article counts
    total_articles = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)

    # Source diversity
    source_count = Column(Integer, default=0)
    sources = Column(Text)  # JSON array of sources

    # Top keywords
    top_keywords = Column(Text)  # JSON array

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SentimentHistory {self.ticker} on {self.date.date()}: {self.overall_sentiment}>"
