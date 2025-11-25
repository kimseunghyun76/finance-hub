"""Portfolio API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.database import get_db
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioWithHoldings,
)
from app.services.portfolio_service import PortfolioService
from app.services.portfolio_performance import PortfolioPerformanceService
from app.services.portfolio_advanced import PortfolioAdvancedService

router = APIRouter()


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: PortfolioCreate,
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db),
):
    """Create a new portfolio"""
    return PortfolioService.create_portfolio(db, portfolio, user_id)


@router.get("/", response_model=List[PortfolioResponse])
def get_portfolios(
    user_id: int = 1,  # TODO: Get from authentication
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all portfolios for current user"""
    return PortfolioService.get_portfolios_by_user(db, user_id, skip, limit)


@router.get("/{portfolio_id}", response_model=PortfolioWithHoldings)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get portfolio by ID with holdings"""
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    db: Session = Depends(get_db),
):
    """Update portfolio"""
    portfolio = PortfolioService.update_portfolio(db, portfolio_id, portfolio_update)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Delete portfolio"""
    success = PortfolioService.delete_portfolio(db, portfolio_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return None


# 새로운 성과 분석 API들
@router.get("/{portfolio_id}/performance", response_model=Dict)
def get_portfolio_performance(portfolio_id: int, db: Session = Depends(get_db)):
    """포트폴리오 성과 분석"""
    performance = PortfolioPerformanceService.calculate_portfolio_performance(db, portfolio_id)
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return performance


@router.get("/{portfolio_id}/allocation", response_model=Dict)
def get_asset_allocation(portfolio_id: int, db: Session = Depends(get_db)):
    """자산 배분 분석"""
    allocation = PortfolioPerformanceService.calculate_asset_allocation(db, portfolio_id)
    return allocation


@router.get("/{portfolio_id}/dividends", response_model=Dict)
def get_dividend_income(portfolio_id: int, db: Session = Depends(get_db)):
    """배당금 수익 분석"""
    dividends = PortfolioPerformanceService.calculate_dividend_income(db, portfolio_id)
    return dividends


@router.get("/{portfolio_id}/risk", response_model=Dict)
def get_risk_metrics(portfolio_id: int, db: Session = Depends(get_db)):
    """리스크 분석"""
    risk = PortfolioPerformanceService.calculate_risk_metrics(db, portfolio_id)
    return risk


@router.get("/{portfolio_id}/summary", response_model=Dict)
def get_portfolio_summary(portfolio_id: int, db: Session = Depends(get_db)):
    """포트폴리오 종합 요약 (모든 분석 데이터)"""
    performance = PortfolioPerformanceService.calculate_portfolio_performance(db, portfolio_id)
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )

    allocation = PortfolioPerformanceService.calculate_asset_allocation(db, portfolio_id)
    dividends = PortfolioPerformanceService.calculate_dividend_income(db, portfolio_id)
    risk = PortfolioPerformanceService.calculate_risk_metrics(db, portfolio_id)

    return {
        "performance": performance,
        "allocation": allocation,
        "dividends": dividends,
        "risk": risk,
    }


# 고급 분석 API들
@router.post("/{portfolio_id}/snapshot", response_model=Dict)
def create_portfolio_snapshot(portfolio_id: int, db: Session = Depends(get_db)):
    """포트폴리오 스냅샷 생성"""
    snapshot = PortfolioAdvancedService.create_snapshot(db, portfolio_id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return {
        "message": "Snapshot created successfully",
        "snapshot_date": snapshot.snapshot_date.isoformat(),
        "total_value": snapshot.total_value,
    }


@router.get("/{portfolio_id}/history", response_model=Dict)
def get_portfolio_history(
    portfolio_id: int, days: int = 30, db: Session = Depends(get_db)
):
    """포트폴리오 히스토리 조회"""
    history = PortfolioAdvancedService.get_historical_performance(db, portfolio_id, days)
    return history


@router.get("/{portfolio_id}/rebalancing", response_model=Dict)
def get_rebalancing_recommendations(portfolio_id: int, db: Session = Depends(get_db)):
    """리밸런싱 추천"""
    recommendations = PortfolioAdvancedService.get_rebalancing_recommendations(db, portfolio_id)
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return recommendations


@router.get("/{portfolio_id}/target-comparison", response_model=Dict)
def get_target_comparison(portfolio_id: int, db: Session = Depends(get_db)):
    """목표 대비 성과 비교"""
    comparison = PortfolioAdvancedService.compare_with_target(db, portfolio_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found",
        )
    return comparison


@router.get("/{portfolio_id}/tax", response_model=Dict)
def get_tax_implications(portfolio_id: int, db: Session = Depends(get_db)):
    """세금 계산"""
    tax = PortfolioAdvancedService.calculate_tax_implications(db, portfolio_id)
    return tax
