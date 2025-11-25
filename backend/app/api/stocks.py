"""Stock API endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.schemas.stock import StockInfo, StockQuote, AnalystPriceTarget, AnalystRecommendation, StockFundamentals
from app.services.data_fetcher import StockDataFetcher
from app.services.cache import (
    stock_info_cache,
    stock_quote_cache,
    analyst_targets_cache,
    STOCK_INFO_TTL,
    STOCK_QUOTE_TTL,
    ANALYST_TARGETS_TTL,
)
from app.database import get_db
from app.models.sector import StockInfo as StockInfoModel
import httpx
from bs4 import BeautifulSoup
import json
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/{ticker}/info", response_model=StockInfo)
def get_stock_info(ticker: str, db: Session = Depends(get_db)):
    """Get stock information (company name, sector, etc.) with caching"""
    # Check cache first
    cache_key = f"stock_info_{ticker}"
    cached_info = stock_info_cache.get(cache_key)

    if cached_info:
        print(f"✅ Returning cached info for {ticker}")
        return cached_info

    # Check database for Korean name first (optional - table may not exist)
    db_stock = None
    try:
        db_stock = db.query(StockInfoModel).filter(StockInfoModel.ticker == ticker).first()
    except Exception as e:
        # Table doesn't exist yet, skip database lookup
        print(f"⚠️ Database lookup skipped for {ticker}: {str(e)}")

    # Fetch from API
    stock_info = StockDataFetcher.get_stock_info(ticker)

    if not stock_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with ticker {ticker} not found",
        )

    # If Korean stock exists in DB, use Korean name
    if db_stock and (ticker.endswith('.KS') or ticker.endswith('.KQ')):
        stock_info['name'] = db_stock.name
        if db_stock.sector:
            stock_info['sector'] = db_stock.sector.value

    # Cache the result
    stock_info_cache.set(cache_key, stock_info, STOCK_INFO_TTL)
    print(f"💾 Cached stock info for {ticker} (1 hour TTL)")

    return stock_info


@router.get("/{ticker}/quote", response_model=StockQuote)
def get_stock_quote(ticker: str):
    """Get current stock price with caching (5 min TTL)"""
    import yfinance as yf
    from datetime import datetime

    # Check cache first
    cache_key = f"stock_quote_{ticker}"
    cached_quote = stock_quote_cache.get(cache_key)

    if cached_quote:
        print(f"✅ Returning cached quote for {ticker}")
        return cached_quote

    # Fetch from API
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")

        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for ticker {ticker}",
            )

        latest = data.iloc[-1]
        previous_close = stock.info.get("previousClose", latest["Close"])

        change = latest["Close"] - previous_close
        change_percent = (change / previous_close) * 100

        quote = StockQuote(
            ticker=ticker,
            current_price=float(latest["Close"]),
            change=float(change),
            change_percent=float(change_percent),
            volume=int(latest["Volume"]),
            timestamp=datetime.now().isoformat(),
        )

        # Cache the result
        stock_quote_cache.set(cache_key, quote, STOCK_QUOTE_TTL)
        print(f"💾 Cached stock quote for {ticker} (5 min TTL)")

        return quote

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stock quote: {str(e)}",
        )


@router.get("/{ticker}/history")
def get_stock_history(ticker: str, period: str = "1mo"):
    """
    Get historical stock data with caching (1 hour TTL)

    Args:
        ticker: Stock ticker symbol
        period: Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    # Check cache first
    cache_key = f"stock_history_{ticker}_{period}"
    cached_history = stock_info_cache.get(cache_key)

    if cached_history:
        print(f"✅ Returning cached history for {ticker} ({period})")
        return cached_history

    # Fetch from API
    df = StockDataFetcher.fetch_yahoo_finance(ticker, period)

    if df is None or df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical data found for ticker {ticker}",
        )

    # Convert DataFrame to list of dicts
    records = df.to_dict("records")
    result = {"ticker": ticker, "period": period, "data": records}

    # Cache the result
    stock_info_cache.set(cache_key, result, STOCK_INFO_TTL)
    print(f"💾 Cached stock history for {ticker} ({period}) (1 hour TTL)")

    return result


@router.get("/{ticker}/analyst-targets", response_model=AnalystPriceTarget)
def get_analyst_price_targets(ticker: str):
    """
    Get analyst price targets and recommendations with caching (1 hour TTL)

    Returns:
        - Current price
        - Analyst price targets (high, low, mean, median)
        - Recommendation summary (buy/hold/sell distribution)
        - Number of analysts covering the stock
    """
    import yfinance as yf
    from app.services.cache import yfinance_circuit_breaker

    # Check if circuit breaker is open (rate limited)
    if yfinance_circuit_breaker.is_open():
        status_obj = yfinance_circuit_breaker.get_status()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Yahoo Finance API rate limited. Service will resume in {int(status_obj['seconds_remaining'])} seconds."
        )

    # Check cache first
    cache_key = f"analyst_targets_{ticker}"
    cached_targets = analyst_targets_cache.get(cache_key)

    if cached_targets:
        print(f"✅ Returning cached analyst targets for {ticker}")
        return cached_targets

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price
        current_price = info.get("currentPrice")
        if not current_price:
            # Fallback to regularMarketPrice
            current_price = info.get("regularMarketPrice")

        if not current_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price data found for ticker {ticker}",
            )

        # Get analyst recommendations distribution
        recommendations_list = []
        try:
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                # Get last 4 periods (current month and 3 previous months)
                recent_recs = recs.tail(4)
                for idx, row in recent_recs.iterrows():
                    recommendations_list.append(
                        AnalystRecommendation(
                            strong_buy=int(row.get("strongBuy", 0)),
                            buy=int(row.get("buy", 0)),
                            hold=int(row.get("hold", 0)),
                            sell=int(row.get("sell", 0)),
                            strong_sell=int(row.get("strongSell", 0)),
                            period=row.get("period", "unknown"),
                        )
                    )
        except Exception as e:
            print(f"Warning: Could not fetch recommendations: {e}")
            recommendations_list = None

        result = AnalystPriceTarget(
            ticker=ticker,
            current_price=float(current_price),
            target_high=info.get("targetHighPrice"),
            target_low=info.get("targetLowPrice"),
            target_mean=info.get("targetMeanPrice"),
            target_median=info.get("targetMedianPrice"),
            recommendation_mean=info.get("recommendationMean"),
            recommendation_key=info.get("recommendationKey"),
            number_of_analysts=info.get("numberOfAnalystOpinions"),
            recommendations=recommendations_list,
        )

        # Cache the result
        analyst_targets_cache.set(cache_key, result, ANALYST_TARGETS_TTL)
        print(f"💾 Cached analyst targets for {ticker} (1 hour TTL)")

        return result

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)

        # Check if it's a rate limit error
        if "Too Many Requests" in error_msg or "Rate limit" in error_msg or "429" in error_msg:
            yfinance_circuit_breaker.trip(f"Rate limit detected in analyst targets API for {ticker}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Yahoo Finance API rate limited. Please try again in 5 minutes.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analyst data: {error_msg}",
        )


@router.get("/{ticker}/fundamentals", response_model=StockFundamentals)
def get_stock_fundamentals(ticker: str):
    """
    Get stock fundamental metrics with caching (1 hour TTL)

    Returns:
        - Valuation metrics (PER, PBR, PSR, PEG)
        - Profitability metrics (ROE, ROA, margins)
        - Growth metrics (earnings growth, revenue growth)
        - Financial health (debt ratios, liquidity ratios)
        - Dividend metrics (yield, payout ratio)
        - Risk metrics (beta)
        - Price range (52-week high/low)
    """
    import yfinance as yf
    from app.services.cache import yfinance_circuit_breaker

    # Check if circuit breaker is open (rate limited)
    if yfinance_circuit_breaker.is_open():
        status = yfinance_circuit_breaker.get_status()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Yahoo Finance API rate limited. Service will resume in {int(status['seconds_remaining'])} seconds."
        )

    # Check cache first
    cache_key = f"fundamentals_{ticker}"
    cached_fundamentals = stock_info_cache.get(cache_key)

    if cached_fundamentals:
        print(f"✅ Returning cached fundamentals for {ticker}")
        return cached_fundamentals

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')

        fundamentals = StockFundamentals(
            ticker=ticker,
            # Valuation
            trailing_pe=info.get('trailingPE'),
            forward_pe=info.get('forwardPE'),
            price_to_book=info.get('priceToBook'),
            price_to_sales=info.get('priceToSalesTrailing12Months'),
            peg_ratio=info.get('pegRatio'),
            # Profitability
            return_on_equity=info.get('returnOnEquity'),
            return_on_assets=info.get('returnOnAssets'),
            profit_margins=info.get('profitMargins'),
            operating_margins=info.get('operatingMargins'),
            # Growth
            earnings_growth=info.get('earningsGrowth'),
            revenue_growth=info.get('revenueGrowth'),
            # Financial Health
            debt_to_equity=info.get('debtToEquity'),
            current_ratio=info.get('currentRatio'),
            quick_ratio=info.get('quickRatio'),
            # Dividend
            dividend_yield=info.get('dividendYield'),
            payout_ratio=info.get('payoutRatio'),
            # Risk
            beta=info.get('beta'),
            # Price Range
            fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
            fifty_two_week_low=info.get('fiftyTwoWeekLow'),
            current_price=current_price,
        )

        # Cache the result
        stock_info_cache.set(cache_key, fundamentals, STOCK_INFO_TTL)
        print(f"💾 Cached fundamentals for {ticker} (1 hour TTL)")

        return fundamentals

    except Exception as e:
        error_msg = str(e)

        # Check if it's a rate limit error
        if "Too Many Requests" in error_msg or "Rate limit" in error_msg or "429" in error_msg:
            yfinance_circuit_breaker.trip(f"Rate limit detected in fundamentals API for {ticker}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Yahoo Finance API rate limited. Please try again in 5 minutes.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching fundamentals: {error_msg}",
        )


@router.get("/search")
def search_stocks(
    query: str = Query(..., min_length=1, description="Search query (ticker or company name)"),
    limit: int = Query(10, ge=1, le=50, description="Max number of results"),
    db: Session = Depends(get_db)
):
    """
    Search stocks by ticker or company name (LIKE search)

    Args:
        query: Search query (ticker symbol or company name)
        limit: Maximum number of results (default 10, max 50)

    Returns:
        List of matching stocks with ticker, name, country, market info
    """
    try:
        # Convert query to uppercase for ticker matching
        query_upper = query.upper()

        # Search database for Korean stocks first (optional - table may not exist)
        results = []
        try:
            db_stocks = db.query(StockInfoModel).filter(
                or_(
                    StockInfoModel.ticker.ilike(f"%{query_upper}%"),
                    StockInfoModel.name.ilike(f"%{query}%")
                )
            ).limit(limit).all()

            for stock in db_stocks:
                results.append({
                    "ticker": stock.ticker,
                    "name": stock.name,
                    "country": stock.country,
                    "sector": stock.sector.value if stock.sector else None,
                    "is_etf": bool(stock.is_etf),
                    "market": "KRX" if stock.ticker.endswith(('.KS', '.KQ')) else "NYSE/NASDAQ"
                })
        except Exception as e:
            # Table doesn't exist yet, skip database lookup
            print(f"⚠️ Database lookup skipped for search '{query}': {str(e)}")

        # If we have fewer results than limit and query looks like a US ticker, try yfinance
        if len(results) < limit and len(query) <= 5:
            import yfinance as yf

            # Check cache first for yfinance search results
            yf_cache_key = f"yf_search_{query_upper}"
            cached_yf_result = stock_info_cache.get(yf_cache_key)

            if cached_yf_result:
                print(f"✅ Returning cached yfinance search for {query_upper}")
                if not any(r['ticker'] == query_upper for r in results):
                    results.append(cached_yf_result)
            else:
                try:
                    # Try exact ticker match from yfinance
                    stock = yf.Ticker(query_upper)
                    info = stock.info

                    # Check if we got valid data
                    if info.get('symbol') and info.get('longName'):
                        yf_result = {
                            "ticker": query_upper,
                            "name": info.get('longName', query_upper),
                            "country": "US",
                            "sector": info.get('sector'),
                            "is_etf": info.get('quoteType') == 'ETF',
                            "market": info.get('exchange', 'NYSE/NASDAQ')
                        }

                        # Cache the yfinance search result
                        stock_info_cache.set(yf_cache_key, yf_result, STOCK_INFO_TTL)
                        print(f"💾 Cached yfinance search for {query_upper} (1 hour TTL)")

                        # Check if already in results
                        if not any(r['ticker'] == query_upper for r in results):
                            results.append(yf_result)
                except Exception as e:
                    print(f"Could not fetch yfinance data for {query_upper}: {e}")

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching stocks: {str(e)}",
        )


@router.get("/fear-greed")
async def get_fear_greed_index():
    """Get CNN Fear & Greed Index by scraping CNN Business website"""
    cache_key = "fear_greed_index"
    cached_data = stock_info_cache.get(cache_key)

    if cached_data:
        print("✅ Returning cached Fear & Greed Index")
        return cached_data

    try:
        # CNN Fear & Greed Index URL
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.cnn.com/'
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Extract current value
            if data and 'fear_and_greed' in data:
                current_value = data['fear_and_greed']['score']
                rating = data['fear_and_greed']['rating']
                previous_close = data.get('fear_and_greed_historical', {}).get('data', [{}])[-1].get('y', current_value) if data.get('fear_and_greed_historical') else current_value

                # Determine label based on value
                if current_value >= 75:
                    label = "Extreme Greed"
                elif current_value >= 55:
                    label = "Greed"
                elif current_value >= 45:
                    label = "Neutral"
                elif current_value >= 25:
                    label = "Fear"
                else:
                    label = "Extreme Fear"

                result = {
                    "value": current_value,
                    "label": label,
                    "rating": rating,
                    "previous_close": previous_close,
                    "timestamp": data.get('fear_and_greed', {}).get('timestamp', '')
                }

                # Cache for 1 hour
                stock_info_cache.set(cache_key, result, ttl_seconds=3600)

                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to fetch Fear & Greed Index data"
                )

    except httpx.HTTPError as e:
        print(f"HTTP error fetching Fear & Greed Index: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch Fear & Greed Index: {str(e)}"
        )
    except Exception as e:
        print(f"Error fetching Fear & Greed Index: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Fear & Greed Index: {str(e)}"
        )


@router.get("/{ticker}/day-of-week-analysis")
def get_day_of_week_analysis(ticker: str, period: str = "1y"):
    """
    요일별 매매 패턴 분석 - 요일별 평균 수익률과 거래량 분석

    Args:
        ticker: Stock ticker symbol
        period: Analysis period (1mo, 3mo, 6mo, 1y, 2y)

    Returns:
        - 요일별 평균 수익률
        - 요일별 평균 거래량
        - 매수세/매도세가 강한 요일
        - 통계적 유의성
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np

    cache_key = f"dow_analysis_{ticker}_{period}"
    cached_data = stock_info_cache.get(cache_key)

    if cached_data:
        print(f"✅ Returning cached day-of-week analysis for {ticker}")
        return cached_data

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for ticker {ticker}"
            )

        # 요일 추가 (0=Monday, 6=Sunday)
        df['DayOfWeek'] = df.index.dayofweek
        df['DayName'] = df.index.day_name()
        df['Returns'] = df['Close'].pct_change() * 100

        # 요일별 통계
        day_stats = df.groupby('DayName').agg({
            'Returns': ['mean', 'std', 'count'],
            'Volume': 'mean',
            'Close': 'count'
        }).round(4)

        # 요일 순서 정렬
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_names_korean = {
            'Monday': '월요일',
            'Tuesday': '화요일',
            'Wednesday': '수요일',
            'Thursday': '목요일',
            'Friday': '금요일',
            'Saturday': '토요일',
            'Sunday': '일요일'
        }

        results = []
        for day in day_order:
            if day in day_stats.index:
                avg_return = float(day_stats.loc[day, ('Returns', 'mean')])
                avg_volume = int(day_stats.loc[day, ('Volume', 'mean')])
                std_return = float(day_stats.loc[day, ('Returns', 'std')])
                count = int(day_stats.loc[day, ('Returns', 'count')])

                # 매수세/매도세 판단
                if avg_return > 0.2:
                    sentiment = "강한 매수세"
                elif avg_return > 0:
                    sentiment = "약한 매수세"
                elif avg_return > -0.2:
                    sentiment = "약한 매도세"
                else:
                    sentiment = "강한 매도세"

                results.append({
                    'day': day,
                    'day_korean': day_names_korean[day],
                    'avg_return': avg_return,
                    'std_return': std_return,
                    'avg_volume': avg_volume,
                    'sample_count': count,
                    'sentiment': sentiment
                })

        # 최고/최저 수익률 요일
        best_day = max(results, key=lambda x: x['avg_return'])
        worst_day = min(results, key=lambda x: x['avg_return'])
        highest_volume_day = max(results, key=lambda x: x['avg_volume'])

        analysis = {
            'ticker': ticker,
            'period': period,
            'day_stats': results,
            'insights': {
                'best_performing_day': {
                    'day': best_day['day_korean'],
                    'avg_return': best_day['avg_return']
                },
                'worst_performing_day': {
                    'day': worst_day['day_korean'],
                    'avg_return': worst_day['avg_return']
                },
                'highest_volume_day': {
                    'day': highest_volume_day['day_korean'],
                    'avg_volume': highest_volume_day['avg_volume']
                }
            }
        }

        # Cache for 1 day
        stock_info_cache.set(cache_key, analysis, ttl_seconds=86400)
        print(f"💾 Cached day-of-week analysis for {ticker} (1 day TTL)")

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing day-of-week patterns: {str(e)}"
        )


@router.get("/{ticker}/technical-indicators")
def get_technical_indicators(ticker: str):
    """
    기술적 지표 분석 - RSI, MACD, 볼린저 밴드, 이동평균선

    Returns:
        - RSI (상대강도지수)
        - MACD (이동평균수렴확산)
        - 볼린저 밴드 (상단/중간/하단)
        - 이동평균선 (5, 20, 60, 120일)
        - 매매 신호
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np

    cache_key = f"tech_indicators_{ticker}"
    cached_data = stock_quote_cache.get(cache_key)

    if cached_data:
        print(f"✅ Returning cached technical indicators for {ticker}")
        return cached_data

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for ticker {ticker}"
            )

        # RSI 계산
        def calculate_rsi(data, period=14):
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        # MACD 계산
        def calculate_macd(data):
            exp1 = data.ewm(span=12, adjust=False).mean()
            exp2 = data.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            return macd, signal, histogram

        # 볼린저 밴드 계산
        def calculate_bollinger_bands(data, period=20):
            sma = data.rolling(window=period).mean()
            std = data.rolling(window=period).std()
            upper = sma + (std * 2)
            lower = sma - (std * 2)
            return upper, sma, lower

        # 지표 계산
        df['RSI'] = calculate_rsi(df['Close'])
        df['MACD'], df['Signal'], df['Histogram'] = calculate_macd(df['Close'])
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = calculate_bollinger_bands(df['Close'])
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        df['MA120'] = df['Close'].rolling(window=120).mean()

        # 최신 데이터
        latest = df.iloc[-1]
        current_price = float(latest['Close'])

        # 매매 신호 생성
        signals = []

        # RSI 신호
        rsi = float(latest['RSI'])
        if rsi < 30:
            signals.append({'type': 'RSI', 'signal': 'BUY', 'strength': 'STRONG', 'reason': f'과매도 구간 (RSI: {rsi:.1f})'})
        elif rsi > 70:
            signals.append({'type': 'RSI', 'signal': 'SELL', 'strength': 'STRONG', 'reason': f'과매수 구간 (RSI: {rsi:.1f})'})

        # MACD 신호
        macd = float(latest['MACD'])
        signal_line = float(latest['Signal'])
        if macd > signal_line and df.iloc[-2]['MACD'] <= df.iloc[-2]['Signal']:
            signals.append({'type': 'MACD', 'signal': 'BUY', 'strength': 'MODERATE', 'reason': 'MACD 골든크로스'})
        elif macd < signal_line and df.iloc[-2]['MACD'] >= df.iloc[-2]['Signal']:
            signals.append({'type': 'MACD', 'signal': 'SELL', 'strength': 'MODERATE', 'reason': 'MACD 데드크로스'})

        # 볼린저 밴드 신호
        bb_upper = float(latest['BB_Upper'])
        bb_lower = float(latest['BB_Lower'])
        if current_price <= bb_lower:
            signals.append({'type': 'BOLLINGER', 'signal': 'BUY', 'strength': 'MODERATE', 'reason': '볼린저 하단 이탈'})
        elif current_price >= bb_upper:
            signals.append({'type': 'BOLLINGER', 'signal': 'SELL', 'strength': 'MODERATE', 'reason': '볼린저 상단 이탈'})

        # 이동평균선 신호
        ma5 = float(latest['MA5'])
        ma20 = float(latest['MA20'])
        if ma5 > ma20 and df.iloc[-2]['MA5'] <= df.iloc[-2]['MA20']:
            signals.append({'type': 'MA', 'signal': 'BUY', 'strength': 'WEAK', 'reason': '5일선 20일선 골든크로스'})
        elif ma5 < ma20 and df.iloc[-2]['MA5'] >= df.iloc[-2]['MA20']:
            signals.append({'type': 'MA', 'signal': 'SELL', 'strength': 'WEAK', 'reason': '5일선 20일선 데드크로스'})

        result = {
            'ticker': ticker,
            'current_price': current_price,
            'indicators': {
                'rsi': {
                    'value': rsi,
                    'signal': 'BUY' if rsi < 30 else 'SELL' if rsi > 70 else 'NEUTRAL',
                    'level': '과매도' if rsi < 30 else '과매수' if rsi > 70 else '중립'
                },
                'macd': {
                    'macd': macd,
                    'signal': signal_line,
                    'histogram': float(latest['Histogram']),
                    'trend': 'BULLISH' if macd > signal_line else 'BEARISH'
                },
                'bollinger_bands': {
                    'upper': bb_upper,
                    'middle': float(latest['BB_Middle']),
                    'lower': bb_lower,
                    'position': '상단권' if current_price > bb_upper else '하단권' if current_price < bb_lower else '중간권'
                },
                'moving_averages': {
                    'ma5': ma5,
                    'ma20': ma20,
                    'ma60': float(latest['MA60']) if not pd.isna(latest['MA60']) else None,
                    'ma120': float(latest['MA120']) if not pd.isna(latest['MA120']) else None
                }
            },
            'signals': signals,
            'overall_signal': 'BUY' if len([s for s in signals if s['signal'] == 'BUY']) > len([s for s in signals if s['signal'] == 'SELL']) else 'SELL' if len([s for s in signals if s['signal'] == 'SELL']) > len([s for s in signals if s['signal'] == 'BUY']) else 'NEUTRAL'
        }

        # Cache for 5 minutes
        stock_quote_cache.set(cache_key, result, STOCK_QUOTE_TTL)
        print(f"💾 Cached technical indicators for {ticker} (5 min TTL)")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating technical indicators: {str(e)}"
        )


@router.get("/{ticker}/events")
def get_stock_events(ticker: str):
    """
    주요 주식 이벤트 캘린더 - 배당락일, 실적발표일, 옵션만기일

    Returns:
        - 다음 배당락일 및 배당금
        - 다음 실적발표일
        - 옵션만기일 (월별)
        - 이벤트 임팩트 예측
    """
    import yfinance as yf
    from datetime import datetime, timedelta

    cache_key = f"stock_events_{ticker}"
    cached_data = stock_info_cache.get(cache_key)

    if cached_data:
        print(f"✅ Returning cached stock events for {ticker}")
        return cached_data

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        calendar = stock.calendar

        events = []

        # 배당 이벤트
        if info.get('dividendDate'):
            div_date = datetime.fromtimestamp(info['dividendDate'])
            dividend_amount = info.get('dividendRate', info.get('trailingAnnualDividendRate', 0))
            events.append({
                'type': '배당락일',
                'date': div_date.strftime('%Y-%m-%d'),
                'impact': 'MODERATE',
                'description': f'배당금: ${dividend_amount:.2f}',
                'days_until': (div_date - datetime.now()).days
            })

        # 실적발표일
        if calendar is not None and 'Earnings Date' in calendar:
            earnings_dates = calendar['Earnings Date']
            if len(earnings_dates) > 0:
                earnings_date = pd.to_datetime(earnings_dates[0])
                events.append({
                    'type': '실적발표',
                    'date': earnings_date.strftime('%Y-%m-%d'),
                    'impact': 'HIGH',
                    'description': '분기 실적 발표 예정',
                    'days_until': (earnings_date - datetime.now()).days
                })

        # 옵션만기일 (미국 주식: 매월 셋째 금요일)
        def get_next_option_expiry():
            today = datetime.now()
            year = today.year
            month = today.month

            expirations = []
            for i in range(3):  # 다음 3개월
                target_month = month + i
                target_year = year
                if target_month > 12:
                    target_month -= 12
                    target_year += 1

                # 해당 월의 첫 날
                first_day = datetime(target_year, target_month, 1)
                # 첫 금요일 찾기
                days_until_friday = (4 - first_day.weekday()) % 7
                first_friday = first_day + timedelta(days=days_until_friday)
                # 셋째 금요일
                third_friday = first_friday + timedelta(weeks=2)

                if third_friday > today:
                    expirations.append(third_friday)

            return expirations

        option_dates = get_next_option_expiry()
        for opt_date in option_dates:
            events.append({
                'type': '옵션만기일',
                'date': opt_date.strftime('%Y-%m-%d'),
                'impact': 'MODERATE',
                'description': '월간 옵션 만기일 (변동성 증가 가능)',
                'days_until': (opt_date - datetime.now()).days
            })

        # 이벤트를 날짜순으로 정렬
        events.sort(key=lambda x: x['days_until'])

        result = {
            'ticker': ticker,
            'events': events,
            'next_major_event': events[0] if events else None
        }

        # Cache for 1 day
        stock_info_cache.set(cache_key, result, ttl_seconds=86400)
        print(f"💾 Cached stock events for {ticker} (1 day TTL)")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stock events: {str(e)}"
        )


@router.get("/exchange-rate-impact")
def get_exchange_rate_impact():
    """
    USD/KRW 환율 영향 분석 - 환율이 한국 증시에 미치는 영향

    Returns:
        - 현재 USD/KRW 환율
        - 환율 변화 추이
        - 코스피 상관관계
        - 투자 가이드
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np

    cache_key = "exchange_rate_impact"
    cached_data = stock_info_cache.get(cache_key)

    if cached_data:
        print("✅ Returning cached exchange rate impact analysis")
        return cached_data

    try:
        # USD/KRW 환율 데이터
        usdkrw = yf.Ticker("KRW=X")
        usdkrw_data = usdkrw.history(period="3mo")

        # 코스피 데이터
        kospi = yf.Ticker("^KS11")
        kospi_data = kospi.history(period="3mo")

        if usdkrw_data.empty or kospi_data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange rate or KOSPI data not available"
            )

        # 현재 환율
        current_rate = float(usdkrw_data['Close'].iloc[-1])
        prev_rate = float(usdkrw_data['Close'].iloc[-2])
        rate_change = current_rate - prev_rate
        rate_change_pct = (rate_change / prev_rate) * 100

        # 환율 통계
        avg_3m = float(usdkrw_data['Close'].mean())
        max_3m = float(usdkrw_data['Close'].max())
        min_3m = float(usdkrw_data['Close'].min())

        # 환율 수준 판단
        if current_rate > avg_3m + (max_3m - min_3m) * 0.25:
            rate_level = "고환율"
            rate_description = "원화 약세 (달러 강세)"
        elif current_rate < avg_3m - (max_3m - min_3m) * 0.25:
            rate_level = "저환율"
            rate_description = "원화 강세 (달러 약세)"
        else:
            rate_level = "중립"
            rate_description = "환율 안정"

        # 상관관계 분석 (환율 상승 vs 코스피 하락)
        # 두 데이터의 공통 날짜만 사용
        merged = pd.merge(
            usdkrw_data['Close'].rename('USDKRW'),
            kospi_data['Close'].rename('KOSPI'),
            left_index=True,
            right_index=True,
            how='inner'
        )

        if len(merged) > 10:
            correlation = merged['USDKRW'].corr(merged['KOSPI'])
        else:
            correlation = 0

        # 투자 가이드 생성
        guides = []

        if rate_level == "고환율":
            guides.append({
                'category': '수출주',
                'recommendation': 'POSITIVE',
                'reason': '고환율은 수출 기업에 유리 (환차익 발생)'
            })
            guides.append({
                'category': '수입주',
                'recommendation': 'NEGATIVE',
                'reason': '고환율은 수입 비용 증가로 수입 기업에 불리'
            })
            guides.append({
                'category': '외국인 투자',
                'recommendation': 'NEUTRAL',
                'reason': '달러 강세 시 외국인 자금 유출 가능성'
            })
        elif rate_level == "저환율":
            guides.append({
                'category': '수출주',
                'recommendation': 'NEGATIVE',
                'reason': '저환율은 수출 기업의 가격 경쟁력 약화'
            })
            guides.append({
                'category': '수입주',
                'recommendation': 'POSITIVE',
                'reason': '저환율은 수입 비용 감소로 수입 기업에 유리'
            })
            guides.append({
                'category': '외국인 투자',
                'recommendation': 'POSITIVE',
                'reason': '원화 강세 시 외국인 자금 유입 가능성'
            })
        else:
            guides.append({
                'category': '시장 전반',
                'recommendation': 'NEUTRAL',
                'reason': '환율 안정으로 시장 변동성 제한적'
            })

        # 업종별 영향도
        sector_impacts = [
            {
                'sector': '자동차/부품',
                'export_ratio': 'HIGH',
                'impact': 'POSITIVE' if rate_level == "고환율" else 'NEGATIVE' if rate_level == "저환율" else 'NEUTRAL'
            },
            {
                'sector': '반도체',
                'export_ratio': 'HIGH',
                'impact': 'POSITIVE' if rate_level == "고환율" else 'NEGATIVE' if rate_level == "저환율" else 'NEUTRAL'
            },
            {
                'sector': '정유/화학',
                'export_ratio': 'MEDIUM',
                'impact': 'NEUTRAL' if rate_level != "고환율" else 'POSITIVE'
            },
            {
                'sector': '유통/식품',
                'export_ratio': 'LOW',
                'impact': 'NEGATIVE' if rate_level == "고환율" else 'POSITIVE' if rate_level == "저환율" else 'NEUTRAL'
            }
        ]

        result = {
            'current_rate': current_rate,
            'change': rate_change,
            'change_percent': rate_change_pct,
            'rate_level': rate_level,
            'rate_description': rate_description,
            'statistics': {
                'avg_3month': avg_3m,
                'max_3month': max_3m,
                'min_3month': min_3m
            },
            'kospi_correlation': float(correlation),
            'correlation_description': '음의 상관관계 (환율 ↑ → 코스피 ↓)' if correlation < -0.3 else '양의 상관관계 (환율 ↑ → 코스피 ↑)' if correlation > 0.3 else '약한 상관관계',
            'investment_guides': guides,
            'sector_impacts': sector_impacts
        }

        # Cache for 5 minutes
        stock_info_cache.set(cache_key, result, ttl_seconds=300)
        print("💾 Cached exchange rate impact analysis (5 min TTL)")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing exchange rate impact: {str(e)}"
        )


@router.get("/{ticker}/risk-score")
def get_risk_score(ticker: str):
    """
    종합 리스크 점수 계산 - 자체 개발 리스크 평가 모델

    Returns:
        - 종합 리스크 점수 (0-100, 낮을수록 안전)
        - 위험도 등급 (매우 낮음/낮음/보통/높음/매우 높음)
        - 세부 리스크 요소 (변동성, 베타, 낙폭, 유동성)
        - 투자자 성향 매칭
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np

    cache_key = f"risk_score_{ticker}"
    cached_data = stock_quote_cache.get(cache_key)

    if cached_data:
        print(f"✅ Returning cached risk score for {ticker}")
        return cached_data

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        df = stock.history(period="1y")

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for ticker {ticker}"
            )

        # 1. 변동성 리스크 (0-30점)
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # 연간 변동성 (%)
        volatility_score = min(volatility * 0.5, 30)  # 60% 변동성 = 30점

        # 2. 베타 리스크 (0-25점)
        beta = info.get('beta', 1.0)
        if beta is None:
            beta = 1.0
        beta_score = min(abs(beta - 1.0) * 25, 25)  # 베타가 1에서 멀수록 위험

        # 3. 최대낙폭 리스크 (0-30점)
        cummax = df['Close'].cummax()
        drawdown = ((df['Close'] - cummax) / cummax * 100).min()
        max_drawdown = abs(drawdown)
        drawdown_score = min(max_drawdown * 0.6, 30)  # 50% 낙폭 = 30점

        # 4. 유동성 리스크 (0-15점)
        avg_volume = df['Volume'].mean()
        if avg_volume < 100000:
            liquidity_score = 15
        elif avg_volume < 500000:
            liquidity_score = 10
        elif avg_volume < 1000000:
            liquidity_score = 5
        else:
            liquidity_score = 0

        # 종합 리스크 점수
        total_risk_score = volatility_score + beta_score + drawdown_score + liquidity_score

        # 위험도 등급
        if total_risk_score < 20:
            risk_level = "매우 낮음"
            risk_color = "green"
            investor_match = "보수적 투자자"
        elif total_risk_score < 40:
            risk_level = "낮음"
            risk_color = "lightgreen"
            investor_match = "안정 추구 투자자"
        elif total_risk_score < 60:
            risk_level = "보통"
            risk_color = "yellow"
            investor_match = "균형 투자자"
        elif total_risk_score < 80:
            risk_level = "높음"
            risk_color = "orange"
            investor_match = "적극적 투자자"
        else:
            risk_level = "매우 높음"
            risk_color = "red"
            investor_match = "공격적 투자자"

        result = {
            'ticker': ticker,
            'risk_score': round(total_risk_score, 2),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'investor_match': investor_match,
            'risk_breakdown': {
                'volatility': {
                    'score': round(volatility_score, 2),
                    'value': round(volatility, 2),
                    'description': f'연간 변동성 {volatility:.1f}%'
                },
                'beta': {
                    'score': round(beta_score, 2),
                    'value': round(beta, 2),
                    'description': f'시장 대비 민감도 {beta:.2f}'
                },
                'max_drawdown': {
                    'score': round(drawdown_score, 2),
                    'value': round(max_drawdown, 2),
                    'description': f'최대 낙폭 {max_drawdown:.1f}%'
                },
                'liquidity': {
                    'score': round(liquidity_score, 2),
                    'value': int(avg_volume),
                    'description': f'평균 거래량 {int(avg_volume):,}주'
                }
            },
            'recommendation': _get_risk_recommendation(risk_level)
        }

        # Cache for 1 hour
        stock_quote_cache.set(cache_key, result, ttl_seconds=3600)
        print(f"💾 Cached risk score for {ticker} (1 hour TTL)")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating risk score: {str(e)}"
        )


def _get_risk_recommendation(risk_level: str) -> str:
    """리스크 등급별 투자 권고사항"""
    recommendations = {
        "매우 낮음": "안정적인 투자 대상. 장기 보유에 적합하며, 포트폴리오의 핵심 자산으로 활용 가능합니다.",
        "낮음": "비교적 안전한 투자처. 적절한 수익과 안정성을 균형있게 제공합니다.",
        "보통": "중간 수준의 리스크. 분산 투자를 통해 리스크 관리가 필요합니다.",
        "높음": "높은 변동성 주의. 단기 투자 또는 소액 비중으로 접근하세요.",
        "매우 높음": "매우 높은 리스크. 투자 경험이 풍부하고 손실 감내 능력이 있는 투자자만 고려하세요."
    }
    return recommendations.get(risk_level, "투자에 주의가 필요합니다.")


@router.get("/{ticker}/anomaly-detection")
def detect_anomalies(ticker: str):
    """
    이상 거래 탐지 시스템 - 통계 기반 이상 징후 감지

    Returns:
        - 가격 이상 징후 (Z-score 기반)
        - 거래량 이상 징후
        - 급등/급락 알림
        - 패턴 이탈 감지
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    cache_key = f"anomaly_{ticker}"
    cached_data = stock_quote_cache.get(cache_key)

    if cached_data:
        print(f"✅ Returning cached anomaly detection for {ticker}")
        return cached_data

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")

        if df.empty or len(df) < 20:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insufficient data for ticker {ticker}"
            )

        # 일일 수익률 계산
        df['Returns'] = df['Close'].pct_change() * 100

        # 1. 가격 이상 징후 (Z-score 분석)
        price_mean = df['Close'].mean()
        price_std = df['Close'].std()
        latest_price = df['Close'].iloc[-1]
        price_zscore = (latest_price - price_mean) / price_std if price_std > 0 else 0

        price_anomaly = {
            'detected': bool(abs(price_zscore) > 2),
            'zscore': float(round(price_zscore, 2)),
            'type': '급등' if price_zscore > 2 else '급락' if price_zscore < -2 else '정상',
            'severity': '높음' if abs(price_zscore) > 3 else '보통' if abs(price_zscore) > 2 else '낮음'
        }

        # 2. 거래량 이상 징후
        volume_mean = df['Volume'].mean()
        volume_std = df['Volume'].std()
        latest_volume = df['Volume'].iloc[-1]
        volume_zscore = (latest_volume - volume_mean) / volume_std if volume_std > 0 else 0

        volume_anomaly = {
            'detected': bool(volume_zscore > 2),
            'zscore': float(round(volume_zscore, 2)),
            'type': '거래량 급증' if volume_zscore > 2 else '정상',
            'volume_vs_avg': float(round((latest_volume / volume_mean - 1) * 100, 1) if volume_mean > 0 else 0)
        }

        # 3. 급등/급락 감지 (일일 수익률)
        returns_mean = df['Returns'].mean()
        returns_std = df['Returns'].std()
        latest_return = df['Returns'].iloc[-1]
        return_zscore = (latest_return - returns_mean) / returns_std if returns_std > 0 else 0

        price_movement = {
            'detected': bool(abs(return_zscore) > 2),
            'daily_return': float(round(latest_return, 2)),
            'zscore': float(round(return_zscore, 2)),
            'type': '급등' if return_zscore > 2 else '급락' if return_zscore < -2 else '정상'
        }

        # 4. 연속 상승/하락 감지
        consecutive_up = 0
        consecutive_down = 0
        for ret in df['Returns'].iloc[-10:]:
            if ret > 0:
                consecutive_up += 1
                consecutive_down = 0
            elif ret < 0:
                consecutive_down += 1
                consecutive_up = 0
            else:
                break

        pattern = {
            'consecutive_up_days': consecutive_up,
            'consecutive_down_days': consecutive_down,
            'pattern_alert': consecutive_up >= 5 or consecutive_down >= 5,
            'pattern_type': f'{consecutive_up}일 연속 상승' if consecutive_up >= 3 else f'{consecutive_down}일 연속 하락' if consecutive_down >= 3 else '변동성 장세'
        }

        # 종합 이상 감지
        anomalies_detected = []
        if price_anomaly['detected']:
            anomalies_detected.append(f"가격 {price_anomaly['type']}")
        if volume_anomaly['detected']:
            anomalies_detected.append("거래량 급증")
        if price_movement['detected']:
            anomalies_detected.append(f"일일 수익률 {price_movement['type']}")
        if pattern['pattern_alert']:
            anomalies_detected.append(pattern['pattern_type'])

        overall_status = "이상 감지" if anomalies_detected else "정상"

        result = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'anomalies': anomalies_detected,
            'analysis': {
                'price_anomaly': price_anomaly,
                'volume_anomaly': volume_anomaly,
                'price_movement': price_movement,
                'pattern': pattern
            },
            'alert_level': '높음' if len(anomalies_detected) >= 3 else '보통' if len(anomalies_detected) >= 1 else '낮음'
        }

        # Cache for 5 minutes
        stock_quote_cache.set(cache_key, result, ttl_seconds=300)
        print(f"💾 Cached anomaly detection for {ticker} (5 min TTL)")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting anomalies: {str(e)}"
        )
