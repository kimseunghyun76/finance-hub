"""Create news and sentiment tables"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models.news import NewsArticle, SentimentHistory

if __name__ == "__main__":
    print("Creating news and sentiment tables...")

    # Create tables
    Base.metadata.create_all(bind=engine, tables=[
        NewsArticle.__table__,
        SentimentHistory.__table__
    ])

    print("✅ News and sentiment tables created successfully!")
