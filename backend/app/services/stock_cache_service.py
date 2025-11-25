"""Stock data caching service for performance optimization"""
import yfinance as yf
from typing import Dict, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.models.stock_price_cache import StockPriceCache, StockMetadata


class StockCacheService:
    """Service for caching stock data to reduce API calls"""

    # Cache validity periods
    PRICE_CACHE_HOURS = 1  # Price data valid for 1 hour during market hours
    METADATA_CACHE_DAYS = 30  # Static metadata valid for 30 days

    @staticmethod
    def get_stock_price(db: Session, ticker: str, force_refresh: bool = False) -> Tuple[float, float]:
        """
        Get stock price from cache or fetch from API
        Returns: (current_price, previous_close)
        """
        today = date.today()

        if not force_refresh:
            # Check cache first
            cached = (
                db.query(StockPriceCache)
                .filter(
                    StockPriceCache.ticker == ticker,
                    StockPriceCache.price_date == today,
                )
                .first()
            )

            if cached:
                # Check if cache is still valid (within 1 hour)
                cache_age = datetime.now() - cached.cached_at.replace(tzinfo=None)
                if cache_age < timedelta(hours=StockCacheService.PRICE_CACHE_HOURS):
                    return cached.current_price, cached.previous_close

        # Fetch from API
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            previous_close = info.get("previousClose", current_price)

            # Update or create cache
            cached = (
                db.query(StockPriceCache)
                .filter(
                    StockPriceCache.ticker == ticker,
                    StockPriceCache.price_date == today,
                )
                .first()
            )

            if cached:
                cached.current_price = current_price
                cached.previous_close = previous_close
                cached.cached_at = datetime.now()
            else:
                cached = StockPriceCache(
                    ticker=ticker,
                    current_price=current_price,
                    previous_close=previous_close,
                    price_date=today,
                )
                db.add(cached)

            db.commit()
            return current_price, previous_close

        except Exception as e:
            print(f"⚠️ Error fetching price for {ticker}: {e}")
            # Return 0 if fetch fails
            return 0.0, 0.0

    @staticmethod
    def get_stock_metadata(db: Session, ticker: str, force_refresh: bool = False) -> Optional[StockMetadata]:
        """
        Get stock metadata from cache or fetch from API
        Returns: StockMetadata object or None
        """
        if not force_refresh:
            # Check cache first
            metadata = db.query(StockMetadata).filter(StockMetadata.ticker == ticker).first()

            if metadata:
                # Check if cache is still valid (within 30 days)
                cache_age = datetime.now() - metadata.last_updated.replace(tzinfo=None)
                if cache_age < timedelta(days=StockCacheService.METADATA_CACHE_DAYS):
                    return metadata

        # Fetch from API
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            sector = info.get("sector", "Unknown")
            industry = info.get("industry", "Unknown")
            country = info.get("country", "Unknown")

            # Handle Korean stocks
            if ticker.endswith(".KS") or ticker.endswith(".KQ"):
                country = "South Korea"

            dividend_rate = info.get("dividendRate", 0)
            dividend_yield = info.get("dividendYield", 0)

            # Update or create metadata
            metadata = db.query(StockMetadata).filter(StockMetadata.ticker == ticker).first()

            if metadata:
                metadata.sector = sector
                metadata.industry = industry
                metadata.country = country
                metadata.dividend_rate = dividend_rate
                metadata.dividend_yield = dividend_yield
                metadata.last_updated = datetime.now()
            else:
                metadata = StockMetadata(
                    ticker=ticker,
                    sector=sector,
                    industry=industry,
                    country=country,
                    dividend_rate=dividend_rate,
                    dividend_yield=dividend_yield,
                )
                db.add(metadata)

            db.commit()
            db.refresh(metadata)
            return metadata

        except Exception as e:
            print(f"⚠️ Error fetching metadata for {ticker}: {e}")
            return None

    @staticmethod
    def batch_refresh_prices(db: Session, tickers: list[str]) -> Dict[str, Tuple[float, float]]:
        """
        Batch refresh prices for multiple tickers
        Returns: Dict of ticker -> (current_price, previous_close)
        """
        results = {}
        for ticker in tickers:
            try:
                current_price, previous_close = StockCacheService.get_stock_price(
                    db, ticker, force_refresh=True
                )
                results[ticker] = (current_price, previous_close)
            except Exception as e:
                print(f"⚠️ Error refreshing {ticker}: {e}")
                results[ticker] = (0.0, 0.0)

        return results

    @staticmethod
    def cleanup_old_cache(db: Session, days: int = 7) -> int:
        """
        Delete price cache older than specified days
        Returns: Number of records deleted
        """
        cutoff_date = date.today() - timedelta(days=days)
        deleted = (
            db.query(StockPriceCache)
            .filter(StockPriceCache.price_date < cutoff_date)
            .delete()
        )
        db.commit()
        return deleted
