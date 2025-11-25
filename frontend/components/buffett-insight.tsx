'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, DollarSign, Target } from 'lucide-react'

interface BuffettInsightProps {
  ticker: string
  prediction?: any
  stockInfo?: any
  compact?: boolean
}

interface MarketData {
  currentPrice: number
  news?: string[]
  financials?: {
    pe?: number
    pb?: number
    roe?: number
    debtToEquity?: number
  }
}

export function BuffettInsight({ ticker, prediction, stockInfo, compact = false }: BuffettInsightProps) {
  const [insight, setInsight] = useState<string>('')
  const [rating, setRating] = useState<'buy' | 'hold' | 'sell' | 'research'>('research')
  const [marketData, setMarketData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    generateBuffettInsight()
  }, [ticker, prediction])

  const generateBuffettInsight = () => {
    setLoading(true)

    // Buffett's investment philosophy
    const insights = {
      // 매수 추천 (AI confidence > 0.7 and predicted change > 3%)
      strongBuy: [
        `"${getStockName()}, 이것은 내가 좋아하는 종류의 기업이군요. 좋은 가격에 훌륭한 기업을 사는 것, 이것이 바로 투자의 본질입니다. 시장이 두려워할 때가 바로 우리가 탐욕스러워야 할 때죠."`,
        `"이 주식은 내재가치 대비 저평가되어 있습니다. 10년 후에도 이 회사를 보유하고 싶은가요? 그렇다면 지금이 매수 시점입니다. 가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것입니다."`,
        `"${getStockName()}의 경영진과 사업 모델이 마음에 듭니다. 좋은 기업을 적정 가격에 사는 것이 적정한 기업을 좋은 가격에 사는 것보다 훨씬 낫습니다. 이것은 찰리 멍거가 가르쳐준 교훈이죠."`,
      ],
      buy: [
        `"${getStockName()}, 흥미로운 기업이네요. 단기 변동성에 흔들리지 마세요. 우리의 투자 기간은 '영원'입니다. 시장이 폭락할 때 이 주식을 더 살 준비가 되어 있어야 합니다."`,
        `"이 회사는 경쟁 우위가 있는 것 같습니다. 해자(moat)가 깊고 넓은 기업을 찾으세요. 경쟁자들이 쉽게 침범할 수 없는 그런 기업 말입니다."`,
        `"주가가 내재가치보다 낮다면, 이것은 기회입니다. 다만 비즈니스를 이해하지 못한다면 투자하지 마세요. 이해할 수 없는 것에 투자하는 것은 도박입니다."`,
      ],
      hold: [
        `"${getStockName()}, 좋은 기업이지만 지금은 적정 가격입니다. 인내심을 가지세요. 시장 가격과 내재 가치 사이에 안전 마진이 생길 때까지 기다리는 것도 투자의 일부입니다."`,
        `"이 주식을 이미 보유하고 있다면 계속 보유하세요. 하지만 지금 당장 새로 매수할 만큼 매력적이지는 않습니다. 훌륭한 기업도 때로는 비싸게 거래됩니다."`,
        `"단기 실적에 너무 집착하지 마세요. 나는 5년, 10년 후의 이 회사를 봅니다. 하지만 지금은 더 나은 기회를 기다리는 것이 현명합니다."`,
      ],
      sell: [
        `"${getStockName()}, 이 가격에서는 매력이 없습니다. 시장이 탐욕스러울 때가 바로 우리가 두려워해야 할 때입니다. 더 나은 기회가 올 것입니다."`,
        `"주가가 내재가치를 크게 초과했습니다. 가격과 가치를 혼동하지 마세요. 이익을 실현하고 더 저평가된 기회를 찾아보세요."`,
        `"과대평가된 주식을 파는 것은 실수가 아닙니다. 오히려 현명한 결정입니다. 캐시를 보유하고 더 나은 기회를 기다리세요."`,
      ],
      caution: [
        `"${getStockName()}, 이 기업의 비즈니스 모델을 충분히 이해하지 못했다면 투자하지 마세요. 나는 내가 이해하는 범위 안에서만 투자합니다."`,
        `"변동성이 큽니다. 이것은 위험이 아니라 기회일 수 있지만, 당신의 능력 범위(circle of competence) 안에 있는지 확인하세요."`,
        `"단기 트레이딩은 내 스타일이 아닙니다. 장기적으로 이 회사가 가치를 창출할 수 있는지가 중요합니다."`,
      ],
    }

    // Determine rating based on AI prediction
    let selectedInsights: string[] = []
    let selectedRating: 'buy' | 'hold' | 'sell' | 'research' = 'research'

    if (prediction) {
      const confidence = prediction.confidence || 0
      const changePercent = prediction.change_percent || prediction.predicted_change_percent || 0

      if (prediction.action === 'BUY' && confidence > 0.7 && changePercent > 3) {
        selectedInsights = insights.strongBuy
        selectedRating = 'buy'
      } else if (prediction.action === 'BUY' && (confidence > 0.6 || changePercent > 2)) {
        selectedInsights = insights.buy
        selectedRating = 'buy'
      } else if (prediction.action === 'SELL' || changePercent < -3) {
        selectedInsights = insights.sell
        selectedRating = 'sell'
      } else if (Math.abs(changePercent) < 2) {
        selectedInsights = insights.hold
        selectedRating = 'hold'
      } else {
        selectedInsights = insights.caution
        selectedRating = 'research'
      }
    } else {
      selectedInsights = insights.caution
    }

    // Pick random insight
    const randomInsight = selectedInsights[Math.floor(Math.random() * selectedInsights.length)]
    setInsight(randomInsight)
    setRating(selectedRating)
    setLoading(false)
  }

  const getStockName = () => {
    if (stockInfo?.name) return stockInfo.name
    const stockNames: Record<string, string> = {
      'AAPL': 'Apple',
      'GOOGL': 'Google',
      'MSFT': 'Microsoft',
      'AMZN': 'Amazon',
      'META': 'Meta',
      'TSLA': 'Tesla',
      'NVDA': 'NVIDIA',
      '005930.KS': '삼성전자',
      '000660.KS': 'SK하이닉스',
      '035420.KS': 'NAVER',
      '035720.KS': '카카오',
    }
    return stockNames[ticker] || ticker
  }

  const getRatingIcon = () => {
    switch (rating) {
      case 'buy':
        return <TrendingUp className="w-5 h-5 text-green-600" />
      case 'sell':
        return <TrendingDown className="w-5 h-5 text-red-600" />
      case 'hold':
        return <Target className="w-5 h-5 text-blue-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
    }
  }

  const getRatingText = () => {
    switch (rating) {
      case 'buy':
        return '매수 고려'
      case 'sell':
        return '매도 고려'
      case 'hold':
        return '보유 유지'
      default:
        return '추가 조사 필요'
    }
  }

  const getRatingColor = () => {
    switch (rating) {
      case 'buy':
        return 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800'
      case 'sell':
        return 'bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800'
      case 'hold':
        return 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800'
      default:
        return 'bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800'
    }
  }

  if (loading) {
    return (
      <div className={`border rounded-lg p-4 ${compact ? 'p-3' : 'p-6'} bg-muted/30 animate-pulse`}>
        <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-muted rounded w-full"></div>
      </div>
    )
  }

  if (compact) {
    return (
      <div className={`border rounded-lg p-3 ${getRatingColor()}`}>
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-1">
            {getRatingIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm italic line-clamp-2">
              {insight}
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Get detailed analysis based on prediction
  const getDetailedAnalysis = () => {
    if (!prediction) return null

    const confidence = prediction.confidence || 0
    const changePercent = prediction.change_percent || prediction.predicted_change_percent || 0
    const action = prediction.action

    return {
      analysis: action === 'BUY' && confidence > 0.7
        ? `이 기업은 현재 시장에서 과소평가되어 있을 가능성이 큽니다. AI 모델의 높은 신뢰도(${(confidence * 100).toFixed(0)}%)와 ${changePercent > 0 ? '+' : ''}${changePercent.toFixed(1)}%의 예상 변동률은 긍정적인 신호입니다. 하지만 단기 변동성에 흔들리지 말고, 기업의 펀더멘털을 깊이 들여다봐야 합니다.`
        : action === 'BUY'
        ? `잠재력은 보이지만, 신중한 접근이 필요합니다. AI 신뢰도 ${(confidence * 100).toFixed(0)}%는 괜찮은 수준이지만, 본인의 능력 범위(circle of competence) 안에서 이 기업을 충분히 이해하고 있는지 확인하세요. 이해하지 못하는 것에 투자하는 것은 투기입니다.`
        : action === 'SELL'
        ? `현재 가격은 내재가치를 초과한 것으로 보입니다. 시장이 탐욕스러울 때가 바로 우리가 두려워해야 할 때입니다. 이익을 실현하고 더 매력적인 기회를 찾아보는 것도 현명한 전략입니다.`
        : `변동성이 예상됩니다. 이럴 때일수록 기업의 본질을 파악하는 것이 중요합니다. 단기적 가격 움직임보다는 10년 후 이 회사가 어디에 있을지를 상상해 보세요.`,

      keyPoints: action === 'BUY' && confidence > 0.7
        ? [
            '🎯 경쟁 우위(Economic Moat): 이 회사만의 지속가능한 경쟁력이 있는지 확인하세요',
            '💰 안전 마진(Margin of Safety): 현재 가격이 내재가치 대비 충분한 여유가 있는지 점검하세요',
            '📊 수익성 지표: 꾸준한 현금흐름과 높은 자기자본이익률(ROE)을 확인하세요',
            '👥 경영진 품질: 주주 이익을 최우선하는 정직하고 유능한 경영진인지 살펴보세요'
          ]
        : action === 'BUY'
        ? [
            '🔍 비즈니스 이해: 이 회사가 10년 후에도 존재할 수 있는 사업을 하는지 평가하세요',
            '📈 장기 성장성: 단기 실적보다 장기적 성장 가능성에 집중하세요',
            '💪 재무 건전성: 부채비율과 유동성을 체크하세요',
            '⏰ 인내심: 좋은 가격이 될 때까지 기다릴 준비가 되어 있나요?'
          ]
        : action === 'SELL'
        ? [
            '💸 이익 실현: 과대평가 구간에서 이익을 확정하는 것도 현명한 전략입니다',
            '🔄 기회비용: 이 돈으로 더 나은 투자 기회를 찾을 수 있나요?',
            '📉 리스크 관리: 고평가 위험을 피하는 것도 투자의 기술입니다',
            '🎯 재진입 전략: 가격이 적정 수준으로 내려올 때를 대비하세요'
          ]
        : [
            '🤔 능력 범위: 이 기업을 정말 이해하고 계신가요?',
            '📚 추가 조사: 재무제표, 산업 동향, 경쟁사 분석을 해보세요',
            '⏳ 서두르지 마세요: 완벽한 기회는 기다리는 자에게 옵니다',
            '💡 학습: 이해가 안 되면 이해할 수 있는 것에 투자하세요'
          ]
    }
  }

  const detailedInfo = getDetailedAnalysis()

  return (
    <div className={`border rounded-lg p-6 ${getRatingColor()}`}>
      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        <div className="flex-shrink-0 p-3 rounded-full bg-white dark:bg-gray-800 shadow-sm">
          <DollarSign className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-bold">워렌 버핏의 투자 철학</h3>
            <span className="flex items-center gap-1 px-3 py-1 rounded-full bg-white dark:bg-gray-800 text-sm font-semibold shadow-sm">
              {getRatingIcon()}
              {getRatingText()}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">
            "오마하의 현인"이 전하는 장기 가치투자 관점
          </p>
        </div>
      </div>

      {/* Main Quote */}
      <blockquote className="border-l-4 border-current pl-4 py-3 mb-4 bg-white/50 dark:bg-gray-800/50 rounded-r">
        <p className="text-base italic leading-relaxed font-medium">
          {insight}
        </p>
      </blockquote>

      {/* Detailed Analysis */}
      {detailedInfo && (
        <div className="space-y-4 mb-4">
          <div className="p-4 bg-white/70 dark:bg-gray-800/70 rounded-lg">
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              투자 분석
            </h4>
            <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
              {detailedInfo.analysis}
            </p>
          </div>

          <div className="p-4 bg-white/70 dark:bg-gray-800/70 rounded-lg">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Target className="w-4 h-4" />
              체크리스트
            </h4>
            <ul className="space-y-2">
              {detailedInfo.keyPoints.map((point, idx) => (
                <li key={idx} className="text-sm leading-relaxed text-gray-700 dark:text-gray-300 flex items-start gap-2">
                  <span className="flex-shrink-0">{point.split(' ')[0]}</span>
                  <span>{point.substring(point.indexOf(' ') + 1)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Investment Principles */}
      <div className="mt-4 pt-4 border-t space-y-2">
        <p className="text-xs text-muted-foreground leading-relaxed">
          💡 <strong>버핏의 황금률:</strong> "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1."
        </p>
        <p className="text-xs text-muted-foreground leading-relaxed">
          📖 <strong>투자 원칙:</strong> 장기적 관점에서 기업의 본질적 가치를 평가하고, 충분한 안전 마진(Margin of Safety)을 확보한 뒤 투자하세요.
          시장의 단기 변동성은 진정한 투자자에게 기회입니다.
        </p>
        <p className="text-xs text-muted-foreground leading-relaxed">
          🎓 <strong>능력 범위:</strong> "자신의 능력 범위를 아는 것과 그 범위를 넓히는 것 중, 전자가 훨씬 더 중요합니다."
          이해하지 못하는 것에는 투자하지 마세요.
        </p>
      </div>
    </div>
  )
}
