"""Portfolio Analytics API Endpoints - Portfolio 2.0"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.portfolio import Portfolio
from app.services.portfolio_analyzer import PortfolioAnalyzer
from app.services.recommendation_engine import RecommendationEngine
from app.services.rebalancer import Rebalancer

router = APIRouter()


@router.get("/portfolios/{portfolio_id}/analytics")
async def get_portfolio_analytics(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """포트폴리오 종합 분석

    Returns:
        - Performance metrics (수익률, 일일 수익률, 연간 수익률)
        - Risk metrics (변동성, 샤프 비율, 베타, 알파, 최대 낙폭)
        - Diversification (섹터 다양성, 지역 다양성, 집중도)
        - Holdings analysis (종목별 상세)
    """
    # 포트폴리오 존재 확인
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # 분석 실행
    analyzer = PortfolioAnalyzer(db)
    analysis = await analyzer.analyze_portfolio(portfolio_id)

    return {
        "success": True,
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "analysis": analysis
    }


@router.post("/portfolios/{portfolio_id}/analytics/snapshot")
async def save_analytics_snapshot(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """포트폴리오 분석 스냅샷 저장

    일별 또는 정기적으로 포트폴리오 분석 결과를 저장하여
    성과 추이를 추적할 수 있습니다.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    analyzer = PortfolioAnalyzer(db)
    snapshot = await analyzer.save_analytics_snapshot(portfolio_id)

    return {
        "success": True,
        "message": "Analytics snapshot saved",
        "snapshot": {
            "id": snapshot.id,
            "portfolio_id": snapshot.portfolio_id,
            "total_value": snapshot.total_value,
            "total_return": snapshot.total_return,
            "sharpe_ratio": snapshot.sharpe_ratio,
            "snapshot_date": snapshot.snapshot_date
        }
    }


@router.get("/recommendations")
async def get_stock_recommendations(
    portfolio_id: Optional[int] = Query(None, description="포트폴리오 ID (선택)"),
    focus_sectors: Optional[str] = Query(None, description="관심 섹터 (쉼표로 구분)"),
    max_results: int = Query(10, ge=1, le=50, description="최대 추천 개수"),
    db: Session = Depends(get_db)
):
    """AI 기반 종목 추천

    Args:
        portfolio_id: 포트폴리오 ID (있으면 포트폴리오 맞춤 추천)
        focus_sectors: 관심 섹터 (예: "TECHNOLOGY,HEALTHCARE")
        max_results: 최대 추천 개수

    Returns:
        추천 종목 리스트 (신뢰도 순)
    """
    # 포트폴리오 확인
    if portfolio_id:
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

    # 섹터 파싱
    sectors = None
    if focus_sectors:
        sectors = [s.strip().upper() for s in focus_sectors.split(',')]

    # 추천 생성
    engine = RecommendationEngine(db)
    recommendations = await engine.generate_recommendations(
        portfolio_id=portfolio_id,
        focus_sectors=sectors,
        max_recommendations=max_results
    )

    return {
        "success": True,
        "count": len(recommendations),
        "portfolio_id": portfolio_id,
        "recommendations": recommendations
    }


@router.post("/recommendations/save")
async def save_recommendations(
    portfolio_id: Optional[int] = Query(None, description="포트폴리오 ID"),
    focus_sectors: Optional[str] = Query(None, description="관심 섹터"),
    max_results: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """추천 결과를 데이터베이스에 저장

    생성된 추천을 데이터베이스에 저장하여
    나중에 조회하고 추적할 수 있습니다.
    """
    # 추천 생성
    sectors = None
    if focus_sectors:
        sectors = [s.strip().upper() for s in focus_sectors.split(',')]

    engine = RecommendationEngine(db)
    recommendations = await engine.generate_recommendations(
        portfolio_id=portfolio_id,
        focus_sectors=sectors,
        max_recommendations=max_results
    )

    # 데이터베이스에 저장
    await engine.save_recommendations(recommendations, portfolio_id)

    return {
        "success": True,
        "message": f"Saved {len(recommendations)} recommendations",
        "count": len(recommendations)
    }


@router.get("/portfolios/{portfolio_id}/rebalance/check")
async def check_rebalancing_needed(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """리밸런싱 필요 여부 체크

    포트폴리오가 리밸런싱이 필요한지 확인하고,
    필요하다면 어떤 이유 때문인지 알려줍니다.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    rebalancer = Rebalancer(db)
    check_result = await rebalancer.check_rebalancing_needed(portfolio_id)

    return {
        "success": True,
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        **check_result
    }


@router.post("/portfolios/{portfolio_id}/rebalance/propose")
async def propose_rebalancing(
    portfolio_id: int,
    proposal_type: str = Query("AUTO", description="SECTOR_REBALANCE | RISK_REDUCTION | PERIODIC | AUTO"),
    db: Session = Depends(get_db)
):
    """리밸런싱 제안 생성

    현재 포트폴리오 상태를 분석하여
    최적의 리밸런싱 방안을 제안합니다.

    Args:
        portfolio_id: 포트폴리오 ID
        proposal_type: 제안 유형
            - AUTO: 자동 분석 (기본값)
            - SECTOR_REBALANCE: 섹터 균형 조정
            - RISK_REDUCTION: 리스크 축소
            - PERIODIC: 정기 리밸런싱
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    rebalancer = Rebalancer(db)
    proposal = await rebalancer.generate_rebalancing_proposal(
        portfolio_id=portfolio_id,
        proposal_type=proposal_type
    )

    if not proposal:
        return {
            "success": True,
            "message": "No rebalancing needed",
            "proposal": None
        }

    # 제안 저장
    saved_proposal = await rebalancer.save_proposal(proposal)

    return {
        "success": True,
        "message": "Rebalancing proposal created",
        "proposal": {
            "id": saved_proposal.id,
            "portfolio_id": saved_proposal.portfolio_id,
            "proposal_type": saved_proposal.proposal_type,
            "trigger_reason": saved_proposal.trigger_reason,
            "current_risk_score": saved_proposal.current_risk_score,
            "target_risk_score": saved_proposal.target_risk_score,
            "proposed_actions": saved_proposal.proposed_actions,
            "expected_return_change": saved_proposal.expected_return_change,
            "expected_risk_change": saved_proposal.expected_risk_change,
            "status": saved_proposal.status,
            "created_at": saved_proposal.created_at
        }
    }


@router.post("/rebalance/{proposal_id}/execute")
async def execute_rebalancing(
    proposal_id: int,
    db: Session = Depends(get_db)
):
    """리밸런싱 제안 실행

    Warning: 이 작업은 포트폴리오의 보유 주식 수량을 변경합니다.
    실제 거래는 하지 않고, 데이터만 업데이트합니다.
    """
    rebalancer = Rebalancer(db)

    try:
        executed_proposal = await rebalancer.execute_proposal(proposal_id)

        return {
            "success": True,
            "message": "Rebalancing executed successfully",
            "proposal": {
                "id": executed_proposal.id,
                "status": executed_proposal.status,
                "executed_at": executed_proposal.executed_at
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/portfolios/{portfolio_id}/insights")
async def get_portfolio_insights(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """포트폴리오 종합 인사이트

    분석, 추천, 리밸런싱을 한 번에 조회하여
    포트폴리오에 대한 전체적인 인사이트를 제공합니다.
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # 1. 포트폴리오 분석
    analyzer = PortfolioAnalyzer(db)
    analysis = await analyzer.analyze_portfolio(portfolio_id)

    # 2. 추천 생성
    engine = RecommendationEngine(db)
    recommendations = await engine.generate_recommendations(
        portfolio_id=portfolio_id,
        max_recommendations=5
    )

    # 3. 리밸런싱 체크
    rebalancer = Rebalancer(db)
    rebalance_check = await rebalancer.check_rebalancing_needed(portfolio_id)

    # 종합 점수 계산
    overall_score = 0.0
    strengths = []
    warnings = []
    suggestions = []

    # 성과 평가
    total_return = analysis['performance'].get('total_return', 0)
    if total_return > 10:
        overall_score += 30
        strengths.append(f"높은 수익률: {total_return:.1f}%")
    elif total_return < 0:
        warnings.append(f"마이너스 수익률: {total_return:.1f}%")

    # 리스크 평가
    sharpe_ratio = analysis['risk'].get('sharpe_ratio', 0)
    if sharpe_ratio > 1.0:
        overall_score += 25
        strengths.append(f"우수한 샤프 비율: {sharpe_ratio:.2f}")
    elif sharpe_ratio < 0.5:
        warnings.append(f"낮은 샤프 비율: {sharpe_ratio:.2f}")

    # 다각화 평가
    sector_diversity = analysis['diversification'].get('sector_diversity_score', 0)
    if sector_diversity > 60:
        overall_score += 25
        strengths.append(f"우수한 섹터 다각화: {sector_diversity:.1f}")
    elif sector_diversity < 40:
        warnings.append(f"낮은 섹터 다각화: {sector_diversity:.1f}")
        suggestions.append("다양한 섹터의 종목을 추가하세요")

    # 리밸런싱 필요성
    if rebalance_check['needs_rebalancing']:
        if rebalance_check['severity'] == 'HIGH':
            warnings.append("리밸런싱 긴급 필요")
            suggestions.append("즉시 리밸런싱을 실행하세요")
        elif rebalance_check['severity'] == 'MEDIUM':
            suggestions.append("리밸런싱을 고려하세요")
    else:
        overall_score += 20
        strengths.append("포트폴리오 균형 양호")

    return {
        "success": True,
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "overall_score": min(100, overall_score),
        "summary": {
            "strengths": strengths,
            "warnings": warnings,
            "suggestions": suggestions
        },
        "analysis": analysis,
        "top_recommendations": recommendations[:3],
        "rebalancing": rebalance_check
    }
