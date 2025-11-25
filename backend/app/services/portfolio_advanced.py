"""Advanced portfolio analysis services"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.portfolio_snapshot import PortfolioSnapshot
from app.services.stock_cache_service import StockCacheService
from app.services.portfolio_performance import PortfolioPerformanceService


class PortfolioAdvancedService:
    """고급 포트폴리오 분석 서비스"""

    @staticmethod
    def create_snapshot(db: Session, portfolio_id: int) -> Optional[PortfolioSnapshot]:
        """포트폴리오 스냅샷 생성"""
        # 현재 성과 계산
        performance = PortfolioPerformanceService.calculate_portfolio_performance(db, portfolio_id)
        if not performance:
            return None

        today = date.today()

        # 이미 오늘 스냅샷이 있는지 확인
        existing = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.snapshot_date == today,
            )
            .first()
        )

        if existing:
            # 업데이트
            existing.total_value = performance["total_value"]
            existing.total_cost = performance["total_cost"]
            existing.total_gain_loss = performance["total_gain_loss"]
            existing.total_return_percent = performance["total_return_percent"]
            existing.daily_change = performance["daily_change"]
            existing.daily_change_percent = performance["daily_change_percent"]
            existing.holdings_count = performance["holdings_count"]
        else:
            # 생성
            existing = PortfolioSnapshot(
                portfolio_id=portfolio_id,
                snapshot_date=today,
                total_value=performance["total_value"],
                total_cost=performance["total_cost"],
                total_gain_loss=performance["total_gain_loss"],
                total_return_percent=performance["total_return_percent"],
                daily_change=performance["daily_change"],
                daily_change_percent=performance["daily_change_percent"],
                holdings_count=performance["holdings_count"],
            )
            db.add(existing)

        db.commit()
        db.refresh(existing)
        return existing

    @staticmethod
    def get_historical_performance(
        db: Session, portfolio_id: int, days: int = 30
    ) -> Dict:
        """히스토리 성과 조회"""
        start_date = date.today() - timedelta(days=days)

        snapshots = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.snapshot_date >= start_date,
            )
            .order_by(PortfolioSnapshot.snapshot_date.asc())
            .all()
        )

        if not snapshots:
            return {
                "portfolio_id": portfolio_id,
                "period_days": days,
                "data_points": 0,
                "history": [],
            }

        history = []
        for snapshot in snapshots:
            history.append({
                "date": snapshot.snapshot_date.isoformat(),
                "total_value": round(snapshot.total_value, 2),
                "total_return_percent": round(snapshot.total_return_percent, 2),
                "daily_change_percent": round(snapshot.daily_change_percent, 2),
            })

        # 기간 수익률 계산
        period_start_value = snapshots[0].total_value
        period_end_value = snapshots[-1].total_value
        period_return = ((period_end_value - period_start_value) / period_start_value * 100) if period_start_value > 0 else 0

        return {
            "portfolio_id": portfolio_id,
            "period_days": days,
            "period_return_percent": round(period_return, 2),
            "data_points": len(snapshots),
            "history": history,
        }

    @staticmethod
    def get_rebalancing_recommendations(db: Session, portfolio_id: int) -> Dict:
        """리밸런싱 추천"""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return None

        # 현재 자산 배분
        allocation = PortfolioPerformanceService.calculate_asset_allocation(db, portfolio_id)

        # 리스크 분석
        risk = PortfolioPerformanceService.calculate_risk_metrics(db, portfolio_id)

        recommendations = []

        # 1. 집중도 리스크 기반 추천
        if risk["concentration_risk"] > 50:
            recommendations.append({
                "type": "reduce_concentration",
                "priority": "high",
                "description": "상위 3개 종목이 포트폴리오의 50% 이상을 차지합니다. 분산 투자를 권장합니다.",
                "action": "일부 비중이 높은 종목을 매도하고, 다른 섹터나 국가의 종목에 투자하세요.",
            })
        elif risk["concentration_risk"] > 30:
            recommendations.append({
                "type": "moderate_rebalancing",
                "priority": "medium",
                "description": "일부 종목의 비중이 높습니다.",
                "action": "포트폴리오를 검토하고 필요시 리밸런싱을 고려하세요.",
            })

        # 2. 분산도 기반 추천
        if risk["diversification_score"] < 30:
            recommendations.append({
                "type": "increase_diversification",
                "priority": "high",
                "description": f"현재 {risk['holdings_count']}개 종목만 보유 중입니다.",
                "action": "최소 5-10개 종목으로 분산 투자를 권장합니다.",
            })

        # 3. 섹터 배분 기반 추천
        sector_allocation = allocation["by_sector"]
        max_sector = max(sector_allocation.items(), key=lambda x: x[1]) if sector_allocation else (None, 0)
        if max_sector[1] > 60:
            recommendations.append({
                "type": "sector_diversification",
                "priority": "medium",
                "description": f"{max_sector[0]} 섹터가 {max_sector[1]:.1f}%로 과도하게 집중되어 있습니다.",
                "action": "다른 섹터(기술, 금융, 헬스케어, 소비재 등)로 분산하세요.",
            })

        # 4. 국가 배분 기반 추천
        country_allocation = allocation["by_country"]
        max_country = max(country_allocation.items(), key=lambda x: x[1]) if country_allocation else (None, 0)
        if max_country[1] > 70:
            recommendations.append({
                "type": "geographic_diversification",
                "priority": "medium",
                "description": f"{max_country[0]}에 {max_country[1]:.1f}%가 집중되어 있습니다.",
                "action": "글로벌 분산 투자를 고려하세요 (미국, 유럽, 아시아 등).",
            })

        return {
            "portfolio_id": portfolio_id,
            "concentration_risk": risk["concentration_risk"],
            "diversification_score": risk["diversification_score"],
            "recommendations_count": len(recommendations),
            "recommendations": recommendations,
        }

    @staticmethod
    def compare_with_target(db: Session, portfolio_id: int) -> Dict:
        """목표 대비 성과 분석"""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return None

        performance = PortfolioPerformanceService.calculate_portfolio_performance(db, portfolio_id)
        if not performance:
            return None

        # 목표 수익률과 현재 수익률 비교
        target_return = portfolio.target_return or 0
        current_return = performance["total_return_percent"]

        # 목표 금액 계산
        target_value = portfolio.initial_value * (1 + target_return / 100) if portfolio.initial_value > 0 else 0
        current_value = performance["total_value"]

        # 달성률
        achievement_rate = (current_return / target_return * 100) if target_return > 0 else 0

        # 상태 판단
        if achievement_rate >= 100:
            status = "achieved"
            message = f"🎉 목표 수익률 {target_return}%를 달성했습니다!"
        elif achievement_rate >= 80:
            status = "on_track"
            message = f"✅ 목표 달성률 {achievement_rate:.1f}%. 순조롭게 진행 중입니다."
        elif achievement_rate >= 50:
            status = "behind"
            message = f"⚠️ 목표 달성률 {achievement_rate:.1f}%. 목표에 약간 못 미치고 있습니다."
        else:
            status = "far_behind"
            message = f"🚨 목표 달성률 {achievement_rate:.1f}%. 전략 재검토가 필요합니다."

        return {
            "portfolio_id": portfolio_id,
            "initial_value": portfolio.initial_value,
            "current_value": current_value,
            "target_return_percent": target_return,
            "current_return_percent": current_return,
            "target_value": round(target_value, 2),
            "value_gap": round(target_value - current_value, 2),
            "achievement_rate": round(achievement_rate, 2),
            "status": status,
            "message": message,
        }

    @staticmethod
    def calculate_tax_implications(db: Session, portfolio_id: int) -> Dict:
        """세금 계산 (한국 기준)"""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        # 국내 주식: 양도소득세 없음 (대주주 제외)
        # 해외 주식: 250만원 공제 후 22% 과세

        domestic_gain = 0.0
        foreign_gain = 0.0
        domestic_count = 0
        foreign_count = 0

        for holding in holdings:
            try:
                current_price, _ = StockCacheService.get_stock_price(db, holding.ticker)
                if current_price == 0:
                    current_price = holding.avg_price

                cost = holding.avg_price * holding.quantity
                current_value = current_price * holding.quantity
                gain = current_value - cost

                # 한국 주식 (.KS, .KQ)
                if holding.ticker.endswith(".KS") or holding.ticker.endswith(".KQ"):
                    domestic_gain += gain
                    domestic_count += 1
                else:
                    foreign_gain += gain
                    foreign_count += 1

            except Exception as e:
                print(f"⚠️ Error calculating tax for {holding.ticker}: {e}")
                continue

        # 해외 주식 세금 계산 (250만원 공제, 22% 과세)
        foreign_deduction = 2500000  # 250만원 기본 공제
        taxable_foreign_gain = max(foreign_gain - foreign_deduction, 0)
        foreign_tax = taxable_foreign_gain * 0.22

        # 지방소득세 (양도소득세의 10%)
        local_tax = foreign_tax * 0.1
        total_tax = foreign_tax + local_tax

        return {
            "portfolio_id": portfolio_id,
            "domestic_stocks": {
                "count": domestic_count,
                "total_gain": round(domestic_gain, 2),
                "tax": 0.0,  # 대주주 아니면 과세 없음
                "note": "국내 주식은 대주주가 아닌 경우 양도소득세가 없습니다.",
            },
            "foreign_stocks": {
                "count": foreign_count,
                "total_gain": round(foreign_gain, 2),
                "deduction": foreign_deduction,
                "taxable_gain": round(taxable_foreign_gain, 2),
                "tax_rate": 0.22,
                "income_tax": round(foreign_tax, 2),
                "local_tax": round(local_tax, 2),
                "total_tax": round(total_tax, 2),
                "note": "해외 주식은 연 250만원 공제 후 22% 과세됩니다.",
            },
            "total_estimated_tax": round(total_tax, 2),
            "net_gain_after_tax": round(domestic_gain + foreign_gain - total_tax, 2),
        }
