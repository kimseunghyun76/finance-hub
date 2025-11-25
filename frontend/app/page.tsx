'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { predictionApi, portfolioApi, holdingApi, stockApi } from '@/lib/api'
import { getStockName } from '@/lib/stock-names'
import { formatPrice, isKoreanStock } from '@/lib/utils'
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertTriangle, ArrowRight, Clock, CheckCircle, BarChart3, BookOpen } from 'lucide-react'
import { BuffettInsight } from '@/components/buffett-insight'

interface PredictionSummary {
  ticker: string
  action: string
  predicted_change_percent: number
  confidence: number
}

interface PortfolioPosition {
  ticker: string
  quantity: number
  averagePrice: number
  currentPrice: number
  profit: number
  profitPercent: number
}

interface PortfolioSummary {
  positions: PortfolioPosition[]
  totalValue: number
  totalCost: number
  totalProfit: number
  totalProfitPercent: number
  usdValue: number
  krwValue: number
  usdProfit: number
  krwProfit: number
}

export default function Home() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [predictions, setPredictions] = useState<PredictionSummary[]>([])
  const [portfolio, setPortfolio] = useState<PortfolioSummary>({
    positions: [],
    totalValue: 0,
    totalCost: 0,
    totalProfit: 0,
    totalProfitPercent: 0,
    usdValue: 0,
    krwValue: 0,
    usdProfit: 0,
    krwProfit: 0
  })
  const [loading, setLoading] = useState(true)
  const [trainedCount, setTrainedCount] = useState(0)
  const [accuracyData, setAccuracyData] = useState<{
    direction_accuracy: number
    total_predictions: number
    trained_models: number
    tested_models: number
  } | null>(null)
  const [marketData, setMarketData] = useState<{
    [key: string]: { price: number; change: number; changePercent: number }
  }>({})

  useEffect(() => {
    setMounted(true)
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Load predictions summary
      const response = await fetch('http://localhost:8001/api/v1/predictions/summary')
      const data = await response.json()

      if (data.predictions && data.predictions.length > 0) {
        const mappedPredictions = data.predictions.map((p: any) => ({
          ticker: p.ticker,
          action: p.action,
          predicted_change_percent: p.change_percent || 0,
          confidence: p.confidence || 0
        }))
        setPredictions(mappedPredictions)
      }

      // Load trained models count
      try {
        const trainedResponse = await predictionApi.getSummary()
        setTrainedCount(trainedResponse.data.trained_models?.length || 0)
      } catch (error) {
        console.error('Failed to load trained models:', error)
      }

      // Load accuracy data
      try {
        const accuracyResponse = await fetch('http://localhost:8001/api/v1/predictions/daily/accuracy')
        const accuracyJson = await accuracyResponse.json()
        if (accuracyJson.count > 0) {
          setAccuracyData({
            direction_accuracy: accuracyJson.overall.direction_accuracy,
            total_predictions: accuracyJson.count,
            trained_models: accuracyJson.trained_models,
            tested_models: accuracyJson.tested_models
          })
        }
      } catch (error) {
        console.error('Failed to load accuracy data:', error)
      }

      // Load portfolio
      await loadPortfolioData()

      // Load market data
      await loadMarketData()
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadMarketData = async () => {
    const tickers = ['SPY', 'DIA', 'QQQ', 'GLD', 'BTC-USD', 'CL=F']
    const data: { [key: string]: { price: number; change: number; changePercent: number } } = {}

    await Promise.all(tickers.map(async (ticker) => {
      try {
        const response = await fetch(`http://localhost:8001/api/v1/stocks/${ticker}/quote`)
        const quote = await response.json()
        data[ticker] = {
          price: quote.current_price,
          change: quote.change,
          changePercent: quote.change_percent
        }
      } catch (error) {
        console.error(`Failed to load ${ticker}:`, error)
      }
    }))

    setMarketData(data)
  }

  const loadPortfolioData = async () => {
    try {
      const portfoliosResponse = await portfolioApi.getAll()
      const allPortfolios = portfoliosResponse.data

      if (allPortfolios.length === 0) {
        return
      }

      const allHoldings = await Promise.all(
        allPortfolios.map(async (p) => {
          const detailResponse = await portfolioApi.getById(p.id)
          return detailResponse.data.holdings || []
        })
      )

      const flatHoldings = allHoldings.flat()

      const positions = await Promise.all(
        flatHoldings.map(async (holding) => {
          try {
            const priceResponse = await holdingApi.getWithPrice(holding.id)
            const data = priceResponse.data
            return {
              ticker: data.ticker,
              quantity: data.quantity,
              averagePrice: data.avg_price,
              currentPrice: data.current_price || data.avg_price,
              profit: data.profit_loss || 0,
              profitPercent: data.profit_loss_percent || 0
            }
          } catch (error) {
            return {
              ticker: holding.ticker,
              quantity: holding.quantity,
              averagePrice: holding.avg_price,
              currentPrice: holding.avg_price,
              profit: 0,
              profitPercent: 0
            }
          }
        })
      )

      const usdPositions = positions.filter(p => !isKoreanStock(p.ticker))
      const krwPositions = positions.filter(p => isKoreanStock(p.ticker))

      const usdValue = usdPositions.reduce((sum, p) => sum + (p.currentPrice * p.quantity), 0)
      const krwValue = krwPositions.reduce((sum, p) => sum + (p.currentPrice * p.quantity), 0)

      const usdCost = usdPositions.reduce((sum, p) => sum + (p.averagePrice * p.quantity), 0)
      const krwCost = krwPositions.reduce((sum, p) => sum + (p.averagePrice * p.quantity), 0)

      const usdProfit = usdValue - usdCost
      const krwProfit = krwValue - krwCost

      const totalValue = usdValue + krwValue
      const totalCost = usdCost + krwCost
      const totalProfit = totalValue - totalCost
      const totalProfitPercent = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0

      setPortfolio({
        positions: positions.sort((a, b) => (b.currentPrice * b.quantity) - (a.currentPrice * a.quantity)),
        totalValue,
        totalCost,
        totalProfit,
        totalProfitPercent,
        usdValue,
        krwValue,
        usdProfit,
        krwProfit
      })
    } catch (error) {
      console.error('Failed to load portfolio data:', error)
    }
  }

  // Get current date and day
  const today = new Date()
  const dateStr = today.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })

  // Determine market status based on time
  const getCurrentMarketStatus = () => {
    const hour = today.getHours()
    const day = today.getDay()

    // US market: Mon-Fri, 23:30-06:00 KST (9:30am-4:00pm ET)
    const isUSMarketOpen = day >= 1 && day <= 5 && (hour >= 23 || hour < 6)

    // Korean market: Mon-Fri, 9:00-15:30 KST
    const isKRMarketOpen = day >= 1 && day <= 5 && hour >= 9 && hour < 16

    return {
      us: isUSMarketOpen ? '개장' : '폐장',
      kr: isKRMarketOpen ? '개장' : '폐장'
    }
  }

  const marketStatus = getCurrentMarketStatus()

  // Top BUY recommendations sorted by confidence * expected change
  const topBuyRecommendations = predictions
    .filter(p => p.action === 'BUY' && p.confidence > 0.6)
    .sort((a, b) => {
      const scoreA = a.confidence * Math.abs(a.predicted_change_percent)
      const scoreB = b.confidence * Math.abs(b.predicted_change_percent)
      return scoreB - scoreA
    })
    .slice(0, 5)

  // Top SELL warnings
  const topSellWarnings = predictions
    .filter(p => p.action === 'SELL')
    .sort((a, b) => Math.abs(b.predicted_change_percent) - Math.abs(a.predicted_change_percent))
    .slice(0, 3)

  if (!mounted) return null

  return (
    <main className="min-h-screen bg-background">
      {/* Header - Daily Guide */}
      <header className="border-b bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-1">📊 오늘의 투자 가이드</h1>
              <p className="text-blue-100 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {dateStr}
              </p>
            </div>
            <div className="flex gap-4 text-sm">
              <div className="text-right">
                <div className="text-blue-100">미국장</div>
                <div className={`font-bold ${marketStatus.us === '개장' ? 'text-green-300' : 'text-gray-300'}`}>
                  {marketStatus.us}
                </div>
              </div>
              <div className="text-right">
                <div className="text-blue-100">한국장</div>
                <div className={`font-bold ${marketStatus.kr === '개장' ? 'text-green-300' : 'text-gray-300'}`}>
                  {marketStatus.kr}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 space-y-6">
        {/* Section 1: Top AI Recommendations (가장 중요) */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border-2 border-green-200 dark:border-green-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-green-900 dark:text-green-100 mb-1">
                💰 오늘의 AI 추천 매수 종목
              </h2>
              <p className="text-sm text-muted-foreground">신뢰도 × 예상수익률 기준 Top 5</p>
            </div>
            <button
              onClick={() => router.push('/prediction-map')}
              className="flex items-center gap-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold text-sm transition-colors"
            >
              전체보기 <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8 text-muted-foreground">로딩 중...</div>
          ) : topBuyRecommendations.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              현재 매수 추천 종목이 없습니다
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {topBuyRecommendations.map((pred, index) => (
                <button
                  key={`buy-${pred.ticker}`}
                  onClick={() => router.push(`/stocks/${pred.ticker}`)}
                  className="p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-green-300 dark:border-green-700 hover:shadow-lg transition-all text-left"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-green-600 text-white text-xs font-bold">
                          {index + 1}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-medium">
                          {isKoreanStock(pred.ticker) ? '🇰🇷 한국' : '🇺🇸 미국'}
                        </span>
                      </div>
                      <h3 className="font-bold text-lg mb-1">{getStockName(pred.ticker)}</h3>
                      <p className="text-xs text-muted-foreground font-mono">{pred.ticker}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3 mt-3 pt-3 border-t">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">예상 수익</p>
                      <p className="font-bold text-green-600 text-lg">
                        +{pred.predicted_change_percent.toFixed(2)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">AI 신뢰도</p>
                      <p className="font-bold text-blue-600 text-lg">
                        {(pred.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>

                  {/* Warren Buffett Investment Insight */}
                  <div className="mt-3 pt-3 border-t">
                    <BuffettInsight
                      ticker={pred.ticker}
                      prediction={pred}
                      compact={true}
                    />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Section 2: Sell Warnings */}
        {topSellWarnings.length > 0 && (
          <div className="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-950/20 dark:to-orange-950/20 border-2 border-red-200 dark:border-red-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <h2 className="text-2xl font-bold text-red-900 dark:text-red-100">
                ⚠️ 주의 필요 종목
              </h2>
            </div>
            <div className="space-y-3">
              {topSellWarnings.map((pred) => (
                <button
                  key={`sell-${pred.ticker}`}
                  onClick={() => router.push(`/stocks/${pred.ticker}`)}
                  className="w-full p-4 bg-white dark:bg-gray-800 rounded-lg border hover:shadow-md transition-all text-left flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs px-2 py-0.5 rounded bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 font-medium">
                        {isKoreanStock(pred.ticker) ? '🇰🇷 한국' : '🇺🇸 미국'}
                      </span>
                      <h3 className="font-bold">{getStockName(pred.ticker)}</h3>
                      <span className="text-xs text-muted-foreground">{pred.ticker}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      AI 예측: <span className="text-red-600 font-bold">{pred.predicted_change_percent.toFixed(2)}%</span> 하락 예상
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="px-3 py-1 rounded-lg text-sm font-bold bg-red-600 text-white">
                      매도 검토
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Section 3: Portfolio Quick View */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="border rounded-xl p-6 bg-card shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold mb-1">💼 내 포트폴리오</h2>
                <p className="text-sm text-muted-foreground">총 {portfolio.positions.length}개 종목</p>
              </div>
              <button
                onClick={() => router.push('/portfolio')}
                className="flex items-center gap-1 px-4 py-2 border rounded-lg hover:bg-accent transition-colors text-sm font-medium"
              >
                관리 <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            {portfolio.positions.length > 0 ? (
              <div>
                {/* Total Value */}
                <div className="mb-4 p-4 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-muted-foreground">총 자산</span>
                    <DollarSign className="w-5 h-5 text-blue-600" />
                  </div>
                  {portfolio.usdValue > 0 && (
                    <div className="mb-2">
                      <p className="text-2xl font-bold">
                        ${portfolio.usdValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </p>
                      <span className={`text-sm font-bold ${portfolio.usdProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {portfolio.usdProfit >= 0 && '+'}${portfolio.usdProfit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </span>
                    </div>
                  )}
                  {portfolio.krwValue > 0 && (
                    <div>
                      <p className="text-xl font-bold">
                        ₩{Math.round(portfolio.krwValue).toLocaleString()}
                      </p>
                      <span className={`text-sm font-bold ${portfolio.krwProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {portfolio.krwProfit >= 0 && '+'}₩{Math.round(portfolio.krwProfit).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>

                {/* Top Gainers/Losers */}
                <div>
                  <h3 className="text-sm font-semibold mb-2">주요 등락</h3>
                  <div className="space-y-2">
                    {portfolio.positions.slice(0, 3).map((position, index) => (
                      <button
                        key={`portfolio-pos-${index}-${position.ticker}`}
                        onClick={() => router.push(`/stocks/${position.ticker}`)}
                        className="w-full flex items-center justify-between p-2 bg-muted/30 rounded-lg border hover:bg-muted/50 transition-colors text-sm"
                      >
                        <span className="font-medium">{getStockName(position.ticker)}</span>
                        <span className={`font-bold ${position.profitPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.profitPercent >= 0 && '+'}{position.profitPercent.toFixed(2)}%
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p className="mb-2">포트폴리오가 비어있습니다</p>
                <button
                  onClick={() => router.push('/stocks-list')}
                  className="text-sm text-primary hover:underline"
                >
                  종목 검색하기 →
                </button>
              </div>
            )}
          </div>

          {/* Section 4: Validation Results */}
          <div className="border rounded-xl p-6 bg-card shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  AI 예측 정확도
                </h2>
                <p className="text-sm text-muted-foreground">최근 검증 결과</p>
              </div>
              <button
                onClick={() => router.push('/accuracy')}
                className="flex items-center gap-1 px-4 py-2 border rounded-lg hover:bg-accent transition-colors text-sm font-medium"
              >
                상세보기 <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30">
                  <div className="text-sm text-muted-foreground mb-1">학습된 AI 모델</div>
                  <div className="text-3xl font-bold text-green-600">{trainedCount}개</div>
                  <div className="text-xs text-muted-foreground mt-1">실시간 예측 가능</div>
                </div>

                {accuracyData && (
                  <div className="p-4 rounded-lg bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30">
                    <div className="text-sm text-muted-foreground mb-1">방향 정확도</div>
                    <div className="text-3xl font-bold text-blue-600">{accuracyData.direction_accuracy.toFixed(1)}%</div>
                    <div className="text-xs text-muted-foreground mt-1">{accuracyData.total_predictions}개 검증됨</div>
                  </div>
                )}
              </div>

              {accuracyData && (
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-muted/50">
                    <div className="text-xs text-muted-foreground mb-1">테스트된 모델</div>
                    <div className="text-xl font-bold">{accuracyData.tested_models}개</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/50">
                    <div className="text-xs text-muted-foreground mb-1">총 예측</div>
                    <div className="text-xl font-bold">{accuracyData.total_predictions}건</div>
                  </div>
                </div>
              )}

              {!accuracyData && (
                <div className="text-xs text-muted-foreground text-center p-4 bg-muted/30 rounded-lg">
                  검증된 예측 데이터가 아직 없습니다.<br />
                  예측 정확도 페이지에서 검증을 실행하세요.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Section 5: Market Indicators & Warren Buffett Guide */}
        <div className="border rounded-xl p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
          <div className="flex items-center gap-3 mb-6">
            <div className="text-3xl">📈</div>
            <div>
              <h2 className="text-xl font-bold">오늘의 투자 가이드</h2>
              <p className="text-sm text-muted-foreground">워렌 버핏의 투자 철학 기반</p>
            </div>
          </div>

          {/* Warren Buffett's Investment Philosophy */}
          <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 rounded-lg border border-amber-200 dark:border-amber-800">
            <div className="flex items-start gap-3">
              <div className="text-2xl">💎</div>
              <div>
                <p className="font-semibold text-amber-900 dark:text-amber-100 mb-2">
                  "가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것이다"
                </p>
                <p className="text-sm text-amber-800 dark:text-amber-200">
                  단기적 시장 변동성에 흔들리지 말고, 기업의 본질적 가치에 집중하세요.
                  훌륭한 기업을 합리적인 가격에 사는 것이 평범한 기업을 싼 가격에 사는 것보다 낫습니다.
                </p>
              </div>
            </div>
          </div>

          {/* Market Indicators */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="text-xl">🌍</span>
              주요 시장 지표
            </h3>

            {/* US Market Indices */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">S&P 500</p>
                    <p className="text-lg font-bold">
                      {marketData['SPY'] ? formatPrice(marketData['SPY'].price) : '...'}
                    </p>
                  </div>
                  <div className={`text-sm font-medium ${marketData['SPY']?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {marketData['SPY'] ? `${marketData['SPY'].changePercent >= 0 ? '+' : ''}${marketData['SPY'].changePercent.toFixed(2)}%` : '...'}
                  </div>
                </div>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">다우존스</p>
                    <p className="text-lg font-bold">
                      {marketData['DIA'] ? formatPrice(marketData['DIA'].price) : '...'}
                    </p>
                  </div>
                  <div className={`text-sm font-medium ${marketData['DIA']?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {marketData['DIA'] ? `${marketData['DIA'].changePercent >= 0 ? '+' : ''}${marketData['DIA'].changePercent.toFixed(2)}%` : '...'}
                  </div>
                </div>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">나스닥</p>
                    <p className="text-lg font-bold">
                      {marketData['QQQ'] ? formatPrice(marketData['QQQ'].price) : '...'}
                    </p>
                  </div>
                  <div className={`text-sm font-medium ${marketData['QQQ']?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {marketData['QQQ'] ? `${marketData['QQQ'].changePercent >= 0 ? '+' : ''}${marketData['QQQ'].changePercent.toFixed(2)}%` : '...'}
                  </div>
                </div>
              </div>
            </div>

            {/* Commodities & Crypto */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">금 (온스)</p>
                <p className="text-base font-bold">
                  {marketData['GLD'] ? `$${marketData['GLD'].price.toFixed(2)}` : '...'}
                </p>
                <p className={`text-xs ${marketData['GLD']?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {marketData['GLD'] ? `${marketData['GLD'].changePercent >= 0 ? '+' : ''}${marketData['GLD'].changePercent.toFixed(1)}%` : '...'}
                </p>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">비트코인</p>
                <p className="text-base font-bold">
                  {marketData['BTC-USD'] ? `$${Math.round(marketData['BTC-USD'].price).toLocaleString()}` : '...'}
                </p>
                <p className={`text-xs ${marketData['BTC-USD']?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {marketData['BTC-USD'] ? `${marketData['BTC-USD'].changePercent >= 0 ? '+' : ''}${marketData['BTC-USD'].changePercent.toFixed(1)}%` : '...'}
                </p>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">원유 (WTI)</p>
                <p className="text-base font-bold">
                  {marketData['CL=F'] ? `$${marketData['CL=F'].price.toFixed(2)}` : '...'}
                </p>
                <p className={`text-xs ${marketData['CL=F']?.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {marketData['CL=F'] ? `${marketData['CL=F'].changePercent >= 0 ? '+' : ''}${marketData['CL=F'].changePercent.toFixed(1)}%` : '...'}
                </p>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">원/달러</p>
                <p className="text-base font-bold">₩1,395</p>
                <p className="text-xs text-muted-foreground">참고값</p>
              </div>
            </div>

            {/* Additional Indicators */}
            <div className="grid grid-cols-2 md:grid-cols-2 gap-3">
              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">미국채 10년물</p>
                <p className="text-base font-bold">4.06%</p>
                <p className="text-xs text-muted-foreground">수익률</p>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">VIX (공포지수)</p>
                <p className="text-base font-bold">23.43</p>
                <p className="text-xs text-yellow-600">보통 수준</p>
              </div>
            </div>
          </div>

          {/* Investment Tips Based on Buffett Philosophy */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <span className="text-lg">📝</span>
              오늘의 투자 체크리스트
            </h3>

            {topBuyRecommendations.length > 0 && (
              <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                <div className="text-xl">✅</div>
                <div>
                  <p className="text-sm font-medium mb-1">AI가 {topBuyRecommendations.length}개 매수 추천 종목을 발견했습니다</p>
                  <p className="text-xs text-muted-foreground">
                    기업의 경쟁 우위와 재무 건전성을 확인하세요
                  </p>
                </div>
              </div>
            )}

            <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
              <div className="text-xl">🎯</div>
              <div>
                <p className="text-sm font-medium mb-1">장기 투자 관점 유지</p>
                <p className="text-xs text-muted-foreground">
                  "주식시장은 조급한 사람에게서 인내심 있는 사람에게로 돈을 이동시킵니다"
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
              <div className="text-xl">🛡️</div>
              <div>
                <p className="text-sm font-medium mb-1">안전 마진 확보</p>
                <p className="text-xs text-muted-foreground">
                  내재가치 대비 충분한 할인율이 있는 종목에 투자하세요
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
              <div className="text-xl">📚</div>
              <div>
                <p className="text-sm font-medium mb-1">분산 투자로 리스크 관리</p>
                <p className="text-xs text-muted-foreground">
                  여러 우량 기업에 분산하되, 이해하는 산업에만 투자하세요
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Warning */}
        <div className="p-4 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            ⚠️ <strong>투자 유의사항:</strong> 본 서비스는 투자 권유가 아닙니다. 모든 투자 결정은 본인의 책임 하에 신중히 하시기 바랍니다.
          </p>
        </div>
      </div>
    </main>
  )
}
