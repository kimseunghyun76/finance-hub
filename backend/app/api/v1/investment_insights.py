"""Investment insights API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.investment_insight_service import InvestmentInsightService

router = APIRouter(prefix="/insights", tags=["investment-insights"])


@router.get("/{ticker}")
def get_investment_insight(
    ticker: str,
    refresh: bool = False,
    db: Session = Depends(get_db)
):
    """Get investment insight for a stock ticker

    Args:
        ticker: Stock ticker symbol
        refresh: Force regenerate insight (invalidate cache)
        db: Database session

    Returns:
        Investment insight with Buffett, Lynch, and Graham analyses
    """
    import yfinance as yf

    service = InvestmentInsightService(db)

    # Invalidate cache if refresh requested
    if refresh:
        service.invalidate_cache(ticker)

    # Get real stock data from yfinance
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        stock_data = {
            "price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "market_cap": info.get("marketCap"),
        }
    except Exception as e:
        # Fallback to default values if yfinance fails
        stock_data = {"price": 0, "pe_ratio": None, "market_cap": None}

    # Get or generate insight
    insight = service.get_or_generate_insight(
        ticker=ticker,
        stock_data=stock_data
    )

    if not insight:
        raise HTTPException(status_code=404, detail=f"Unable to generate insight for {ticker}")

    return {
        "ticker": insight.ticker,
        "buffett_analysis": insight.buffett_analysis,
        "lynch_analysis": insight.lynch_analysis,
        "graham_analysis": insight.graham_analysis,
        "overall_rating": insight.overall_rating,
        "confidence_score": insight.confidence_score,
        "current_price": insight.current_price,
        "pe_ratio": insight.pe_ratio,
        "generated_at": insight.generated_at.isoformat() if insight.generated_at else None,
        "expires_at": insight.expires_at.isoformat() if insight.expires_at else None,
    }
