"""Stock screening and discovery service"""
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd


class StockScreener:
    """Screen and discover new investment opportunities"""

    # Major US stocks (NASDAQ-100 and S&P 500 most liquid)
    US_TOP_STOCKS = [
        # Tech Giants
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
        # Semiconductors
        'AMD', 'INTC', 'QCOM', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MCHP',
        # Software & Cloud
        'ORCL', 'CRM', 'ADBE', 'NOW', 'INTU', 'PLTR', 'SNOW', 'DDOG',
        # Communication
        'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS',
        # E-commerce & Retail
        'SHOP', 'MELI', 'EBAY', 'ETSY',
        # Finance
        'V', 'MA', 'PYPL', 'SQ', 'JPM', 'BAC', 'WFC', 'GS',
        # Healthcare & Biotech
        'UNH', 'JNJ', 'PFE', 'ABBV', 'TMO', 'ABT', 'AMGN', 'GILD',
        # Consumer
        'COST', 'WMT', 'HD', 'NKE', 'SBUX', 'MCD', 'PEP', 'KO',
        # Energy
        'XOM', 'CVX', 'COP', 'SLB',
        # Industrial
        'BA', 'CAT', 'GE', 'HON', 'UPS', 'RTX',
    ]

    # Major Korean stocks (KOSPI top companies)
    KR_TOP_STOCKS = [
        # Electronics & Semiconductors
        '005930.KS',  # Samsung Electronics
        '000660.KS',  # SK Hynix
        '006400.KS',  # Samsung SDI

        # Internet & Platform
        '035420.KS',  # NAVER
        '035720.KS',  # Kakao
        '376300.KS',  # Coupang (may not work, NYSE-listed)

        # Automotive
        '005380.KS',  # Hyundai Motor
        '000270.KS',  # Kia

        # Battery & Energy
        '051910.KS',  # LG Chem
        '373220.KS',  # LG Energy Solution

        # Bio & Healthcare
        '207940.KS',  # Samsung Biologics
        '068270.KS',  # Celltrion
        '326030.KS',  # SK Biopharmaceuticals

        # Finance
        '105560.KS',  # KB Financial
        '055550.KS',  # Shinhan Financial
        '086790.KS',  # Hana Financial

        # Steel & Materials
        '005490.KS',  # POSCO Holdings

        # Entertainment
        '035900.KS',  # JYP Entertainment
        '041510.KS',  # SM Entertainment
        '352820.KS',  # Hybe
    ]

    @classmethod
    def get_top_stocks_by_market(cls, market: str = 'US', limit: int = 50) -> List[str]:
        """
        Get top stocks by market capitalization

        Args:
            market: 'US' or 'KR'
            limit: Maximum number of stocks to return

        Returns:
            List of ticker symbols
        """
        if market == 'US':
            return cls.US_TOP_STOCKS[:limit]
        elif market == 'KR':
            return cls.KR_TOP_STOCKS[:limit]
        else:
            return []

    @classmethod
    def get_all_top_stocks(cls, us_limit: int = 50, kr_limit: int = 20) -> List[str]:
        """Get combined list of top US and Korean stocks"""
        return (
            cls.US_TOP_STOCKS[:us_limit] +
            cls.KR_TOP_STOCKS[:kr_limit]
        )

    @staticmethod
    def detect_volume_spike(ticker: str, spike_threshold: float = 2.0) -> Optional[Dict]:
        """
        Detect if stock has unusual volume spike

        Args:
            ticker: Stock ticker symbol
            spike_threshold: Multiple of average volume (default: 2.0 = 200%)

        Returns:
            Dict with spike info or None
        """
        try:
            stock = yf.Ticker(ticker)
            # Get last 30 days of data
            df = stock.history(period='1mo')

            if df.empty or len(df) < 5:
                return None

            # Calculate average volume (excluding today)
            avg_volume = df['Volume'][:-1].mean()
            current_volume = df['Volume'].iloc[-1]

            if current_volume > avg_volume * spike_threshold:
                return {
                    'ticker': ticker,
                    'current_volume': int(current_volume),
                    'avg_volume': int(avg_volume),
                    'spike_ratio': round(current_volume / avg_volume, 2),
                    'detected_at': datetime.utcnow().isoformat()
                }

            return None

        except Exception as e:
            print(f"Error detecting volume spike for {ticker}: {e}")
            return None

    @staticmethod
    def detect_price_movement(ticker: str, days: int = 5, threshold: float = 10.0) -> Optional[Dict]:
        """
        Detect significant price movements

        Args:
            ticker: Stock ticker symbol
            days: Number of days to analyze
            threshold: Percentage change threshold (default: 10%)

        Returns:
            Dict with movement info or None
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=f'{days}d')

            if df.empty or len(df) < 2:
                return None

            start_price = df['Close'].iloc[0]
            end_price = df['Close'].iloc[-1]
            change_percent = ((end_price - start_price) / start_price) * 100

            if abs(change_percent) >= threshold:
                return {
                    'ticker': ticker,
                    'days': days,
                    'start_price': float(start_price),
                    'end_price': float(end_price),
                    'change_percent': round(change_percent, 2),
                    'direction': 'up' if change_percent > 0 else 'down',
                    'detected_at': datetime.utcnow().isoformat()
                }

            return None

        except Exception as e:
            print(f"Error detecting price movement for {ticker}: {e}")
            return None

    @staticmethod
    def get_stock_basic_info(ticker: str) -> Optional[Dict]:
        """
        Get basic stock information for screening

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with stock info or None
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
            }

        except Exception as e:
            print(f"Error getting basic info for {ticker}: {e}")
            return None

    @classmethod
    def screen_untrained_opportunities(
        cls,
        trained_tickers: List[str],
        market: str = 'ALL',
        check_volume_spike: bool = True,
        check_price_movement: bool = True
    ) -> Dict:
        """
        Screen for untrained stocks that might be good opportunities

        Args:
            trained_tickers: List of already trained tickers
            market: 'US', 'KR', or 'ALL'
            check_volume_spike: Whether to check for volume spikes
            check_price_movement: Whether to check for price movements

        Returns:
            Dict with untrained stocks and signals
        """
        # Get candidate stocks
        if market == 'ALL':
            candidates = cls.get_all_top_stocks()
        else:
            candidates = cls.get_top_stocks_by_market(market)

        # Filter out already trained
        untrained = [t for t in candidates if t not in trained_tickers]

        results = {
            'untrained_stocks': [],
            'volume_spikes': [],
            'price_movements': [],
            'high_priority': []  # Stocks with multiple signals
        }

        for ticker in untrained:
            stock_info = cls.get_stock_basic_info(ticker)
            if not stock_info:
                continue

            signals = []

            # Check volume spike
            if check_volume_spike:
                volume_spike = cls.detect_volume_spike(ticker)
                if volume_spike:
                    results['volume_spikes'].append(volume_spike)
                    signals.append('volume_spike')

            # Check price movement
            if check_price_movement:
                price_movement = cls.detect_price_movement(ticker)
                if price_movement:
                    results['price_movements'].append(price_movement)
                    signals.append('price_movement')

            # Add to results
            stock_info['signals'] = signals
            results['untrained_stocks'].append(stock_info)

            # High priority if multiple signals
            if len(signals) >= 2:
                results['high_priority'].append(stock_info)

        return results
