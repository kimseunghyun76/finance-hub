"""News fetching and sentiment analysis service"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from textblob import TextBlob
import re

from app.models.news import NewsArticle, SentimentHistory, SentimentType, NewsSource

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """News fetching and sentiment analysis engine"""

    def __init__(self, db: Session):
        self.db = db

        # Sentiment score ranges
        self.SENTIMENT_RANGES = {
            SentimentType.VERY_POSITIVE: (0.5, 1.0),
            SentimentType.POSITIVE: (0.1, 0.5),
            SentimentType.NEUTRAL: (-0.1, 0.1),
            SentimentType.NEGATIVE: (-0.5, -0.1),
            SentimentType.VERY_NEGATIVE: (-1.0, -0.5),
        }

        # Financial keywords for enhanced analysis
        self.POSITIVE_KEYWORDS = [
            'growth', 'profit', 'gain', 'surge', 'rally', 'bullish', 'upgrade',
            'beat', 'exceed', 'record', 'strong', 'positive', 'success', 'innovative',
            'expansion', 'revenue', 'earnings beat', 'outperform', 'breakthrough'
        ]

        self.NEGATIVE_KEYWORDS = [
            'loss', 'decline', 'fall', 'crash', 'bearish', 'downgrade', 'miss',
            'weak', 'negative', 'concern', 'risk', 'scandal', 'lawsuit', 'debt',
            'bankruptcy', 'layoff', 'cut', 'underperform', 'warning', 'investigation'
        ]

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using TextBlob and keyword analysis

        Returns:
            {
                'score': float (-1.0 to 1.0),
                'confidence': float (0.0 to 1.0)
            }
        """
        if not text:
            return {'score': 0.0, 'confidence': 0.0}

        # Basic sentiment using TextBlob
        blob = TextBlob(text.lower())
        base_score = blob.sentiment.polarity  # -1.0 to 1.0

        # Keyword-based adjustment
        text_lower = text.lower()
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text_lower)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text_lower)

        # Adjust score based on keywords
        keyword_adjustment = (positive_count - negative_count) * 0.1
        keyword_adjustment = max(-0.3, min(0.3, keyword_adjustment))  # Cap adjustment

        final_score = base_score + keyword_adjustment
        final_score = max(-1.0, min(1.0, final_score))  # Ensure in range

        # Calculate confidence based on text length and keyword presence
        word_count = len(text.split())
        keyword_count = positive_count + negative_count

        confidence = min(1.0, (word_count / 100) * 0.5 + (keyword_count / 5) * 0.5)
        confidence = max(0.1, confidence)  # Minimum confidence

        return {
            'score': final_score,
            'confidence': confidence
        }

    def score_to_sentiment_type(self, score: float) -> SentimentType:
        """Convert sentiment score to sentiment type"""
        for sentiment_type, (min_score, max_score) in self.SENTIMENT_RANGES.items():
            if min_score <= score <= max_score:
                return sentiment_type
        return SentimentType.NEUTRAL

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []

        # Simple keyword extraction (in production, use NLP libraries like spaCy)
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())

        # Filter common words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'would', 'their', 'there'}
        keywords = [w for w in words if w not in stop_words]

        # Count frequency
        from collections import Counter
        word_counts = Counter(keywords)

        return [word for word, _ in word_counts.most_common(max_keywords)]

    def create_news_article(
        self,
        ticker: str,
        title: str,
        url: str,
        source: NewsSource,
        published_at: datetime,
        summary: str = None,
        content: str = None,
        author: str = None,
        category: str = None
    ) -> NewsArticle:
        """Create a news article with sentiment analysis"""

        # Check if article already exists
        existing = self.db.query(NewsArticle).filter(NewsArticle.url == url).first()
        if existing:
            logger.info(f"Article already exists: {url}")
            return existing

        # Analyze sentiment
        analysis_text = f"{title} {summary or ''} {content or ''}"
        sentiment_result = self.analyze_sentiment(analysis_text)

        # Extract keywords
        keywords = self.extract_keywords(analysis_text)

        # Create article
        article = NewsArticle(
            ticker=ticker,
            title=title,
            url=url,
            source=source,
            author=author,
            published_at=published_at,
            summary=summary,
            content=content,
            sentiment=self.score_to_sentiment_type(sentiment_result['score']),
            sentiment_score=sentiment_result['score'],
            confidence=sentiment_result['confidence'],
            keywords=json.dumps(keywords, ensure_ascii=False),
            category=category,
            relevance_score=0.8  # Default relevance
        )

        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)

        logger.info(f"Created news article: {ticker} - {title[:50]} - Sentiment: {article.sentiment}")
        return article

    def get_recent_news(
        self,
        ticker: str,
        days: int = 7,
        limit: int = 20
    ) -> List[NewsArticle]:
        """Get recent news for a ticker"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        articles = (
            self.db.query(NewsArticle)
            .filter(
                NewsArticle.ticker == ticker,
                NewsArticle.published_at >= cutoff_date
            )
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
            .all()
        )

        return articles

    def calculate_ticker_sentiment(
        self,
        ticker: str,
        days: int = 7
    ) -> Optional[SentimentHistory]:
        """Calculate aggregated sentiment for a ticker"""

        articles = self.get_recent_news(ticker, days=days, limit=100)

        if not articles:
            logger.info(f"No articles found for {ticker} in last {days} days")
            return None

        # Aggregate sentiment
        total_articles = len(articles)
        sentiment_counts = {
            SentimentType.VERY_POSITIVE: 0,
            SentimentType.POSITIVE: 0,
            SentimentType.NEUTRAL: 0,
            SentimentType.NEGATIVE: 0,
            SentimentType.VERY_NEGATIVE: 0
        }

        total_score = 0.0
        total_confidence = 0.0
        sources = set()
        all_keywords = []

        for article in articles:
            sentiment_counts[article.sentiment] += 1
            total_score += article.sentiment_score or 0.0
            total_confidence += article.confidence or 0.0
            sources.add(article.source.value)

            if article.keywords:
                try:
                    keywords = json.loads(article.keywords)
                    all_keywords.extend(keywords)
                except:
                    pass

        # Calculate overall sentiment
        avg_score = total_score / total_articles
        avg_confidence = total_confidence / total_articles
        overall_sentiment = self.score_to_sentiment_type(avg_score)

        # Get top keywords
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(10)]

        # Create or update sentiment history
        today = datetime.utcnow().date()
        history = (
            self.db.query(SentimentHistory)
            .filter(
                SentimentHistory.ticker == ticker,
                SentimentHistory.date >= datetime.combine(today, datetime.min.time())
            )
            .first()
        )

        if history:
            # Update existing
            history.overall_sentiment = overall_sentiment
            history.sentiment_score = avg_score
            history.confidence = avg_confidence
            history.total_articles = total_articles
            history.positive_count = sentiment_counts[SentimentType.POSITIVE] + sentiment_counts[SentimentType.VERY_POSITIVE]
            history.neutral_count = sentiment_counts[SentimentType.NEUTRAL]
            history.negative_count = sentiment_counts[SentimentType.NEGATIVE] + sentiment_counts[SentimentType.VERY_NEGATIVE]
            history.source_count = len(sources)
            history.sources = json.dumps(list(sources), ensure_ascii=False)
            history.top_keywords = json.dumps(top_keywords, ensure_ascii=False)
        else:
            # Create new
            history = SentimentHistory(
                ticker=ticker,
                date=datetime.utcnow(),
                overall_sentiment=overall_sentiment,
                sentiment_score=avg_score,
                confidence=avg_confidence,
                total_articles=total_articles,
                positive_count=sentiment_counts[SentimentType.POSITIVE] + sentiment_counts[SentimentType.VERY_POSITIVE],
                neutral_count=sentiment_counts[SentimentType.NEUTRAL],
                negative_count=sentiment_counts[SentimentType.NEGATIVE] + sentiment_counts[SentimentType.VERY_NEGATIVE],
                source_count=len(sources),
                sources=json.dumps(list(sources), ensure_ascii=False),
                top_keywords=json.dumps(top_keywords, ensure_ascii=False)
            )
            self.db.add(history)

        self.db.commit()
        self.db.refresh(history)

        logger.info(f"Calculated sentiment for {ticker}: {overall_sentiment} (score: {avg_score:.3f})")
        return history

    def get_sentiment_trend(
        self,
        ticker: str,
        days: int = 30
    ) -> List[SentimentHistory]:
        """Get sentiment history for trend analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        history = (
            self.db.query(SentimentHistory)
            .filter(
                SentimentHistory.ticker == ticker,
                SentimentHistory.date >= cutoff_date
            )
            .order_by(SentimentHistory.date.asc())
            .all()
        )

        return history
