"""Portfolio Rebalancing Engine - 포트폴리오 리밸런싱 엔진"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.sector import StockInfo, RebalanceProposal, SectorType
from app.services.portfolio_analyzer import PortfolioAnalyzer
from app.services.data_fetcher import StockDataFetcher


class Rebalancer:
    """포트폴리오 리밸런싱 제안 엔진

    리밸런싱 트리거:
    1. 정기 리밸런싱 (월간, 분기)
    2. 섹터 불균형
    3. 리스크 급증
    4. 집중도 위험
    """

    def __init__(self, db: Session):
        self.db = db
        self.analyzer = PortfolioAnalyzer(db)

        # 리밸런싱 기준
        self.RISK_THRESHOLDS = {
            'volatility_max': 25.0,  # 연간 변동성 25% 이상
            'concentration_max': 50.0,  # 상위 5개 종목 50% 이상
            'sector_min_diversity': 40.0,  # 섹터 다양성 40% 미만
        }

        self.TARGET_ALLOCATION = {
            'single_stock_max': 15.0,  # 개별 종목 최대 15%
            'single_stock_min': 2.0,   # 개별 종목 최소 2%
            'sector_max': 40.0,        # 단일 섹터 최대 40%
            'etf_allocation': 20.0,    # ETF 권장 비중 20%
        }

    async def check_rebalancing_needed(self, portfolio_id: int) -> Dict:
        """리밸런싱 필요 여부 체크

        Returns:
            {
                'needs_rebalancing': bool,
                'triggers': List[str],
                'severity': 'LOW' | 'MEDIUM' | 'HIGH'
            }
        """
        # 포트폴리오 분석
        analysis = await self.analyzer.analyze_portfolio(portfolio_id)

        triggers = []
        severity_score = 0

        # 1. 리스크 체크
        risk = analysis.get('risk', {})
        volatility = risk.get('volatility', 0)
        if volatility > self.RISK_THRESHOLDS['volatility_max']:
            triggers.append(f"HIGH_VOLATILITY: {volatility:.1f}%")
            severity_score += 3

        # 2. 집중도 체크
        diversification = analysis.get('diversification', {})
        concentration = diversification.get('concentration_risk', 0)
        if concentration > self.RISK_THRESHOLDS['concentration_max']:
            triggers.append(f"HIGH_CONCENTRATION: {concentration:.1f}%")
            severity_score += 2

        # 3. 섹터 다양성 체크
        sector_diversity = diversification.get('sector_diversity_score', 100)
        if sector_diversity < self.RISK_THRESHOLDS['sector_min_diversity']:
            triggers.append(f"LOW_SECTOR_DIVERSITY: {sector_diversity:.1f}")
            severity_score += 2

        # 4. 개별 종목 비중 체크
        holdings = analysis.get('holdings', [])
        for holding in holdings:
            weight = holding.get('weight', 0)
            if weight > self.TARGET_ALLOCATION['single_stock_max']:
                triggers.append(f"OVERWEIGHT_{holding['ticker']}: {weight:.1f}%")
                severity_score += 1

        # 심각도 판단
        if severity_score >= 5:
            severity = 'HIGH'
        elif severity_score >= 3:
            severity = 'MEDIUM'
        elif severity_score >= 1:
            severity = 'LOW'
        else:
            severity = 'NONE'

        return {
            'needs_rebalancing': len(triggers) > 0,
            'triggers': triggers,
            'severity': severity,
            'severity_score': severity_score
        }

    async def generate_rebalancing_proposal(
        self,
        portfolio_id: int,
        proposal_type: str = "AUTO"
    ) -> Optional[Dict]:
        """리밸런싱 제안 생성

        Args:
            portfolio_id: 포트폴리오 ID
            proposal_type: SECTOR_REBALANCE | RISK_REDUCTION | PERIODIC | AUTO

        Returns:
            리밸런싱 제안 내용
        """
        # 현재 상태 분석
        check_result = await self.check_rebalancing_needed(portfolio_id)

        if not check_result['needs_rebalancing'] and proposal_type == "AUTO":
            return None

        # 포트폴리오 분석
        analysis = await self.analyzer.analyze_portfolio(portfolio_id)
        holdings = analysis.get('holdings', [])

        if not holdings:
            return None

        # 현재 가격 업데이트
        holdings_with_prices = await self._update_current_prices(holdings)

        # 리밸런싱 액션 계산
        actions = self._calculate_rebalancing_actions(
            holdings_with_prices,
            analysis,
            proposal_type
        )

        if not actions:
            return None

        # 예상 효과 계산
        expected_impact = self._calculate_expected_impact(
            holdings_with_prices,
            actions,
            analysis
        )

        # 제안 저장
        proposal = {
            'portfolio_id': portfolio_id,
            'proposal_type': proposal_type,
            'trigger_reason': ", ".join(check_result['triggers']) or "PERIODIC",
            'current_risk_score': analysis['risk'].get('volatility', 0),
            'target_risk_score': expected_impact['target_risk_score'],
            'current_diversification': analysis['diversification'].get('sector_diversity_score', 0),
            'target_diversification': expected_impact['target_diversification'],
            'proposed_actions': json.dumps(actions),
            'expected_return_change': expected_impact.get('return_change', 0),
            'expected_risk_change': expected_impact.get('risk_change', 0),
            'status': 'PENDING',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return proposal

    async def _update_current_prices(self, holdings: List[Dict]) -> List[Dict]:
        """현재 가격 업데이트"""
        updated_holdings = []

        for holding in holdings:
            # 최신 가격 가져오기
            price_data = StockDataFetcher.fetch_yahoo_finance(
                holding['ticker'],
                period="5d"
            )

            if price_data is not None and not price_data.empty:
                current_price = float(price_data['close'].iloc[-1])
                holding['current_price'] = current_price
                holding['total_value'] = current_price * holding['shares']

            updated_holdings.append(holding)

        return updated_holdings

    def _calculate_rebalancing_actions(
        self,
        holdings: List[Dict],
        analysis: Dict,
        proposal_type: str
    ) -> List[Dict]:
        """리밸런싱 액션 계산 (USD 기준)"""
        actions = []

        # USD 기준 총 가치 사용
        total_value_usd = sum(h.get('total_value_usd', h['total_value']) for h in holdings)

        # 섹터별 현재 비중 (이미 USD 기준)
        sector_weights = analysis['diversification'].get('sector_distribution', {})

        for holding in holdings:
            # USD 기준 비중 계산
            holding_value_usd = holding.get('total_value_usd', holding['total_value'])
            current_weight = (holding_value_usd / total_value_usd) * 100
            target_weight = current_weight

            ticker = holding['ticker']
            action_type = "HOLD"
            reason = "Optimal allocation"

            # 1. 개별 종목 비중 조정
            if current_weight > self.TARGET_ALLOCATION['single_stock_max']:
                target_weight = self.TARGET_ALLOCATION['single_stock_max']
                action_type = "REDUCE"
                reason = f"Overweight: {current_weight:.1f}% → {target_weight:.1f}%"

            elif current_weight < self.TARGET_ALLOCATION['single_stock_min']:
                target_weight = self.TARGET_ALLOCATION['single_stock_min']
                action_type = "INCREASE"
                reason = f"Underweight: {current_weight:.1f}% → {target_weight:.1f}%"

            # 2. 섹터 비중 조정
            sector = holding.get('sector', 'Unknown')
            if sector in sector_weights:
                sector_weight = sector_weights[sector]
                if sector_weight > self.TARGET_ALLOCATION['sector_max']:
                    # 섹터 비중이 높으면 해당 섹터 종목 감소
                    target_weight = min(target_weight, current_weight * 0.8)
                    action_type = "REDUCE"
                    reason = f"Sector overweight: {sector} {sector_weight:.1f}%"

            # 3. 리스크 축소 (proposal_type이 RISK_REDUCTION인 경우)
            if proposal_type == "RISK_REDUCTION":
                # 변동성이 높은 종목 비중 축소
                if holding.get('gain_percent', 0) < -10:
                    target_weight = current_weight * 0.7
                    action_type = "REDUCE"
                    reason = "Risk reduction: High volatility"

            # 액션이 필요한 경우만 추가
            if abs(target_weight - current_weight) > 1.0:  # 1% 이상 차이
                # 원래 통화 기준으로 목표 주식 수 계산
                target_value = (target_weight / 100) * holding['total_value']
                target_shares = int(target_value / holding['current_price'])
                shares_diff = target_shares - holding['shares']

                actions.append({
                    'ticker': ticker,
                    'action': action_type,
                    'current_weight': round(current_weight, 2),
                    'target_weight': round(target_weight, 2),
                    'current_shares': holding['shares'],
                    'target_shares': target_shares,
                    'shares_diff': shares_diff,
                    'current_price': holding['current_price'],
                    'amount': round(abs(shares_diff) * holding['current_price'], 2),
                    'reason': reason,
                    'currency': holding.get('currency', 'USD')
                })

        return actions

    def _calculate_expected_impact(
        self,
        holdings: List[Dict],
        actions: List[Dict],
        current_analysis: Dict
    ) -> Dict:
        """리밸런싱 예상 효과 계산"""
        # 현재 지표
        current_risk = current_analysis['risk'].get('volatility', 15.0)
        current_diversity = current_analysis['diversification'].get('sector_diversity_score', 50.0)

        # 목표 지표 (단순화된 추정)
        # 리밸런싱 후 리스크 10% 감소 예상
        target_risk = current_risk * 0.9

        # 다양성 10% 개선 예상
        target_diversity = min(100.0, current_diversity * 1.1)

        # 수익률 변화 (보수적 추정: 0%)
        return_change = 0.0

        # 리스크 변화
        risk_change = target_risk - current_risk

        return {
            'target_risk_score': round(target_risk, 2),
            'target_diversification': round(target_diversity, 2),
            'return_change': round(return_change, 2),
            'risk_change': round(risk_change, 2)
        }

    async def save_proposal(self, proposal: Dict) -> RebalanceProposal:
        """제안을 데이터베이스에 저장"""
        db_proposal = RebalanceProposal(**proposal)
        self.db.add(db_proposal)
        self.db.commit()
        self.db.refresh(db_proposal)

        return db_proposal

    async def execute_proposal(self, proposal_id: int):
        """리밸런싱 제안 실행

        실제 거래는 하지 않고, 포트폴리오 데이터만 업데이트
        """
        proposal = self.db.query(RebalanceProposal).filter(
            RebalanceProposal.id == proposal_id
        ).first()

        if not proposal or proposal.status != 'PENDING':
            raise ValueError("Invalid proposal or already executed")

        actions = json.loads(proposal.proposed_actions)

        # 포트폴리오 업데이트
        for action in actions:
            ticker = action['ticker']
            target_shares = action['target_shares']

            # 기존 보유량 업데이트
            holding = self.db.query(Holding).filter(
                Holding.portfolio_id == proposal.portfolio_id,
                Holding.ticker == ticker
            ).first()

            if holding:
                if target_shares == 0:
                    # 전량 매도
                    self.db.delete(holding)
                else:
                    # 수량 조정
                    holding.shares = target_shares

        # 제안 상태 업데이트
        proposal.status = 'EXECUTED'
        proposal.executed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.db.commit()

        return proposal
