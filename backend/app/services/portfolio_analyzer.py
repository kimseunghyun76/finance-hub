"""Portfolio Analytics Engine - 포트폴리오 성과 분석"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.sector import StockInfo, PortfolioAnalytics, SectorType
from app.services.data_fetcher import StockDataFetcher


class PortfolioAnalyzer:
    """포트폴리오 성과 및 리스크 분석 엔진"""

    def __init__(self, db: Session):
        self.db = db
        self.risk_free_rate = 0.045  # 무위험 수익률 (4.5% = 미국 국채 수익률)
        self.market_ticker = "SPY"  # 시장 벤치마크 (S&P 500)
        self.exchange_rate_cache = {}  # 환율 캐시 (세션 동안 재사용)

    async def analyze_portfolio(self, portfolio_id: int) -> Dict:
        """포트폴리오 종합 분석

        Returns:
            {
                'performance': {...},  # 수익률 지표
                'risk': {...},         # 리스크 지표
                'diversification': {...},  # 다각화 지표
                'holdings': [...],     # 보유 종목 분석
            }
        """
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        holdings = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id
        ).all()

        if not holdings:
            return {
                'performance': {},
                'risk': {},
                'diversification': {},
                'holdings': []
            }

        # 각 종목의 가격 데이터 및 정보 가져오기
        holdings_data = await self._fetch_holdings_data(holdings)

        # 성과 분석
        performance = self._calculate_performance(holdings_data)

        # 리스크 분석
        risk = await self._calculate_risk(holdings_data, portfolio_id)

        # 다각화 분석
        diversification = self._calculate_diversification(holdings_data)

        # 종목별 분석
        holdings_analysis = self._analyze_holdings(holdings_data)

        return {
            'performance': performance,
            'risk': risk,
            'diversification': diversification,
            'holdings': holdings_analysis,
            'snapshot_date': datetime.now().strftime('%Y-%m-%d')
        }

    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """환율 가져오기 (캐싱 지원)"""
        if from_currency == to_currency:
            return 1.0

        cache_key = f"{from_currency}_{to_currency}"
        if cache_key in self.exchange_rate_cache:
            return self.exchange_rate_cache[cache_key]

        rate = StockDataFetcher.get_exchange_rate(from_currency, to_currency)
        if rate is None:
            # Fallback: 기본 환율 (2024년 평균)
            if from_currency == "KRW" and to_currency == "USD":
                rate = 0.00075  # 1 KRW ≈ 0.00075 USD (1 USD ≈ 1,333 KRW)
            elif from_currency == "USD" and to_currency == "KRW":
                rate = 1333.0
            else:
                rate = 1.0

        self.exchange_rate_cache[cache_key] = rate
        return rate

    def _get_currency_from_ticker(self, ticker: str) -> str:
        """티커에서 통화 추출"""
        if ticker.endswith(".KS") or ticker.endswith(".KQ"):
            return "KRW"
        return "USD"

    async def _fetch_holdings_data(self, holdings: List[Holding]) -> List[Dict]:
        """보유 종목 데이터 가져오기"""
        holdings_data = []

        for holding in holdings:
            # 주식 정보
            stock_info = self.db.query(StockInfo).filter(
                StockInfo.ticker == holding.ticker
            ).first()

            # 최근 1년 가격 데이터
            price_data = StockDataFetcher.fetch_yahoo_finance(
                holding.ticker,
                period="1y"
            )

            if price_data is None or price_data.empty:
                continue

            current_price = float(price_data['close'].iloc[-1])
            total_value = current_price * holding.shares

            # 통화 정보
            currency = self._get_currency_from_ticker(holding.ticker)

            # USD로 환산한 가치
            if currency == "USD":
                total_value_usd = total_value
                current_price_usd = current_price
                purchase_price_usd = holding.purchase_price
            else:
                exchange_rate = self._get_exchange_rate(currency, "USD")
                total_value_usd = total_value * exchange_rate
                current_price_usd = current_price * exchange_rate
                purchase_price_usd = holding.purchase_price * exchange_rate

            holdings_data.append({
                'ticker': holding.ticker,
                'shares': holding.shares,
                'purchase_price': holding.purchase_price,
                'current_price': current_price,
                'total_value': total_value,
                'currency': currency,
                'purchase_price_usd': purchase_price_usd,
                'current_price_usd': current_price_usd,
                'total_value_usd': total_value_usd,
                'price_data': price_data,
                'stock_info': stock_info
            })

        return holdings_data

    def _calculate_performance(self, holdings_data: List[Dict]) -> Dict:
        """수익률 지표 계산 (USD 기준 통합)"""
        if not holdings_data:
            return {}

        # USD 기준 합산
        total_value_usd = sum(h['total_value_usd'] for h in holdings_data)
        total_cost_usd = sum(h['purchase_price_usd'] * h['shares'] for h in holdings_data)

        # 통화별 분리 계산
        by_currency = {}
        for holding in holdings_data:
            currency = holding['currency']
            if currency not in by_currency:
                by_currency[currency] = {'value': 0, 'cost': 0}

            by_currency[currency]['value'] += holding['total_value']
            by_currency[currency]['cost'] += holding['purchase_price'] * holding['shares']

        # USD 기준 수익률
        if total_cost_usd > 0:
            total_return = ((total_value_usd - total_cost_usd) / total_cost_usd) * 100
        else:
            total_return = 0.0

        # 일일 수익률 계산 (USD 기준)
        daily_returns = []
        for holding in holdings_data:
            price_data = holding['price_data']
            if len(price_data) > 1:
                daily_return = price_data['close'].pct_change().iloc[-1]
                weight = holding['total_value_usd'] / total_value_usd if total_value_usd > 0 else 0
                daily_returns.append(daily_return * weight)

        daily_return = sum(daily_returns) * 100 if daily_returns else 0.0

        # 연간 수익률 (단순화)
        days_held = 365  # 평균 보유 기간으로 가정
        annualized_return = ((1 + total_return/100) ** (365/days_held) - 1) * 100

        return {
            'total_value': round(total_value_usd, 2),
            'total_cost': round(total_cost_usd, 2),
            'total_return': round(total_return, 2),
            'total_gain': round(total_value_usd - total_cost_usd, 2),
            'daily_return': round(daily_return, 2),
            'annualized_return': round(annualized_return, 2),
            'by_currency': {
                currency: {
                    'value': round(data['value'], 2),
                    'cost': round(data['cost'], 2),
                    'gain': round(data['value'] - data['cost'], 2),
                    'return': round(((data['value'] - data['cost']) / data['cost'] * 100) if data['cost'] > 0 else 0, 2)
                }
                for currency, data in by_currency.items()
            }
        }

    async def _calculate_risk(self, holdings_data: List[Dict], portfolio_id: int) -> Dict:
        """리스크 지표 계산"""
        if not holdings_data:
            return {}

        # 포트폴리오 일별 수익률 계산
        portfolio_returns = self._calculate_portfolio_returns(holdings_data)

        # 변동성 (Volatility) - 연간화된 표준편차
        volatility = portfolio_returns.std() * np.sqrt(252) * 100

        # 샤프 비율 (Sharpe Ratio) = (포트폴리오 수익률 - 무위험 수익률) / 변동성
        annual_return = portfolio_returns.mean() * 252 * 100
        sharpe_ratio = (annual_return - self.risk_free_rate * 100) / volatility if volatility > 0 else 0

        # 최대 낙폭 (Maximum Drawdown)
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # 베타 (Beta) - 시장 대비 민감도
        beta, alpha = await self._calculate_beta_alpha(portfolio_returns)

        # VaR (Value at Risk) 95% 신뢰수준
        var_95 = np.percentile(portfolio_returns, 5) * 100

        return {
            'volatility': round(volatility, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'beta': round(beta, 2),
            'alpha': round(alpha, 2),
            'var_95': round(var_95, 2)
        }

    def _calculate_portfolio_returns(self, holdings_data: List[Dict]) -> pd.Series:
        """포트폴리오 일별 수익률 계산 (USD 기준)"""
        total_value_usd = sum(h['total_value_usd'] for h in holdings_data)

        # 각 종목의 가중 수익률 계산 (USD 기준)
        all_returns = []
        for holding in holdings_data:
            price_data = holding['price_data']
            returns = price_data['close'].pct_change().dropna()
            weight = holding['total_value_usd'] / total_value_usd if total_value_usd > 0 else 0
            weighted_returns = returns * weight
            all_returns.append(weighted_returns)

        # 날짜별로 합산
        portfolio_returns = pd.concat(all_returns, axis=1).sum(axis=1)
        return portfolio_returns.dropna()

    async def _calculate_beta_alpha(self, portfolio_returns: pd.Series) -> Tuple[float, float]:
        """베타와 알파 계산 (시장 대비)"""
        try:
            # 시장 데이터 (SPY)
            market_data = StockDataFetcher.fetch_yahoo_finance(
                self.market_ticker,
                period="1y"
            )

            if market_data is None or market_data.empty:
                return 1.0, 0.0

            market_returns = market_data['close'].pct_change().dropna()

            # 공통 날짜만 사용
            common_dates = portfolio_returns.index.intersection(market_returns.index)
            if len(common_dates) < 30:
                return 1.0, 0.0

            port_ret = portfolio_returns.loc[common_dates]
            mkt_ret = market_returns.loc[common_dates]

            # 베타 계산 (공분산 / 시장 분산)
            covariance = np.cov(port_ret, mkt_ret)[0][1]
            market_variance = np.var(mkt_ret)
            beta = covariance / market_variance if market_variance > 0 else 1.0

            # 알파 계산 (포트폴리오 수익률 - (무위험 수익률 + 베타 * 시장 초과 수익률))
            portfolio_annual_return = port_ret.mean() * 252
            market_annual_return = mkt_ret.mean() * 252
            alpha = portfolio_annual_return - (self.risk_free_rate + beta * (market_annual_return - self.risk_free_rate))
            alpha = alpha * 100  # 백분율로 변환

            return beta, alpha

        except Exception as e:
            print(f"Beta/Alpha calculation error: {e}")
            return 1.0, 0.0

    def _calculate_diversification(self, holdings_data: List[Dict]) -> Dict:
        """다각화 지표 계산 (USD 기준)"""
        if not holdings_data:
            return {}

        total_value_usd = sum(h['total_value_usd'] for h in holdings_data)

        # 섹터별 분포 (USD 기준)
        sector_distribution = {}
        for holding in holdings_data:
            stock_info = holding['stock_info']
            if stock_info and stock_info.sector:
                sector = stock_info.sector.value
                weight = (holding['total_value_usd'] / total_value_usd) * 100
                sector_distribution[sector] = sector_distribution.get(sector, 0) + weight

        # 섹터 다양성 점수 (0-100) - 허핀달-허쉬만 지수 기반
        # HHI = sum(weight^2), 낮을수록 다각화 잘됨
        if sector_distribution:
            hhi = sum((w/100) ** 2 for w in sector_distribution.values())
            sector_diversity_score = (1 - hhi) * 100  # 0-100 점수로 변환
        else:
            sector_diversity_score = 0.0

        # 지역별 분포 (USD 기준)
        country_distribution = {}
        for holding in holdings_data:
            stock_info = holding['stock_info']
            if stock_info:
                country = stock_info.country
                weight = (holding['total_value_usd'] / total_value_usd) * 100
                country_distribution[country] = country_distribution.get(country, 0) + weight

        # 지역 다양성 점수
        if country_distribution:
            geo_hhi = sum((w/100) ** 2 for w in country_distribution.values())
            geographic_diversity_score = (1 - geo_hhi) * 100
        else:
            geographic_diversity_score = 0.0

        # 집중 리스크 (상위 5개 종목 비중, USD 기준)
        sorted_holdings = sorted(holdings_data, key=lambda x: x['total_value_usd'], reverse=True)
        top_5_value = sum(h['total_value_usd'] for h in sorted_holdings[:5])
        concentration_risk = (top_5_value / total_value_usd) * 100

        return {
            'sector_diversity_score': round(sector_diversity_score, 2),
            'geographic_diversity_score': round(geographic_diversity_score, 2),
            'concentration_risk': round(concentration_risk, 2),
            'sector_distribution': {k: round(v, 2) for k, v in sector_distribution.items()},
            'country_distribution': {k: round(v, 2) for k, v in country_distribution.items()},
            'num_holdings': len(holdings_data)
        }

    def _analyze_holdings(self, holdings_data: List[Dict]) -> List[Dict]:
        """종목별 상세 분석 (USD 기준 정렬 및 비중)"""
        total_value_usd = sum(h['total_value_usd'] for h in holdings_data)

        holdings_analysis = []
        for holding in holdings_data:
            stock_info = holding['stock_info']

            gain = holding['current_price'] - holding['purchase_price']
            gain_percent = (gain / holding['purchase_price']) * 100
            weight = (holding['total_value_usd'] / total_value_usd) * 100

            holdings_analysis.append({
                'ticker': holding['ticker'],
                'name': stock_info.name if stock_info else holding['ticker'],
                'sector': stock_info.sector.value if stock_info and stock_info.sector else 'Unknown',
                'currency': holding['currency'],
                'shares': holding['shares'],
                'purchase_price': round(holding['purchase_price'], 2),
                'current_price': round(holding['current_price'], 2),
                'total_value': round(holding['total_value'], 2),
                'total_value_usd': round(holding['total_value_usd'], 2),
                'gain': round(gain, 2),
                'gain_percent': round(gain_percent, 2),
                'weight': round(weight, 2),
                'is_etf': stock_info.is_etf if stock_info else 0
            })

        return sorted(holdings_analysis, key=lambda x: x['total_value_usd'], reverse=True)

    async def save_analytics_snapshot(self, portfolio_id: int):
        """포트폴리오 분석 결과를 데이터베이스에 저장"""
        analysis = await self.analyze_portfolio(portfolio_id)

        snapshot = PortfolioAnalytics(
            portfolio_id=portfolio_id,
            total_value=analysis['performance'].get('total_value', 0),
            total_return=analysis['performance'].get('total_return', 0),
            daily_return=analysis['performance'].get('daily_return'),
            volatility=analysis['risk'].get('volatility'),
            sharpe_ratio=analysis['risk'].get('sharpe_ratio'),
            max_drawdown=analysis['risk'].get('max_drawdown'),
            beta=analysis['risk'].get('beta'),
            alpha=analysis['risk'].get('alpha'),
            sector_diversity_score=analysis['diversification'].get('sector_diversity_score'),
            geographic_diversity_score=analysis['diversification'].get('geographic_diversity_score'),
            concentration_risk=analysis['diversification'].get('concentration_risk'),
            snapshot_date=analysis['snapshot_date']
        )

        self.db.add(snapshot)
        self.db.commit()

        return snapshot
