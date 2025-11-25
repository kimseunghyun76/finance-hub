"""Investment insight generation service"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session

from app.models.investment_insight import InvestmentInsight


class InvestmentInsightService:
    """Generate and cache AI-powered investment insights"""

    def __init__(self, db: Session):
        self.db = db
        self.cache_days = 7  # Cache for 7 days

    def get_or_generate_insight(self, ticker: str, stock_data: Optional[Dict] = None) -> Optional[InvestmentInsight]:
        """Get cached insight or generate new one"""
        # Check cache first
        cached = self._get_cached_insight(ticker)
        if cached:
            return cached

        # Generate new insight
        return self._generate_insight(ticker, stock_data)

    def _get_cached_insight(self, ticker: str) -> Optional[InvestmentInsight]:
        """Get cached insight if still valid"""
        insight = self.db.query(InvestmentInsight).filter(
            InvestmentInsight.ticker == ticker,
            InvestmentInsight.is_valid == True,
            InvestmentInsight.expires_at > datetime.utcnow()
        ).first()

        return insight

    def _generate_insight(self, ticker: str, stock_data: Optional[Dict] = None) -> InvestmentInsight:
        """Generate new investment insight"""
        # Extract stock fundamentals
        current_price = stock_data.get('price', 0) if stock_data else 0
        pe_ratio = stock_data.get('pe_ratio') if stock_data else None
        market_cap = stock_data.get('market_cap') if stock_data else None

        # Generate analyses based on investment philosophies
        buffett_analysis = self._generate_buffett_analysis(ticker, current_price, pe_ratio, market_cap)
        lynch_analysis = self._generate_lynch_analysis(ticker, current_price, pe_ratio)
        graham_analysis = self._generate_graham_analysis(ticker, current_price, pe_ratio)

        # Calculate overall rating
        rating, confidence = self._calculate_rating(pe_ratio, current_price)

        # Create insight
        insight = InvestmentInsight(
            ticker=ticker,
            buffett_analysis=buffett_analysis,
            lynch_analysis=lynch_analysis,
            graham_analysis=graham_analysis,
            current_price=current_price,
            pe_ratio=pe_ratio,
            market_cap=market_cap,
            generated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=self.cache_days),
            is_valid=True,
            ai_model_used="rule-based-v1",
            overall_rating=rating,
            confidence_score=confidence,
            key_strengths=json.dumps(self._get_strengths(ticker, pe_ratio)),
            key_risks=json.dumps(self._get_risks(ticker, pe_ratio))
        )

        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)

        return insight

    def _generate_buffett_analysis(self, ticker: str, price: float, pe_ratio: Optional[float], market_cap: Optional[float]) -> str:
        """Generate Warren Buffett style analysis for specific stock"""
        analysis = f"**{ticker}에 대한 워렌 버핏의 투자 관점**\n\n"

        if pe_ratio and pe_ratio < 15:
            analysis += f"'{ticker}'는 현재 P/E 비율이 {pe_ratio:.1f}로, 내재가치 대비 저평가되어 있을 가능성이 있습니다. "
            analysis += "버핏은 '훌륭한 기업을 적절한 가격에 사는 것'을 선호하며, 이는 매력적인 진입 시점이 될 수 있습니다.\n\n"
        elif pe_ratio and pe_ratio > 30:
            analysis += f"'{ticker}'의 P/E 비율이 {pe_ratio:.1f}로 높은 편입니다. "
            analysis += "버핏은 '가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것'이라고 말했습니다. "
            analysis += "높은 밸류에이션이 미래 성장을 정당화하는지 신중히 검토해야 합니다.\n\n"
        else:
            analysis += f"'{ticker}'는 현재 적정 밸류에이션 수준을 유지하고 있습니다. "
            analysis += "버핏의 관점에서 볼 때, 기업의 경제적 해자(competitive moat)와 경영진의 자본 배분 능력을 면밀히 살펴봐야 합니다.\n\n"

        analysis += "**핵심 투자 원칙:**\n"
        analysis += f"- {ticker}의 비즈니스 모델이 10년 후에도 지속 가능한가?\n"
        analysis += "- 경쟁우위는 확실하며, 진입장벽이 높은가?\n"
        analysis += "- 자유현금흐름(FCF)을 꾸준히 창출하고 있는가?\n"
        analysis += "- 경영진이 주주가치 창출에 집중하고 있는가?\n\n"

        analysis += "버핏의 조언: '우리가 좋아하는 보유 기간은 영원입니다.'"

        return analysis

    def _generate_lynch_analysis(self, ticker: str, price: float, pe_ratio: Optional[float]) -> str:
        """Generate Peter Lynch style analysis for specific stock"""
        analysis = f"**{ticker}에 대한 피터 린치의 투자 전략**\n\n"

        analysis += f"피터 린치는 '{ticker}' 같은 종목을 분석할 때, 먼저 '이 회사의 사업을 10살 아이에게 설명할 수 있는가?'를 묻습니다.\n\n"

        if pe_ratio:
            peg_estimate = pe_ratio / 15  # Simplified PEG ratio estimate
            if peg_estimate < 1:
                analysis += f"**PEG 비율 분석:** {ticker}의 P/E 대비 성장률을 고려하면, 이 주식은 저평가되어 있을 수 있습니다. "
                analysis += "린치는 PEG 비율이 1 이하인 종목을 선호했습니다.\n\n"
            else:
                analysis += f"**PEG 비율 분석:** {ticker}의 현재 밸류에이션은 성장률을 감안할 때 높은 편입니다. "
                analysis += "린치는 성장 대비 과도한 프리미엄이 붙은 종목은 피하라고 조언했습니다.\n\n"

        analysis += "**린치의 6가지 주식 분류:**\n"
        analysis += f"'{ticker}'가 어느 카테고리에 속하는지 파악하세요:\n"
        analysis += "- 🚀 Fast Growers (빠른 성장주)\n"
        analysis += "- 🏢 Stalwarts (우량 대형주)\n"
        analysis += "- 🔄 Cyclicals (경기순환주)\n"
        analysis += "- 💎 Turnarounds (회생주)\n"
        analysis += "- 💰 Asset Plays (자산주)\n\n"

        analysis += "**실천 조언:**\n"
        analysis += f"- {ticker} 제품을 직접 사용해보고, 품질과 시장 반응을 확인하세요\n"
        analysis += "- 친구나 가족에게 이 회사에 대해 물어보세요 (소비자 관점)\n"
        analysis += "- 분기 실적을 꾸준히 추적하고, 이익 성장세를 확인하세요\n\n"

        analysis += "린치의 명언: '당신이 이해하지 못하는 주식에 투자하지 마세요.'"

        return analysis

    def _generate_graham_analysis(self, ticker: str, price: float, pe_ratio: Optional[float]) -> str:
        """Generate Benjamin Graham style analysis for specific stock"""
        analysis = f"**{ticker}에 대한 벤자민 그레이엄의 가치투자 분석**\n\n"

        analysis += f"벤자민 그레이엄은 '{ticker}'에 투자하기 전, 철저한 재무제표 분석과 안전마진(Margin of Safety) 확보를 강조합니다.\n\n"

        if pe_ratio:
            if pe_ratio < 15:
                analysis += f"**밸류에이션 점검:** {ticker}의 P/E 비율 {pe_ratio:.1f}은 그레이엄의 기준(P/E < 15)을 충족합니다. "
                analysis += "이는 시장이 이 기업을 저평가하고 있을 가능성을 시사합니다.\n\n"
            else:
                analysis += f"**밸류에이션 경고:** {ticker}의 P/E 비율 {pe_ratio:.1f}은 그레이엄의 보수적인 기준을 초과합니다. "
                analysis += "가치투자자는 더 매력적인 진입 시점을 기다리는 것이 현명할 수 있습니다.\n\n"

        analysis += "**그레이엄의 7가지 기준 체크리스트:**\n"
        analysis += f"'{ticker}'가 다음 조건을 충족하는지 검토하세요:\n\n"
        analysis += "1. ✓ 충분한 기업 규모 (연매출 1억 달러 이상)\n"
        analysis += "2. ✓ 재무 상태가 건전한가? (유동비율 ≥ 2, 부채비율 적정)\n"
        analysis += "3. ✓ 10년간 꾸준한 배당 지급 이력\n"
        analysis += "4. ✓ 지난 10년간 적자가 없는가?\n"
        analysis += "5. ✓ 10년간 주당순이익(EPS) 성장률 ≥ 33%\n"
        analysis += "6. ✓ P/E 비율 15 이하\n"
        analysis += "7. ✓ P/B 비율 1.5 이하 (자산가치 대비)\n\n"

        analysis += "**안전마진 원칙:**\n"
        analysis += f"{ticker}의 내재가치를 계산하고, 현재가가 그보다 33% 이상 낮을 때만 투자하세요. "
        analysis += "이는 예상치 못한 리스크로부터 당신의 자본을 보호합니다.\n\n"

        analysis += "그레이엄의 교훈: '투자의 본질은 철저한 분석을 통해 원금을 지키고 적절한 수익을 얻는 것입니다.'"

        return analysis

    def _calculate_rating(self, pe_ratio: Optional[float], price: float) -> tuple:
        """Calculate overall investment rating"""
        if not pe_ratio:
            return "HOLD", 50.0

        if pe_ratio < 10:
            return "BUY", 85.0
        elif pe_ratio < 15:
            return "BUY", 70.0
        elif pe_ratio < 25:
            return "HOLD", 55.0
        else:
            return "SELL", 40.0

    def _get_strengths(self, ticker: str, pe_ratio: Optional[float]) -> list:
        """Get key strengths"""
        strengths = []
        if pe_ratio and pe_ratio < 15:
            strengths.append("저평가된 밸류에이션")
            strengths.append("매력적인 진입 시점")
        if pe_ratio and 10 < pe_ratio < 20:
            strengths.append("적정 P/E 비율 유지")
        return strengths

    def _get_risks(self, ticker: str, pe_ratio: Optional[float]) -> list:
        """Get key risks"""
        risks = []
        if pe_ratio and pe_ratio > 30:
            risks.append("높은 밸류에이션 리스크")
            risks.append("조정 가능성 존재")
        if not pe_ratio:
            risks.append("재무 데이터 부족")
        return risks

    def invalidate_cache(self, ticker: str):
        """Invalidate cached insights for a ticker"""
        self.db.query(InvestmentInsight).filter(
            InvestmentInsight.ticker == ticker
        ).update({"is_valid": False})
        self.db.commit()
