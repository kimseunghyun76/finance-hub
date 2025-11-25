"""Stock schemas"""
from pydantic import BaseModel
from datetime import date
from typing import Optional


class StockInfo(BaseModel):
    """Stock information schema"""

    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    currency: str = "USD"


class StockPrice(BaseModel):
    """Stock price data schema"""

    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None


class StockQuote(BaseModel):
    """Real-time stock quote"""

    ticker: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str


class AnalystRecommendation(BaseModel):
    """Analyst recommendation distribution"""

    strong_buy: int
    buy: int
    hold: int
    sell: int
    strong_sell: int
    period: str


class AnalystPriceTarget(BaseModel):
    """Analyst price target data"""

    ticker: str
    current_price: float
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    target_mean: Optional[float] = None
    target_median: Optional[float] = None
    recommendation_mean: Optional[float] = None  # 1=Strong Buy, 5=Strong Sell
    recommendation_key: Optional[str] = None  # buy, hold, sell, etc.
    number_of_analysts: Optional[int] = None
    recommendations: Optional[list[AnalystRecommendation]] = None


class StockFundamentals(BaseModel):
    """Stock fundamental metrics (valuation, profitability, etc.)"""

    ticker: str

    # Valuation metrics
    trailing_pe: Optional[float] = None  # P/E Ratio (후행)
    forward_pe: Optional[float] = None  # P/E Ratio (전망)
    price_to_book: Optional[float] = None  # PBR (주가순자산비율)
    price_to_sales: Optional[float] = None  # PSR (주가매출비율)
    peg_ratio: Optional[float] = None  # PEG Ratio

    # Profitability metrics
    return_on_equity: Optional[float] = None  # ROE (자기자본이익률)
    return_on_assets: Optional[float] = None  # ROA (총자산이익률)
    profit_margins: Optional[float] = None  # 순이익률
    operating_margins: Optional[float] = None  # 영업이익률

    # Growth metrics
    earnings_growth: Optional[float] = None  # 이익 성장률
    revenue_growth: Optional[float] = None  # 매출 성장률

    # Financial health
    debt_to_equity: Optional[float] = None  # 부채비율
    current_ratio: Optional[float] = None  # 유동비율
    quick_ratio: Optional[float] = None  # 당좌비율

    # Dividend metrics
    dividend_yield: Optional[float] = None  # 배당수익률
    payout_ratio: Optional[float] = None  # 배당성향

    # Risk metrics
    beta: Optional[float] = None  # 베타

    # Price range
    fifty_two_week_high: Optional[float] = None  # 52주 최고가
    fifty_two_week_low: Optional[float] = None  # 52주 최저가
    current_price: Optional[float] = None  # 현재가
