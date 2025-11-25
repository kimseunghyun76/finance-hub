"""News fetching from various sources"""
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
from bs4 import BeautifulSoup

from app.models.news import NewsSource

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch news from various sources"""

    @staticmethod
    def fetch_yahoo_finance_news(ticker: str, limit: int = 10) -> List[Dict]:
        """Fetch news from Yahoo Finance RSS feed

        Returns list of dicts with: title, url, published_at, summary
        """
        try:
            # Yahoo Finance RSS feed
            rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"

            logger.info(f"Fetching Yahoo Finance news for {ticker}")
            feed = feedparser.parse(rss_url)

            articles = []
            for entry in feed.entries[:limit]:
                try:
                    # Parse published date
                    published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow()

                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'published_at': published,
                        'summary': entry.get('summary', ''),
                        'source': NewsSource.YAHOO_FINANCE,
                        'author': entry.get('author', None)
                    })
                except Exception as e:
                    logger.error(f"Error parsing Yahoo Finance entry: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from Yahoo Finance for {ticker}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance news for {ticker}: {e}")
            return []

    @staticmethod
    def fetch_google_news(ticker: str, company_name: str = None, limit: int = 10) -> List[Dict]:
        """Fetch news from Google News RSS

        Returns list of dicts with: title, url, published_at, summary
        """
        try:
            # Use company name if available, otherwise use ticker
            search_term = company_name if company_name else ticker
            rss_url = f"https://news.google.com/rss/search?q={search_term}+stock&hl=en-US&gl=US&ceid=US:en"

            logger.info(f"Fetching Google News for {search_term}")
            feed = feedparser.parse(rss_url)

            articles = []
            for entry in feed.entries[:limit]:
                try:
                    # Parse published date
                    published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow()

                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'published_at': published,
                        'summary': entry.get('description', ''),
                        'source': NewsSource.GOOGLE_NEWS,
                        'author': entry.get('source', {}).get('title', None)
                    })
                except Exception as e:
                    logger.error(f"Error parsing Google News entry: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from Google News for {search_term}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching Google News for {ticker}: {e}")
            return []

    @staticmethod
    def fetch_finviz_news(ticker: str, limit: int = 10) -> List[Dict]:
        """Fetch news from Finviz (web scraping)

        Returns list of dicts with: title, url, published_at, summary
        """
        try:
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            logger.info(f"Fetching Finviz news for {ticker}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find news table
            news_table = soup.find('table', {'id': 'news-table'})
            if not news_table:
                logger.warning(f"No news table found for {ticker} on Finviz")
                return []

            articles = []
            rows = news_table.find_all('tr')[:limit]

            for row in rows:
                try:
                    # Parse date/time
                    date_cell = row.find('td', align='right')
                    link_cell = row.find('a')

                    if not link_cell:
                        continue

                    title = link_cell.text.strip()
                    url = link_cell.get('href', '')

                    # Parse published time
                    if date_cell:
                        date_text = date_cell.text.strip()
                        # Finviz uses relative times like "Today 3:45PM" or "Dec-15-24"
                        # For simplicity, use current time (in production, parse properly)
                        published_at = datetime.utcnow()
                    else:
                        published_at = datetime.utcnow()

                    articles.append({
                        'title': title,
                        'url': url,
                        'published_at': published_at,
                        'summary': '',
                        'source': NewsSource.FINVIZ,
                        'author': None
                    })

                except Exception as e:
                    logger.error(f"Error parsing Finviz row: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from Finviz for {ticker}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching Finviz news for {ticker}: {e}")
            return []

    @staticmethod
    def fetch_all_sources(
        ticker: str,
        company_name: str = None,
        limit_per_source: int = 5
    ) -> List[Dict]:
        """Fetch news from all available sources

        Returns aggregated list of articles from all sources
        """
        all_articles = []

        # Yahoo Finance
        try:
            yahoo_articles = NewsFetcher.fetch_yahoo_finance_news(ticker, limit_per_source)
            all_articles.extend(yahoo_articles)
        except Exception as e:
            logger.error(f"Failed to fetch Yahoo Finance news: {e}")

        # Google News
        try:
            google_articles = NewsFetcher.fetch_google_news(ticker, company_name, limit_per_source)
            all_articles.extend(google_articles)
        except Exception as e:
            logger.error(f"Failed to fetch Google News: {e}")

        # Finviz
        try:
            finviz_articles = NewsFetcher.fetch_finviz_news(ticker, limit_per_source)
            all_articles.extend(finviz_articles)
        except Exception as e:
            logger.error(f"Failed to fetch Finviz news: {e}")

        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        # Sort by published date (most recent first)
        unique_articles.sort(key=lambda x: x['published_at'], reverse=True)

        logger.info(f"Fetched total {len(unique_articles)} unique articles for {ticker} from all sources")
        return unique_articles
