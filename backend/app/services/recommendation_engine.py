"""AI-Powered Stock Recommendation Engine - AI 기반 종목 추천 시스템"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.sector import StockInfo, StockRecommendation, SectorType, AssetType
from app.services.data_fetcher import StockDataFetcher
from app.ml.predictor import StockPredictor
from app.ml.gru_predictor import GRUPredictor


class RecommendationEngine:
    """AI 기반 종목 추천 엔진

    다음 요소들을 종합하여 추천:
    1. AI 예측 점수 (LSTM/GRU 모델)
    2. 기술적 지표 (RSI, MACD, Bollinger Bands)
    3. 다각화 점수 (섹터, 지역)
    4. 모멘텀 점수
    """

    def __init__(self, db: Session):
        self.db = db
        self.models_dir = "models"

    async def generate_recommendations(
        self,
        portfolio_id: Optional[int] = None,
        focus_sectors: Optional[List[str]] = None,
        max_recommendations: int = 10
    ) -> List[Dict]:
        """종목 추천 생성

        Args:
            portfolio_id: 포트폴리오 ID (있으면 포트폴리오 기반 추천)
            focus_sectors: 관심 섹터 리스트
            max_recommendations: 최대 추천 개수

        Returns:
            추천 종목 리스트
        """
        # 현재 포트폴리오 분석
        current_holdings = {}
        if portfolio_id:
            holdings = self.db.query(Holding).filter(
                Holding.portfolio_id == portfolio_id
            ).all()
            current_holdings = {h.ticker: h for h in holdings}

        # 추천 후보 종목 가져오기
        candidate_stocks = self._get_candidate_stocks(focus_sectors)

        # 각 종목 평가
        recommendations = []
        for stock in candidate_stocks:
            # 이미 보유 중인 종목은 추가 매수/매도 판단
            is_holding = stock.ticker in current_holdings

            # 종목 평가
            evaluation = await self._evaluate_stock(
                stock,
                portfolio_id,
                current_holdings
            )

            if evaluation:
                recommendations.append(evaluation)

        # 점수순 정렬
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)

        # 상위 N개 추천
        return recommendations[:max_recommendations]

    def _get_candidate_stocks(self, focus_sectors: Optional[List[str]] = None) -> List[StockInfo]:
        """추천 후보 종목 가져오기"""
        query = self.db.query(StockInfo)

        # 섹터 필터
        if focus_sectors:
            sector_enums = [SectorType[s] for s in focus_sectors if s in SectorType.__members__]
            if sector_enums:
                query = query.filter(StockInfo.sector.in_(sector_enums))

        # 훈련된 모델이 있는 종목만
        all_stocks = query.all()
        candidate_stocks = []

        for stock in all_stocks:
            model_filename = f"{stock.ticker.replace('.', '_')}_LSTM_model.h5"
            gru_filename = f"{stock.ticker.replace('.', '_')}_GRU_model.h5"
            model_path = os.path.join(self.models_dir, model_filename)
            gru_path = os.path.join(self.models_dir, gru_filename)

            if os.path.exists(model_path) or os.path.exists(gru_path):
                candidate_stocks.append(stock)

        return candidate_stocks

    async def _evaluate_stock(
        self,
        stock: StockInfo,
        portfolio_id: Optional[int],
        current_holdings: Dict
    ) -> Optional[Dict]:
        """종목 평가 및 점수 계산"""
        try:
            # 가격 데이터 가져오기
            price_data = StockDataFetcher.fetch_yahoo_finance(stock.ticker, period="1y")
            if price_data is None or price_data.empty or len(price_data) < 60:
                return None

            # 1. AI 예측 점수
            ai_score = await self._calculate_ai_prediction_score(stock.ticker, price_data)

            # 2. 기술적 분석 점수
            technical_score = self._calculate_technical_score(price_data)

            # 3. 모멘텀 점수
            momentum_score = self._calculate_momentum_score(price_data)

            # 4. 다각화 점수 (포트폴리오가 있는 경우)
            diversification_score = 0.5  # 기본값
            if portfolio_id and current_holdings:
                diversification_score = self._calculate_diversification_benefit(
                    stock, current_holdings
                )

            # 종합 점수 계산 (가중 평균)
            weights = {
                'ai': 0.35,
                'technical': 0.25,
                'momentum': 0.20,
                'diversification': 0.20
            }

            confidence_score = (
                ai_score * weights['ai'] +
                technical_score * weights['technical'] +
                momentum_score * weights['momentum'] +
                diversification_score * weights['diversification']
            )

            # 매매 액션 결정
            action, reason_category, reason_detail = self._determine_action(
                stock.ticker,
                current_holdings,
                confidence_score,
                ai_score,
                technical_score
            )

            # 목표 비중 계산
            target_weight = self._calculate_target_weight(
                confidence_score,
                stock.is_etf
            )

            current_price = float(price_data['close'].iloc[-1])

            return {
                'ticker': stock.ticker,
                'name': stock.name,
                'action': action,
                'confidence_score': round(confidence_score, 3),
                'target_weight': round(target_weight, 2),
                'reason_category': reason_category,
                'reason_detail': reason_detail,
                'ai_prediction_score': round(ai_score, 3),
                'technical_score': round(technical_score, 3),
                'momentum_score': round(momentum_score, 3),
                'diversification_score': round(diversification_score, 3),
                'current_price': round(current_price, 2),
                'sector': stock.sector.value if stock.sector else None,
                'is_etf': stock.is_etf,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'expires_at': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f"Error evaluating {stock.ticker}: {e}")
            return None

    async def _calculate_ai_prediction_score(self, ticker: str, price_data: pd.DataFrame) -> float:
        """AI 예측 점수 계산 (0.0 - 1.0)"""
        try:
            # 모델 파일 찾기 (LSTM 또는 GRU)
            model_filename = f"{ticker.replace('.', '_')}_LSTM_model.h5"
            gru_filename = f"{ticker.replace('.', '_')}_GRU_model.h5"
            model_path = os.path.join(self.models_dir, model_filename)
            gru_path = os.path.join(self.models_dir, gru_filename)

            predictor = None
            if os.path.exists(gru_path):
                predictor = GRUPredictor(model_path=gru_path)
            elif os.path.exists(model_path):
                predictor = StockPredictor(model_path=model_path)
            else:
                return 0.5  # 모델 없으면 중립

            # 예측 실행
            prediction = predictor.predict(price_data.tail(60))

            # 예측 상승률을 점수로 변환 (-10% ~ +10% → 0.0 ~ 1.0)
            change_percent = prediction['change_percent']
            confidence = prediction['confidence']

            # 점수 = 예측 상승률 정규화 * 신뢰도
            # -10% 이하 = 0.0, +10% 이상 = 1.0
            normalized_change = (change_percent + 10) / 20
            normalized_change = max(0.0, min(1.0, normalized_change))

            score = normalized_change * confidence

            return score

        except Exception as e:
            print(f"AI prediction error for {ticker}: {e}")
            return 0.5

    def _calculate_technical_score(self, price_data: pd.DataFrame) -> float:
        """기술적 분석 점수 (RSI, MACD, Bollinger Bands)"""
        try:
            close = price_data['close']

            # RSI (Relative Strength Index)
            rsi = self._calculate_rsi(close, period=14)
            rsi_score = self._normalize_rsi(rsi)

            # MACD
            macd_score = self._calculate_macd_score(close)

            # Bollinger Bands
            bb_score = self._calculate_bollinger_score(close)

            # 가중 평균
            technical_score = (rsi_score * 0.4 + macd_score * 0.3 + bb_score * 0.3)

            return max(0.0, min(1.0, technical_score))

        except Exception as e:
            print(f"Technical analysis error: {e}")
            return 0.5

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def _normalize_rsi(self, rsi: float) -> float:
        """RSI를 점수로 변환 (0-1)

        RSI < 30: 과매도 (매수 신호) → 높은 점수
        RSI > 70: 과매수 (매도 신호) → 낮은 점수
        """
        if rsi < 30:
            return 0.8 + (30 - rsi) / 100  # 0.8 - 1.0
        elif rsi > 70:
            return 0.2 - (rsi - 70) / 100  # 0.0 - 0.2
        else:
            # 30-70 사이: 중립 구간
            return 0.4 + (50 - abs(rsi - 50)) / 100  # 0.4 - 0.6

    def _calculate_macd_score(self, prices: pd.Series) -> float:
        """MACD 점수 계산"""
        try:
            # MACD 계산
            exp1 = prices.ewm(span=12, adjust=False).mean()
            exp2 = prices.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()

            # 최근 MACD 크로스오버 확인
            macd_diff = macd.iloc[-1] - signal.iloc[-1]

            # MACD가 시그널 위에 있으면 상승 신호
            if macd_diff > 0:
                return 0.6 + min(0.4, abs(macd_diff) / prices.iloc[-1] * 100)
            else:
                return 0.4 - min(0.4, abs(macd_diff) / prices.iloc[-1] * 100)

        except:
            return 0.5

    def _calculate_bollinger_score(self, prices: pd.Series, period: int = 20) -> float:
        """볼린저 밴드 점수"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()

            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)

            current_price = prices.iloc[-1]
            current_sma = sma.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]

            # 현재 가격이 밴드 내 어디에 위치하는지 (0-1)
            band_position = (current_price - current_lower) / (current_upper - current_lower)

            # 하단 근처 (0-0.2): 과매도 → 높은 점수
            # 상단 근처 (0.8-1.0): 과매수 → 낮은 점수
            if band_position < 0.2:
                return 0.8
            elif band_position > 0.8:
                return 0.2
            else:
                return 0.5

        except:
            return 0.5

    def _calculate_momentum_score(self, price_data: pd.DataFrame) -> float:
        """모멘텀 점수 (최근 추세)"""
        try:
            close = price_data['close']

            # 여러 기간의 수익률
            returns_5d = (close.iloc[-1] / close.iloc[-6] - 1)
            returns_20d = (close.iloc[-1] / close.iloc[-21] - 1)
            returns_60d = (close.iloc[-1] / close.iloc[-61] - 1)

            # 가중 평균 (최근이 더 중요)
            momentum = (returns_5d * 0.5 + returns_20d * 0.3 + returns_60d * 0.2)

            # -20% ~ +20% 를 0-1로 정규화
            normalized = (momentum + 0.2) / 0.4
            return max(0.0, min(1.0, normalized))

        except:
            return 0.5

    def _calculate_diversification_benefit(
        self,
        stock: StockInfo,
        current_holdings: Dict
    ) -> float:
        """다각화 기여도 점수"""
        # 섹터 다각화
        current_sectors = set()
        for ticker, holding in current_holdings.items():
            stock_info = self.db.query(StockInfo).filter(StockInfo.ticker == ticker).first()
            if stock_info and stock_info.sector:
                current_sectors.add(stock_info.sector.value)

        # 새로운 섹터면 높은 점수
        if stock.sector and stock.sector.value not in current_sectors:
            sector_score = 0.8
        else:
            sector_score = 0.3

        # 지역 다각화
        current_countries = set()
        for ticker, holding in current_holdings.items():
            stock_info = self.db.query(StockInfo).filter(StockInfo.ticker == ticker).first()
            if stock_info:
                current_countries.add(stock_info.country)

        if stock.country not in current_countries:
            geo_score = 0.7
        else:
            geo_score = 0.4

        # ETF는 자체적으로 다각화 효과
        etf_bonus = 0.2 if stock.is_etf else 0.0

        return min(1.0, (sector_score * 0.5 + geo_score * 0.3 + etf_bonus * 0.2))

    def _determine_action(
        self,
        ticker: str,
        current_holdings: Dict,
        confidence_score: float,
        ai_score: float,
        technical_score: float
    ) -> tuple:
        """매매 액션 결정"""
        is_holding = ticker in current_holdings

        # 보유 중인 종목
        if is_holding:
            if confidence_score < 0.3:
                return "SELL", "LOW_CONFIDENCE", f"신뢰도 낮음 ({confidence_score:.2f})"
            elif confidence_score < 0.5:
                return "REDUCE", "RISK_MANAGEMENT", f"리스크 관리 ({confidence_score:.2f})"
            elif confidence_score > 0.7:
                return "ADD", "HIGH_CONFIDENCE", f"추가 매수 기회 ({confidence_score:.2f})"
            else:
                return "HOLD", "NEUTRAL", f"현 상태 유지 ({confidence_score:.2f})"

        # 미보유 종목
        else:
            if confidence_score > 0.7:
                reason = []
                if ai_score > 0.7:
                    reason.append("AI 예측 긍정적")
                if technical_score > 0.7:
                    reason.append("기술적 지표 양호")

                return "BUY", "HIGH_CONFIDENCE", ", ".join(reason) or f"높은 신뢰도 ({confidence_score:.2f})"
            elif confidence_score > 0.6:
                return "BUY", "DIVERSIFICATION", f"다각화 기회 ({confidence_score:.2f})"
            else:
                return "HOLD", "WATCH", f"관망 ({confidence_score:.2f})"

    def _calculate_target_weight(self, confidence_score: float, is_etf: int) -> float:
        """목표 포트폴리오 비중 계산 (%)"""
        if is_etf:
            # ETF는 더 높은 비중 허용
            base_weight = 15.0
        else:
            # 개별 종목
            base_weight = 8.0

        # 신뢰도에 따라 조정
        target_weight = base_weight * confidence_score

        return max(2.0, min(25.0, target_weight))

    async def save_recommendations(
        self,
        recommendations: List[Dict],
        portfolio_id: Optional[int] = None
    ):
        """추천 결과를 데이터베이스에 저장"""
        for rec in recommendations:
            recommendation = StockRecommendation(
                portfolio_id=portfolio_id,
                ticker=rec['ticker'],
                action=rec['action'],
                confidence_score=rec['confidence_score'],
                target_weight=rec['target_weight'],
                reason_category=rec['reason_category'],
                reason_detail=rec['reason_detail'],
                ai_prediction_score=rec['ai_prediction_score'],
                technical_score=rec['technical_score'],
                diversification_score=rec['diversification_score'],
                created_at=rec['created_at'],
                expires_at=rec['expires_at'],
                is_active=1
            )

            self.db.add(recommendation)

        self.db.commit()
