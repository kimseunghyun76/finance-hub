"""News and sentiment analysis API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

from app.database import get_db
from app.models.news import NewsArticle, SentimentHistory, SentimentType, NewsSource
from app.services.news_analyzer import NewsAnalyzer
from app.services.news_fetcher import NewsFetcher

router = APIRouter()


# Response models
class NewsArticleResponse(BaseModel):
    id: int
    ticker: str
    title: str
    url: str
    source: NewsSource
    author: Optional[str]
    published_at: datetime
    summary: Optional[str]
    sentiment: Optional[SentimentType]
    sentiment_score: Optional[float]
    confidence: Optional[float]
    keywords: Optional[List[str]]
    category: Optional[str]
    relevance_score: float

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, article: NewsArticle):
        data = {
            'id': article.id,
            'ticker': article.ticker,
            'title': article.title,
            'url': article.url,
            'source': article.source,
            'author': article.author,
            'published_at': article.published_at,
            'summary': article.summary,
            'sentiment': article.sentiment,
            'sentiment_score': article.sentiment_score,
            'confidence': article.confidence,
            'keywords': json.loads(article.keywords) if article.keywords else [],
            'category': article.category,
            'relevance_score': article.relevance_score or 0.5
        }
        return cls(**data)


class SentimentResponse(BaseModel):
    ticker: str
    overall_sentiment: SentimentType
    sentiment_score: float
    confidence: float
    total_articles: int
    positive_count: int
    neutral_count: int
    negative_count: int
    source_count: int
    sources: List[str]
    top_keywords: List[str]
    date: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, history: SentimentHistory):
        data = {
            'ticker': history.ticker,
            'overall_sentiment': history.overall_sentiment,
            'sentiment_score': history.sentiment_score,
            'confidence': history.confidence,
            'total_articles': history.total_articles,
            'positive_count': history.positive_count,
            'neutral_count': history.neutral_count,
            'negative_count': history.negative_count,
            'source_count': history.source_count,
            'sources': json.loads(history.sources) if history.sources else [],
            'top_keywords': json.loads(history.top_keywords) if history.top_keywords else [],
            'date': history.date
        }
        return cls(**data)


@router.get("/news/{ticker}", response_model=List[NewsArticleResponse])
def get_ticker_news(
    ticker: str,
    days: int = Query(7, ge=1, le=30, description="Days of news to fetch"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles"),
    db: Session = Depends(get_db)
):
    """Get news articles for a specific ticker"""

    analyzer = NewsAnalyzer(db)
    articles = analyzer.get_recent_news(ticker, days=days, limit=limit)

    return [NewsArticleResponse.from_orm(article) for article in articles]


@router.post("/news/{ticker}/fetch")
def fetch_ticker_news(
    ticker: str,
    company_name: Optional[str] = Query(None, description="Company name for better search"),
    limit_per_source: int = Query(5, ge=1, le=20, description="Articles per source"),
    db: Session = Depends(get_db)
):
    """Fetch and save new articles for a ticker from all sources"""

    # Fetch from all sources
    fetcher = NewsFetcher()
    articles_data = fetcher.fetch_all_sources(ticker, company_name, limit_per_source)

    if not articles_data:
        return {
            "success": False,
            "message": "No articles found",
            "fetched": 0
        }

    # Save articles with sentiment analysis
    analyzer = NewsAnalyzer(db)
    saved_count = 0

    for article_data in articles_data:
        try:
            analyzer.create_news_article(
                ticker=ticker,
                title=article_data['title'],
                url=article_data['url'],
                source=article_data['source'],
                published_at=article_data['published_at'],
                summary=article_data.get('summary'),
                author=article_data.get('author')
            )
            saved_count += 1
        except Exception as e:
            # Skip duplicates and errors
            continue

    return {
        "success": True,
        "message": f"Fetched and analyzed {saved_count} new articles",
        "fetched": saved_count,
        "total_found": len(articles_data)
    }


@router.get("/sentiment/{ticker}", response_model=SentimentResponse)
def get_ticker_sentiment(
    ticker: str,
    days: int = Query(7, ge=1, le=30, description="Days to analyze"),
    db: Session = Depends(get_db)
):
    """Get aggregated sentiment analysis for a ticker"""

    analyzer = NewsAnalyzer(db)

    # Calculate current sentiment
    sentiment = analyzer.calculate_ticker_sentiment(ticker, days=days)

    if not sentiment:
        raise HTTPException(
            status_code=404,
            detail=f"No sentiment data available for {ticker}"
        )

    return SentimentResponse.from_orm(sentiment)


@router.get("/sentiment/{ticker}/trend", response_model=List[SentimentResponse])
def get_sentiment_trend(
    ticker: str,
    days: int = Query(30, ge=7, le=90, description="Days of history"),
    db: Session = Depends(get_db)
):
    """Get sentiment trend over time"""

    analyzer = NewsAnalyzer(db)
    history = analyzer.get_sentiment_trend(ticker, days=days)

    return [SentimentResponse.from_orm(h) for h in history]


@router.get("/sentiment/dashboard/{ticker}")
def get_sentiment_dashboard(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get complete sentiment dashboard data"""

    analyzer = NewsAnalyzer(db)

    # Current sentiment (7 days)
    current_sentiment = analyzer.calculate_ticker_sentiment(ticker, days=7)

    # Recent news
    recent_news = analyzer.get_recent_news(ticker, days=7, limit=10)

    # Sentiment trend (30 days)
    trend = analyzer.get_sentiment_trend(ticker, days=30)

    return {
        "ticker": ticker,
        "current_sentiment": SentimentResponse.from_orm(current_sentiment) if current_sentiment else None,
        "recent_news": [NewsArticleResponse.from_orm(article) for article in recent_news],
        "sentiment_trend": [SentimentResponse.from_orm(h) for h in trend]
    }


@router.post("/sentiment/analyze-text")
def analyze_text_sentiment(
    text: str,
    db: Session = Depends(get_db)
):
    """Analyze sentiment of arbitrary text (for testing)"""

    analyzer = NewsAnalyzer(db)
    result = analyzer.analyze_sentiment(text)
    sentiment_type = analyzer.score_to_sentiment_type(result['score'])

    return {
        "text": text[:200],  # Return first 200 chars
        "sentiment": sentiment_type,
        "score": result['score'],
        "confidence": result['confidence']
    }
