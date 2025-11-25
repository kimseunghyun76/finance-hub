'use client'

import { useEffect, useState } from 'react'
import { type StockPrediction, type AnalystPriceTarget, type StockFundamentals, stockApi } from '@/lib/api'
import { formatCurrency, formatPercent, formatDateTime, formatTimeRemaining } from '@/lib/utils'
import { Clock, Calendar, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react'

interface PredictionExplanationProps {
  prediction: StockPrediction
  currentPrice: number
  currency: 'USD' | 'KRW'
  ticker: string
  onRefresh?: () => void
}

export function PredictionExplanation({
  prediction,
  currentPrice,
  currency,
  ticker,
  onRefresh,
}: PredictionExplanationProps) {
  const [analystData, setAnalystData] = useState<AnalystPriceTarget | null>(null)
  const [fundamentals, setFundamentals] = useState<StockFundamentals | null>(null)
  const [loading, setLoading] = useState(true)
  const [fundamentalsLoading, setFundamentalsLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  // Check if prediction is expired
  const isExpired = prediction.expires_at ? new Date(prediction.expires_at) < new Date() : false

  // Auto-refresh if expired on mount
  useEffect(() => {
    if (isExpired && onRefresh && !refreshing) {
      handleRefresh()
    }
  }, [])

  const handleRefresh = async () => {
    if (!onRefresh || refreshing) return
    setRefreshing(true)
    try {
      await onRefresh()
    } finally {
      setRefreshing(false)
    }
  }

  const change = prediction.prediction.change
  const changePercent = prediction.prediction.change_percent
  const confidence = prediction.prediction.confidence

  // Determine trend direction
  const isUpward = change > 0
  const isStrong = Math.abs(changePercent) > 3
  const isConfident = confidence > 0.7

  // Load analyst data
  useEffect(() => {
    const loadAnalystData = async () => {
      try {
        const response = await stockApi.getAnalystTargets(ticker)
        setAnalystData(response.data)
      } catch (error) {
        console.error('Failed to load analyst data:', error)
        setAnalystData(null)
      } finally {
        setLoading(false)
      }
    }
    loadAnalystData()
  }, [ticker])

  // Load fundamentals data
  useEffect(() => {
    const loadFundamentals = async () => {
      try {
        const response = await stockApi.getFundamentals(ticker)
        setFundamentals(response.data)
      } catch (error) {
        console.error('Failed to load fundamentals:', error)
        setFundamentals(null)
      } finally {
        setFundamentalsLoading(false)
      }
    }
    loadFundamentals()
  }, [ticker])

  // Get reasoning based on prediction characteristics
  const getReasoningPoints = () => {
    const reasons = []

    // Price trend analysis
    if (isUpward) {
      if (isStrong) {
        reasons.push({
          icon: '📈',
          title: '강한 상승 추세',
          description: `향후 5일간 ${formatPercent(changePercent)} 상승이 예상됩니다. 최근 가격 패턴이 강한 상승 모멘텀을 보이고 있습니다.`,
        })
      } else {
        reasons.push({
          icon: '📊',
          title: '완만한 상승 추세',
          description: `향후 5일간 ${formatPercent(changePercent)} 상승이 예상됩니다. 안정적인 상승 패턴이 감지되었습니다.`,
        })
      }
    } else {
      if (isStrong) {
        reasons.push({
          icon: '📉',
          title: '하락 추세 감지',
          description: `향후 5일간 ${formatPercent(Math.abs(changePercent))} 하락이 예상됩니다. 최근 가격 패턴에서 하락 신호가 나타났습니다.`,
        })
      } else {
        reasons.push({
          icon: '➖',
          title: '횡보 또는 소폭 하락',
          description: `향후 5일간 ${formatPercent(Math.abs(changePercent))} 하락이 예상됩니다. 가격이 보합세를 유지하거나 소폭 조정될 것으로 보입니다.`,
        })
      }
    }

    // Confidence analysis
    if (isConfident) {
      reasons.push({
        icon: '✅',
        title: '높은 신뢰도',
        description: `AI 모델이 이 예측에 대해 ${Math.round(confidence * 100)}%의 높은 신뢰도를 보입니다. 과거 유사한 패턴에서 높은 정확도를 보였습니다.`,
      })
    } else {
      reasons.push({
        icon: '⚠️',
        title: '중간 신뢰도',
        description: `AI 모델의 신뢰도는 ${Math.round(confidence * 100)}%입니다. 시장 변동성이 높아 예측 불확실성이 존재합니다.`,
      })
    }

    // Model information
    reasons.push({
      icon: '🤖',
      title: 'LSTM 딥러닝 모델',
      description: '60일간의 주가 데이터를 학습하여 시계열 패턴을 분석합니다. 단기 트레이딩 패턴과 가격 변동성을 고려합니다.',
    })

    // Investment recommendation rationale
    if (prediction.action === 'BUY') {
      reasons.push({
        icon: '💰',
        title: '매수 추천 근거',
        description: '상승 추세와 긍정적인 가격 모멘텀이 예상되어 매수 기회로 판단됩니다.',
      })
    } else if (prediction.action === 'SELL') {
      reasons.push({
        icon: '💸',
        title: '매도 추천 근거',
        description: '하락 추세 또는 조정 가능성이 높아 보유 포지션 정리를 고려할 시점입니다.',
      })
    } else {
      reasons.push({
        icon: '🤝',
        title: '보유 추천 근거',
        description: '현재 포지션을 유지하며 추가적인 시장 신호를 관찰하는 것이 적절해 보입니다.',
      })
    }

    return reasons
  }

  const reasons = getReasoningPoints()

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="pb-4 border-b">
        <h3 className="text-lg font-bold mb-2">🔍 AI 예측 분석 상세</h3>
        <p className="text-sm text-muted-foreground">
          이 예측은 어떻게 만들어졌나요? 아래에서 AI 모델의 판단 근거를 확인하세요.
        </p>
      </div>

      {/* Key Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-muted/30 rounded-lg">
        <div>
          <p className="text-xs text-muted-foreground mb-1">현재가</p>
          <p className="text-lg font-bold">{formatCurrency(currentPrice, currency)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">예측가 (5일 후)</p>
          <p className={`text-lg font-bold ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(prediction.prediction.predicted_price, currency)}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">예상 변동</p>
          <p className={`text-lg font-bold ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? '+' : ''}{formatCurrency(change, currency)} ({formatPercent(changePercent)})
          </p>
        </div>
      </div>

      {/* Reasoning Points */}
      <div className="space-y-3">
        {reasons.map((reason, index) => (
          <div key={index} className="flex gap-3 p-4 border rounded-lg bg-card/50">
            <div className="text-2xl">{reason.icon}</div>
            <div className="flex-1">
              <h4 className="font-semibold mb-1">{reason.title}</h4>
              <p className="text-sm text-muted-foreground">{reason.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Analyst Price Targets Comparison */}
      {!loading && analystData && analystData.target_mean && (
        <div className="border-t pt-4">
          <h3 className="text-lg font-bold mb-4">📊 애널리스트 목표가 비교</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {/* AI vs Analyst Comparison */}
            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-3">🤖 AI 예측</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">5일 후 예측가:</span>
                  <span className="font-bold text-blue-900">{formatCurrency(prediction.prediction.predicted_price, currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">변동 예상:</span>
                  <span className={`font-bold ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {change >= 0 ? '+' : ''}{formatPercent(changePercent)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">신뢰도:</span>
                  <span className="font-bold text-blue-900">{Math.round(confidence * 100)}%</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-3">👔 애널리스트 컨센서스</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">평균 목표가:</span>
                  <span className="font-bold text-green-900">{formatCurrency(analystData.target_mean, currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">목표가 범위:</span>
                  <span className="font-bold text-green-900">
                    {formatCurrency(analystData.target_low || 0, currency)} ~ {formatCurrency(analystData.target_high || 0, currency)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">애널리스트 수:</span>
                  <span className="font-bold text-green-900">{analystData.number_of_analysts || 0}명</span>
                </div>
              </div>
            </div>
          </div>

          {/* Analyst Recommendations */}
          {analystData.recommendations && analystData.recommendations.length > 0 && (
            <div className="p-4 bg-gray-50 border rounded-lg">
              <h4 className="font-semibold mb-3">📈 애널리스트 추천 분포 (최근)</h4>
              <div className="grid grid-cols-5 gap-2 text-center text-sm">
                <div>
                  <div className="font-semibold text-green-600">강력매수</div>
                  <div className="text-2xl font-bold text-green-600">{analystData.recommendations[0].strong_buy}</div>
                </div>
                <div>
                  <div className="font-semibold text-green-500">매수</div>
                  <div className="text-2xl font-bold text-green-500">{analystData.recommendations[0].buy}</div>
                </div>
                <div>
                  <div className="font-semibold text-gray-600">보유</div>
                  <div className="text-2xl font-bold text-gray-600">{analystData.recommendations[0].hold}</div>
                </div>
                <div>
                  <div className="font-semibold text-red-500">매도</div>
                  <div className="text-2xl font-bold text-red-500">{analystData.recommendations[0].sell}</div>
                </div>
                <div>
                  <div className="font-semibold text-red-600">강력매도</div>
                  <div className="text-2xl font-bold text-red-600">{analystData.recommendations[0].strong_sell}</div>
                </div>
              </div>

              {analystData.recommendation_key && (
                <div className="mt-3 text-center">
                  <span className="text-sm text-gray-600">컨센서스: </span>
                  <span className={`font-bold ${
                    analystData.recommendation_key === 'buy' ? 'text-green-600' :
                    analystData.recommendation_key === 'sell' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {analystData.recommendation_key === 'buy' ? '매수' :
                     analystData.recommendation_key === 'sell' ? '매도' :
                     analystData.recommendation_key === 'hold' ? '보유' :
                     analystData.recommendation_key}
                  </span>
                </div>
              )}
            </div>
          )}

          <div className="mt-3 text-xs text-gray-600 text-center">
            💡 애널리스트 목표가는 주요 투자사들의 평균 의견으로, 장기적인 관점을 반영합니다.
          </div>
        </div>
      )}

      {/* Fundamental Analysis Section */}
      {!fundamentalsLoading && fundamentals && (
        <div className="border-t pt-4">
          <h3 className="text-lg font-bold mb-4">📈 펀더멘탈 분석 (전통적 가치평가)</h3>

          {/* Valuation Metrics */}
          <div className="mb-4">
            <h4 className="font-semibold text-gray-800 mb-3">💰 밸류에이션 지표</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {fundamentals.trailing_pe && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">PER (후행)</div>
                  <div className="text-lg font-bold">{fundamentals.trailing_pe.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.trailing_pe < 15 ? '저평가 📉' : fundamentals.trailing_pe > 25 ? '고평가 📈' : '적정 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.forward_pe && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">PER (전망)</div>
                  <div className="text-lg font-bold">{fundamentals.forward_pe.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.forward_pe < 15 ? '저평가 📉' : fundamentals.forward_pe > 25 ? '고평가 📈' : '적정 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.price_to_book && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">PBR (주가순자산비율)</div>
                  <div className="text-lg font-bold">{fundamentals.price_to_book.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.price_to_book < 1 ? '저평가 📉' : fundamentals.price_to_book > 3 ? '고평가 📈' : '적정 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.price_to_sales && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">PSR (주가매출비율)</div>
                  <div className="text-lg font-bold">{fundamentals.price_to_sales.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.price_to_sales < 2 ? '저평가 📉' : fundamentals.price_to_sales > 5 ? '고평가 📈' : '적정 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.peg_ratio && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">PEG Ratio</div>
                  <div className="text-lg font-bold">{fundamentals.peg_ratio.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.peg_ratio < 1 ? '저평가 📉' : fundamentals.peg_ratio > 2 ? '고평가 📈' : '적정 ➖'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Profitability Metrics */}
          <div className="mb-4">
            <h4 className="font-semibold text-gray-800 mb-3">💼 수익성 지표</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {fundamentals.return_on_equity && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">ROE (자기자본이익률)</div>
                  <div className="text-lg font-bold">{(fundamentals.return_on_equity * 100).toFixed(1)}%</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.return_on_equity > 0.15 ? '우수 ✨' : fundamentals.return_on_equity > 0.1 ? '양호 👍' : '보통 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.return_on_assets && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">ROA (총자산이익률)</div>
                  <div className="text-lg font-bold">{(fundamentals.return_on_assets * 100).toFixed(1)}%</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.return_on_assets > 0.1 ? '우수 ✨' : fundamentals.return_on_assets > 0.05 ? '양호 👍' : '보통 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.profit_margins && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">순이익률</div>
                  <div className="text-lg font-bold">{(fundamentals.profit_margins * 100).toFixed(1)}%</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.profit_margins > 0.2 ? '우수 ✨' : fundamentals.profit_margins > 0.1 ? '양호 👍' : '보통 ➖'}
                  </div>
                </div>
              )}
              {fundamentals.operating_margins && (
                <div className="p-3 bg-white border rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">영업이익률</div>
                  <div className="text-lg font-bold">{(fundamentals.operating_margins * 100).toFixed(1)}%</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fundamentals.operating_margins > 0.2 ? '우수 ✨' : fundamentals.operating_margins > 0.1 ? '양호 👍' : '보통 ➖'}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Growth Metrics */}
          {(fundamentals.earnings_growth || fundamentals.revenue_growth) && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-800 mb-3">📊 성장성 지표</h4>
              <div className="grid grid-cols-2 gap-3">
                {fundamentals.earnings_growth && (
                  <div className="p-3 bg-white border rounded-lg">
                    <div className="text-xs text-gray-600 mb-1">이익 성장률</div>
                    <div className={`text-lg font-bold ${fundamentals.earnings_growth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {fundamentals.earnings_growth > 0 ? <TrendingUp className="inline w-4 h-4 mr-1" /> : <TrendingDown className="inline w-4 h-4 mr-1" />}
                      {(fundamentals.earnings_growth * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
                {fundamentals.revenue_growth && (
                  <div className="p-3 bg-white border rounded-lg">
                    <div className="text-xs text-gray-600 mb-1">매출 성장률</div>
                    <div className={`text-lg font-bold ${fundamentals.revenue_growth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {fundamentals.revenue_growth > 0 ? <TrendingUp className="inline w-4 h-4 mr-1" /> : <TrendingDown className="inline w-4 h-4 mr-1" />}
                      {(fundamentals.revenue_growth * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Financial Health */}
          {(fundamentals.debt_to_equity || fundamentals.current_ratio || fundamentals.quick_ratio) && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-800 mb-3">🏦 재무 건전성</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {fundamentals.debt_to_equity && (
                  <div className="p-3 bg-white border rounded-lg">
                    <div className="text-xs text-gray-600 mb-1">부채비율</div>
                    <div className="text-lg font-bold">{fundamentals.debt_to_equity.toFixed(1)}%</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {fundamentals.debt_to_equity < 50 ? '안전 ✅' : fundamentals.debt_to_equity < 100 ? '양호 👍' : '주의 ⚠️'}
                    </div>
                  </div>
                )}
                {fundamentals.current_ratio && (
                  <div className="p-3 bg-white border rounded-lg">
                    <div className="text-xs text-gray-600 mb-1">유동비율</div>
                    <div className="text-lg font-bold">{fundamentals.current_ratio.toFixed(2)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {fundamentals.current_ratio > 2 ? '안전 ✅' : fundamentals.current_ratio > 1 ? '양호 👍' : '주의 ⚠️'}
                    </div>
                  </div>
                )}
                {fundamentals.quick_ratio && (
                  <div className="p-3 bg-white border rounded-lg">
                    <div className="text-xs text-gray-600 mb-1">당좌비율</div>
                    <div className="text-lg font-bold">{fundamentals.quick_ratio.toFixed(2)}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {fundamentals.quick_ratio > 1.5 ? '안전 ✅' : fundamentals.quick_ratio > 1 ? '양호 👍' : '주의 ⚠️'}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Price Range */}
          {fundamentals.fifty_two_week_high && fundamentals.fifty_two_week_low && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-800 mb-3">📍 가격 범위 (52주)</h4>
              <div className="p-4 bg-white border rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-sm">
                    <span className="text-gray-600">최저가: </span>
                    <span className="font-bold">{formatCurrency(fundamentals.fifty_two_week_low, currency)}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-600">최고가: </span>
                    <span className="font-bold">{formatCurrency(fundamentals.fifty_two_week_high, currency)}</span>
                  </div>
                </div>
                <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="absolute h-full bg-blue-500"
                    style={{
                      left: 0,
                      width: `${((currentPrice - fundamentals.fifty_two_week_low) / (fundamentals.fifty_two_week_high - fundamentals.fifty_two_week_low) * 100)}%`
                    }}
                  />
                </div>
                <div className="text-center mt-2 text-sm text-gray-600">
                  현재가는 52주 범위의 {(((currentPrice - fundamentals.fifty_two_week_low) / (fundamentals.fifty_two_week_high - fundamentals.fifty_two_week_low)) * 100).toFixed(1)}% 위치
                </div>
              </div>
            </div>
          )}

          {/* Valuation Summary */}
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 className="font-semibold text-purple-900 mb-2">🎯 종합 가치평가</h4>
            <div className="text-sm text-purple-800">
              {(() => {
                let overvaluedCount = 0
                let undervaluedCount = 0
                let total = 0

                if (fundamentals.trailing_pe) {
                  total++
                  if (fundamentals.trailing_pe < 15) undervaluedCount++
                  else if (fundamentals.trailing_pe > 25) overvaluedCount++
                }
                if (fundamentals.price_to_book) {
                  total++
                  if (fundamentals.price_to_book < 1) undervaluedCount++
                  else if (fundamentals.price_to_book > 3) overvaluedCount++
                }
                if (fundamentals.peg_ratio) {
                  total++
                  if (fundamentals.peg_ratio < 1) undervaluedCount++
                  else if (fundamentals.peg_ratio > 2) overvaluedCount++
                }

                const overvaluedPercent = total > 0 ? (overvaluedCount / total) * 100 : 0
                const undervaluedPercent = total > 0 ? (undervaluedCount / total) * 100 : 0

                if (overvaluedPercent > 60) {
                  return '⚠️ 전통적 지표 기준으로 고평가 가능성이 있습니다. AI 예측과 비교하여 신중한 판단이 필요합니다.'
                } else if (undervaluedPercent > 60) {
                  return '💎 전통적 지표 기준으로 저평가 가능성이 있습니다. AI 예측이 상승을 예상한다면 좋은 매수 기회일 수 있습니다.'
                } else {
                  return '⚖️ 전통적 지표 기준으로 적정 가격대로 판단됩니다. AI 예측을 참고하여 단기 추세를 확인하세요.'
                }
              })()}
            </div>
          </div>

          <div className="mt-3 text-xs text-gray-600 text-center">
            💡 펀더멘탈 지표는 기업의 재무 건전성과 가치를 평가하는 전통적 방법입니다.
          </div>
        </div>
      )}

      {/* Disclaimers */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="font-semibold text-yellow-900 mb-2">⚠️ 투자 유의사항</h4>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• AI 예측, 애널리스트 목표가, 펀더멘탈 지표는 모두 참고용이며, 실제 투자 결정은 본인의 판단하에 이루어져야 합니다.</li>
          <li>• 과거 데이터 기반 예측이므로 예상치 못한 시장 이벤트를 반영하지 못할 수 있습니다.</li>
          <li>• AI는 단기 예측(5일), 애널리스트는 장기 목표가, 펀더멘탈은 현재 가치평가이므로 시간 범위가 다릅니다.</li>
          <li>• 펀더멘탈 지표의 평가 기준은 일반적인 가이드라인이며, 업종과 시장 상황에 따라 달라질 수 있습니다.</li>
          <li>• 투자에 따른 모든 책임은 투자자 본인에게 있습니다.</li>
        </ul>
      </div>

      {/* Prediction Timing Information */}
      <div className={`p-4 border rounded-lg ${isExpired ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200'}`}>
        <div className="flex items-center justify-between mb-3">
          <h4 className={`font-semibold flex items-center gap-2 ${isExpired ? 'text-orange-900' : 'text-blue-900'}`}>
            <Clock className="w-4 h-4" />
            예측 시간 정보
          </h4>
          {isExpired && onRefresh && (
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-3 py-1.5 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50 text-sm font-medium"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? '갱신 중...' : '새로운 예측 생성'}
            </button>
          )}
        </div>
        {isExpired && (
          <div className="mb-3 p-3 bg-orange-100 border border-orange-300 rounded-lg">
            <p className="text-orange-800 font-medium">⏰ 이 예측은 만료되었습니다</p>
            <p className="text-sm text-orange-700 mt-1">
              새로운 예측을 생성하려면 &quot;새로운 예측 생성&quot; 버튼을 클릭하세요.
            </p>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div className="flex items-start gap-2">
            <Calendar className={`w-4 h-4 mt-0.5 ${isExpired ? 'text-orange-600' : 'text-blue-600'}`} />
            <div>
              <p className={`font-medium ${isExpired ? 'text-orange-700' : 'text-blue-700'}`}>예측 생성 시각</p>
              <p className={`font-semibold ${isExpired ? 'text-orange-900' : 'text-blue-900'}`}>{formatDateTime(prediction.created_at)}</p>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <Clock className={`w-4 h-4 mt-0.5 ${isExpired ? 'text-orange-600' : 'text-blue-600'}`} />
            <div>
              <p className={`font-medium ${isExpired ? 'text-orange-700' : 'text-blue-700'}`}>유효 기간</p>
              <p className={`font-semibold ${isExpired ? 'text-red-600' : 'text-blue-900'}`}>{formatTimeRemaining(prediction.expires_at)}</p>
              <p className={`text-xs mt-1 ${isExpired ? 'text-orange-600' : 'text-blue-600'}`}>만료 시각: {formatDateTime(prediction.expires_at)}</p>
            </div>
          </div>
        </div>
        <div className={`mt-3 text-xs ${isExpired ? 'text-orange-700' : 'text-blue-700'}`}>
          💡 예측은 1시간 동안 유효하며, 만료 후 자동으로 새로운 데이터로 재생성됩니다.
        </div>
      </div>

      {/* Model Details */}
      <div className="text-xs text-muted-foreground p-3 bg-muted/20 rounded">
        <p className="mb-1">
          <strong>모델 정보:</strong> LSTM (Long Short-Term Memory) 신경망
        </p>
        <p className="mb-1">
          <strong>학습 데이터:</strong> 최근 60일 주가 데이터 (종가, 거래량 포함)
        </p>
        <p className="mb-1">
          <strong>예측 기간:</strong> 5 거래일 (약 1주일)
        </p>
        <p>
          <strong>예측 시점:</strong> {new Date(prediction.timestamp).toLocaleString('ko-KR')}
        </p>
      </div>
    </div>
  )
}
