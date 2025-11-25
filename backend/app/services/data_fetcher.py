"""Data fetching service for stock prices"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


class StockDataFetcher:
    """Fetch stock data from various sources"""

    @staticmethod
    def fetch_yahoo_finance(ticker: str, period: str = "5y") -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance (supports both US and Korean stocks)

        Args:
            ticker: Stock ticker (e.g., "AAPL" for Apple, "005930.KS" for Samsung)
            period: Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)

            if df.empty:
                print(f"No data found for {ticker}")
                return None

            # Rename columns to lowercase
            df.columns = [col.lower() for col in df.columns]
            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]

            return df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    @staticmethod
    def fetch_korean_stock(ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch Korean stock data using FinanceDataReader

        Args:
            ticker: Korean stock code (e.g., "005930" for Samsung)

        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            import FinanceDataReader as fdr

            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * 5)  # 5 years

            df = fdr.DataReader(ticker, start_date, end_date)

            if df.empty:
                print(f"No data found for {ticker}")
                return None

            # Rename columns to match our schema
            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]

            return df
        except Exception as e:
            print(f"Error fetching Korean stock {ticker}: {e}")
            return None

    @staticmethod
    def get_current_price(ticker: str) -> Optional[float]:
        """
        Get current/latest price for a ticker

        Args:
            ticker: Stock ticker

        Returns:
            Current price or None if error
        """
        try:
            stock = yf.Ticker(ticker)

            # Try history first with multiple column name variations
            data = stock.history(period="1d")
            if not data.empty:
                # Try different column name variations (case-insensitive)
                for col in ['Close', 'close', 'CLOSE']:
                    if col in data.columns:
                        return float(data[col].iloc[-1])

            # Fallback to info API for current price
            info = stock.info
            if info:
                # Try multiple price fields from info
                for field in ['currentPrice', 'regularMarketPrice', 'previousClose']:
                    price = info.get(field)
                    if price and price > 0:
                        return float(price)

            return None
        except Exception as e:
            print(f"Error getting current price for {ticker}: {e}")
            return None

    @staticmethod
    def get_stock_info(ticker: str) -> Optional[dict]:
        """
        Get stock information (company name, sector, etc.)

        Args:
            ticker: Stock ticker

        Returns:
            Dictionary with stock info or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "ticker": ticker,
                "name": info.get("longName", "Unknown"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "currency": info.get("currency", "USD"),
            }
        except Exception as e:
            print(f"Error getting stock info for {ticker}: {e}")
            return None

    @staticmethod
    def get_exchange_rate(from_currency: str = "KRW", to_currency: str = "USD") -> Optional[float]:
        """
        Get current exchange rate between two currencies

        Args:
            from_currency: Source currency code (e.g., "KRW")
            to_currency: Target currency code (e.g., "USD")

        Returns:
            Exchange rate or None if error
        """
        try:
            # Use Yahoo Finance to get exchange rate
            # Format: XXXYYY=X (e.g., KRWUSD=X for KRW to USD)
            ticker = f"{from_currency}{to_currency}=X"
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")

            if data.empty:
                # Fallback: try inverse rate
                inverse_ticker = f"{to_currency}{from_currency}=X"
                stock = yf.Ticker(inverse_ticker)
                data = stock.history(period="1d")

                if data.empty:
                    print(f"No exchange rate data found for {from_currency} to {to_currency}")
                    return None

                # Return inverse rate
                return 1.0 / float(data['close'].iloc[-1])

            return float(data['close'].iloc[-1])
        except Exception as e:
            print(f"Error getting exchange rate {from_currency} to {to_currency}: {e}")
            return None


# Test function
if __name__ == "__main__":
    fetcher = StockDataFetcher()

    print("Testing US stock (Apple)...")
    aapl_data = fetcher.fetch_yahoo_finance("AAPL", period="1mo")
    if aapl_data is not None:
        print(f"✅ Fetched {len(aapl_data)} rows for AAPL")
        print(aapl_data.head())

    print("\n" + "="*50 + "\n")

    print("Testing Korean stock (Samsung Electronics)...")
    samsung_data = fetcher.fetch_yahoo_finance("005930.KS", period="1mo")
    if samsung_data is not None:
        print(f"✅ Fetched {len(samsung_data)} rows for Samsung")
        print(samsung_data.head())

    print("\n" + "="*50 + "\n")

    print("Testing current price...")
    aapl_price = fetcher.get_current_price("AAPL")
    print(f"Current AAPL price: ${aapl_price}")

    print("\n" + "="*50 + "\n")

    print("Testing stock info...")
    info = fetcher.get_stock_info("AAPL")
    if info:
        print(f"Company: {info['name']}")
        print(f"Sector: {info['sector']}")
        print(f"Market Cap: ${info['market_cap']:,}")
