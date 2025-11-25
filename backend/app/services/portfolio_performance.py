"""Portfolio performance analysis service"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.services.stock_cache_service import StockCacheService


class PortfolioPerformanceService:
    """서비스: 포트폴리오 성과 분석"""

    @staticmethod
    def calculate_portfolio_performance(db: Session, portfolio_id: int) -> Dict:
        """포트폴리오 전체 성과 계산"""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return None

        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        if not holdings:
            return {
                "portfolio_id": portfolio_id,
                "total_value": 0.0,
                "total_cost": 0.0,
                "total_gain_loss": 0.0,
                "total_return_percent": 0.0,
                "daily_change": 0.0,
                "daily_change_percent": 0.0,
                "holdings_count": 0,
            }

        # 현재 포트폴리오 가치 및 수익 계산
        total_value = 0.0
        total_cost = 0.0
        previous_day_value = 0.0

        for holding in holdings:
            # 현재 가격 가져오기 (캐시 사용)
            try:
                current_price, previous_close = StockCacheService.get_stock_price(db, holding.ticker)

                # 가격이 0이면 평균가 사용 (API 실패 시)
                if current_price == 0:
                    current_price = holding.avg_price
                    previous_close = holding.avg_price

                # 현재 가치
                position_value = current_price * holding.quantity
                total_value += position_value

                # 매입 비용
                cost = holding.avg_price * holding.quantity
                total_cost += cost

                # 전일 종가 기준 가치
                previous_day_value += previous_close * holding.quantity

            except Exception as e:
                print(f"⚠️ Error fetching price for {holding.ticker}: {e}")
                # 가격을 가져올 수 없으면 평균가로 계산
                cost = holding.avg_price * holding.quantity
                total_cost += cost
                total_value += cost
                previous_day_value += cost

        # 수익률 계산
        total_gain_loss = total_value - total_cost
        total_return_percent = (
            (total_gain_loss / total_cost * 100) if total_cost > 0 else 0.0
        )

        # 일일 변동
        daily_change = total_value - previous_day_value
        daily_change_percent = (
            (daily_change / previous_day_value * 100) if previous_day_value > 0 else 0.0
        )

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_gain_loss": round(total_gain_loss, 2),
            "total_return_percent": round(total_return_percent, 2),
            "daily_change": round(daily_change, 2),
            "daily_change_percent": round(daily_change_percent, 2),
            "holdings_count": len(holdings),
            "initial_value": portfolio.initial_value,
            "target_return": portfolio.target_return,
            "risk_tolerance": portfolio.risk_tolerance,
        }

    @staticmethod
    def calculate_asset_allocation(db: Session, portfolio_id: int) -> Dict:
        """자산 배분 분석"""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        if not holdings:
            return {
                "by_sector": {},
                "by_country": {},
                "by_asset_type": {},
            }

        # 섹터별, 국가별, 자산 유형별 분류
        sector_allocation = {}
        country_allocation = {}
        total_value = 0.0

        for holding in holdings:
            try:
                # 가격 정보 (캐시 사용)
                current_price, _ = StockCacheService.get_stock_price(db, holding.ticker)
                if current_price == 0:
                    current_price = holding.avg_price

                position_value = current_price * holding.quantity
                total_value += position_value

                # 메타데이터 정보 (캐시 사용)
                metadata = StockCacheService.get_stock_metadata(db, holding.ticker)

                if metadata:
                    # 섹터별
                    sector = metadata.sector or "Unknown"
                    sector_allocation[sector] = sector_allocation.get(sector, 0) + position_value

                    # 국가별
                    country = metadata.country or "Unknown"
                    country_allocation[country] = country_allocation.get(country, 0) + position_value
                else:
                    sector_allocation["Unknown"] = sector_allocation.get("Unknown", 0) + position_value
                    country_allocation["Unknown"] = country_allocation.get("Unknown", 0) + position_value

            except Exception as e:
                print(f"⚠️ Error fetching info for {holding.ticker}: {e}")
                position_value = holding.avg_price * holding.quantity
                total_value += position_value
                sector_allocation["Unknown"] = sector_allocation.get("Unknown", 0) + position_value
                country_allocation["Unknown"] = country_allocation.get("Unknown", 0) + position_value

        # 비율로 변환
        sector_percent = {
            sector: round(value / total_value * 100, 2) if total_value > 0 else 0
            for sector, value in sector_allocation.items()
        }
        country_percent = {
            country: round(value / total_value * 100, 2) if total_value > 0 else 0
            for country, value in country_allocation.items()
        }

        return {
            "by_sector": sector_percent,
            "by_country": country_percent,
            "by_asset_type": {"stocks": 100.0},  # 현재는 주식만 지원
        }

    @staticmethod
    def calculate_dividend_income(db: Session, portfolio_id: int) -> Dict:
        """배당금 수익 계산"""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        total_annual_dividend = 0.0
        total_value = 0.0
        dividend_stocks = []

        for holding in holdings:
            try:
                # 가격 정보 (캐시 사용)
                current_price, _ = StockCacheService.get_stock_price(db, holding.ticker)
                if current_price == 0:
                    current_price = holding.avg_price

                position_value = current_price * holding.quantity
                total_value += position_value

                # 배당 정보 (캐시 사용)
                metadata = StockCacheService.get_stock_metadata(db, holding.ticker)

                if metadata and metadata.dividend_rate and metadata.dividend_rate > 0:
                    annual_dividend = metadata.dividend_rate * holding.quantity
                    total_annual_dividend += annual_dividend

                    dividend_stocks.append({
                        "ticker": holding.ticker,
                        "quantity": holding.quantity,
                        "current_price": current_price,
                        "dividend_rate": metadata.dividend_rate,
                        "dividend_yield": round(metadata.dividend_yield * 100, 2) if metadata.dividend_yield else 0,
                        "annual_dividend": round(annual_dividend, 2),
                    })

            except Exception as e:
                print(f"⚠️ Error fetching dividend for {holding.ticker}: {e}")
                continue

        portfolio_dividend_yield = (
            (total_annual_dividend / total_value * 100) if total_value > 0 else 0.0
        )

        return {
            "total_annual_dividend": round(total_annual_dividend, 2),
            "portfolio_dividend_yield": round(portfolio_dividend_yield, 2),
            "dividend_stocks_count": len(dividend_stocks),
            "dividend_stocks": dividend_stocks,
        }

    @staticmethod
    def calculate_risk_metrics(db: Session, portfolio_id: int) -> Dict:
        """리스크 분석"""
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

        if not holdings:
            return {
                "concentration_risk": 0.0,
                "top_holdings_percent": 0.0,
                "volatility_score": "N/A",
                "diversification_score": 0,
            }

        # 집중도 리스크 계산
        total_value = 0.0
        position_values = []

        for holding in holdings:
            try:
                # 가격 정보 (캐시 사용)
                current_price, _ = StockCacheService.get_stock_price(db, holding.ticker)
                if current_price == 0:
                    current_price = holding.avg_price

                position_value = current_price * holding.quantity
                total_value += position_value
                position_values.append(position_value)
            except:
                position_value = holding.avg_price * holding.quantity
                total_value += position_value
                position_values.append(position_value)

        # 상위 3개 종목 비중
        position_values.sort(reverse=True)
        top_3_value = sum(position_values[:3]) if len(position_values) >= 3 else sum(position_values)
        top_holdings_percent = (top_3_value / total_value * 100) if total_value > 0 else 0

        # 집중도 점수 (높을수록 위험)
        concentration_risk = top_holdings_percent

        # 분산도 점수 (종목 수 기반)
        diversification_score = min(len(holdings) * 10, 100)  # 10개 이상이면 만점

        # 변동성 점수 (간단한 규칙 기반)
        if concentration_risk > 50:
            volatility_score = "High"
        elif concentration_risk > 30:
            volatility_score = "Medium"
        else:
            volatility_score = "Low"

        return {
            "concentration_risk": round(concentration_risk, 2),
            "top_holdings_percent": round(top_holdings_percent, 2),
            "volatility_score": volatility_score,
            "diversification_score": diversification_score,
            "holdings_count": len(holdings),
            "recommendation": PortfolioPerformanceService._get_risk_recommendation(
                concentration_risk, diversification_score
            ),
        }

    @staticmethod
    def _get_risk_recommendation(concentration: float, diversification: int) -> str:
        """리스크 개선 제안"""
        recommendations = []

        if concentration > 50:
            recommendations.append("⚠️ 특정 종목 집중도가 매우 높습니다. 분산 투자를 권장합니다.")
        elif concentration > 30:
            recommendations.append("💡 일부 종목의 비중이 높습니다. 추가 분산을 고려하세요.")

        if diversification < 30:
            recommendations.append("📊 보유 종목 수가 적습니다. 최소 5-10개 종목 보유를 권장합니다.")
        elif diversification < 60:
            recommendations.append("✅ 적절한 분산 수준입니다. 섹터 다양성도 확인하세요.")
        else:
            recommendations.append("🎯 우수한 분산 포트폴리오입니다!")

        return " ".join(recommendations)
