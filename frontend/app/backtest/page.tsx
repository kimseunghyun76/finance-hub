'use client'

import { useState, useEffect } from 'react'
import { STOCK_NAMES } from '@/lib/stock-names'
import { formatElapsedTime } from '@/lib/utils'
import { predictionApi } from '@/lib/api'
import { TrendingUp, TrendingDown, ChevronRight, BarChart3, Trophy, AlertTriangle, Activity, Target, RefreshCw } from 'lucide-react'

interface ModelDetail {
  ticker: string
  name: string
  market: string
  trained: boolean
  lastTrained?: string | null
}

interface BacktestSummary {
  total_trades: number
  wins: number
  losses: number
  win_rate: number
  avg_return: number
  total_return: number
}

interface Trade {
  entry_date: string
  exit_date: string
  entry_price: number
  exit_price: number
  predicted_action: string
  actual_return: number
  profit: number
}

interface BacktestResult {
  ticker: string
  period: string
  summary: BacktestSummary
  best_trades: Trade[]
  worst_trades: Trade[]
  daily_trades?: Trade[]
}

export default function BacktestPage() {
  const [models, setModels] = useState<ModelDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)
  const [backtest, setBacktest] = useState<BacktestResult | null>(null)
  const [backtestLoading, setBacktestLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'US' | 'KR'>('US')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const [trainedResponse, detailsResponse] = await Promise.all([
        predictionApi.getTrainedModels(),
        predictionApi.getModelsDetails()
      ])

      const trainedTickers = trainedResponse.data.trained_models
      const modelsDetails = detailsResponse.data.models || []

      const lastTrainedMap = new Map(
        modelsDetails.map(m => [m.ticker, m.last_trained])
      )

      const allTickers = new Set([
        ...trainedTickers,
        ...Object.keys(STOCK_NAMES)
      ])

      const modelList: ModelDetail[] = Array.from(allTickers).map(ticker => {
        const stockInfo = STOCK_NAMES[ticker] || {
          name: ticker,
          market: ticker.includes('.KS') || ticker.includes('.KQ') ? 'KRX' : 'NASDAQ'
        }

        return {
          ticker,
          name: stockInfo.name,
          market: stockInfo.market,
          trained: trainedTickers.includes(ticker),
          lastTrained: lastTrainedMap.get(ticker) || null
        }
      })

      const uniqueModels = Array.from(
        new Map(modelList.map(item => [item.ticker, item])).values()
      )

      uniqueModels.sort((a, b) => {
        if (a.trained !== b.trained) return a.trained ? -1 : 1
        return a.ticker.localeCompare(b.ticker)
      })

      setModels(uniqueModels)
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStockClick = async (ticker: string) => {
    setSelectedTicker(ticker)
    await loadBacktest(ticker)
  }

  const loadBacktest = async (ticker: string) => {
    setBacktestLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/api/v1/predictions/${ticker}/backtest`)
      const data = await response.json()
      setBacktest(data)
    } catch (error) {
      console.error('Failed to load backtest:', error)
      setBacktest(null)
    } finally {
      setBacktestLoading(false)
    }
  }

  const usStocks = models.filter((s) => s.market !== 'KRX' && s.trained)
  const krStocks = models.filter((s) => s.market === 'KRX' && s.trained)

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">📊 백테스트 결과</h1>
          <p className="text-lg text-muted-foreground">
            AI 모델의 과거 예측 성능을 확인하세요
          </p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">로딩 중...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Sidebar - Stock List */}
            <div className="lg:col-span-4 xl:col-span-3">
              <div className="sticky top-4 border rounded-lg bg-card overflow-hidden" style={{ maxHeight: 'calc(100vh - 200px)' }}>
                {/* Tab Headers */}
                <div className="flex border-b">
                  <button
                    onClick={() => setActiveTab('US')}
                    className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                      activeTab === 'US'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted text-muted-foreground'
                    }`}
                  >
                    🇺🇸 미국 주식 ({usStocks.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('KR')}
                    className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                      activeTab === 'KR'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted text-muted-foreground'
                    }`}
                  >
                    🇰🇷 한국 주식 ({krStocks.length})
                  </button>
                </div>

                {/* Stock List Content - US Stocks */}
                {activeTab === 'US' && (
                  <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                    {usStocks.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground">
                        <p>학습된 미국 주식이 없습니다</p>
                      </div>
                    ) : (
                      usStocks.map((stock) => (
                        <div
                          key={stock.ticker}
                          className={`border-b last:border-b-0 ${
                            selectedTicker === stock.ticker ? 'bg-primary/10 border-l-4 border-l-primary' : ''
                          }`}
                        >
                          <button
                            onClick={() => handleStockClick(stock.ticker)}
                            className="w-full px-4 py-3 text-left hover:bg-accent transition-colors"
                          >
                            <div className="flex items-center justify-between mb-1">
                              <p className="font-bold">{stock.name}</p>
                              <ChevronRight className={`w-4 h-4 transition-transform ${
                                selectedTicker === stock.ticker ? 'rotate-90' : ''
                              }`} />
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-muted-foreground font-mono">{stock.ticker}</span>
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            </div>
                            {stock.lastTrained && (
                              <p className="text-xs text-muted-foreground mt-2">
                                🕐 {formatElapsedTime(stock.lastTrained)}
                              </p>
                            )}
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {/* Stock List Content - Korean Stocks */}
                {activeTab === 'KR' && (
                  <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                    {krStocks.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground">
                        <p>학습된 한국 주식이 없습니다</p>
                      </div>
                    ) : (
                      krStocks.map((stock) => (
                        <div
                          key={stock.ticker}
                          className={`border-b last:border-b-0 ${
                            selectedTicker === stock.ticker ? 'bg-primary/10 border-l-4 border-l-primary' : ''
                          }`}
                        >
                          <button
                            onClick={() => handleStockClick(stock.ticker)}
                            className="w-full px-4 py-3 text-left hover:bg-accent transition-colors"
                          >
                            <div className="flex items-center justify-between mb-1">
                              <p className="font-bold">{stock.name}</p>
                              <ChevronRight className={`w-4 h-4 transition-transform ${
                                selectedTicker === stock.ticker ? 'rotate-90' : ''
                              }`} />
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-muted-foreground font-mono">{stock.ticker}</span>
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            </div>
                            {stock.lastTrained && (
                              <p className="text-xs text-muted-foreground mt-2">
                                🕐 {formatElapsedTime(stock.lastTrained)}
                              </p>
                            )}
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel - Backtest Results */}
            <div className="lg:col-span-8 xl:col-span-9">
              {!selectedTicker && (
                <div className="border rounded-lg p-12 text-center bg-muted/30">
                  <BarChart3 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg text-muted-foreground mb-2">
                    좌측에서 종목을 선택하면 백테스트 결과가 표시됩니다
                  </p>
                  <p className="text-sm text-muted-foreground">
                    💡 AI 모델의 과거 예측 성능을 확인할 수 있습니다
                  </p>
                </div>
              )}

              {selectedTicker && backtestLoading && (
                <div className="border rounded-lg p-12 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-muted-foreground">백테스트 결과를 불러오는 중...</p>
                </div>
              )}

              {selectedTicker && !backtestLoading && backtest && (
                <div className="space-y-6">
                  {/* Header with Performance Grade */}
                  <div className="border rounded-lg p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h2 className="text-3xl font-bold mb-2">
                          {STOCK_NAMES[selectedTicker]?.name || selectedTicker}
                        </h2>
                        <p className="text-muted-foreground font-mono mb-3">{selectedTicker}</p>
                        <p className="text-sm text-muted-foreground">
                          📅 백테스트 기간: {backtest.period || '최근 1년'}
                        </p>
                      </div>
                      <div className="text-center">
                        <div className={`text-6xl font-bold mb-2 ${
                          backtest.summary.win_rate >= 60 ? 'text-green-600' :
                          backtest.summary.win_rate >= 50 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {backtest.summary.win_rate >= 60 ? 'A' :
                           backtest.summary.win_rate >= 50 ? 'B' : 'C'}
                        </div>
                        <p className="text-sm font-semibold text-muted-foreground">
                          {backtest.summary.win_rate >= 60 ? '우수' :
                           backtest.summary.win_rate >= 50 ? '보통' : '개선필요'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Performance Overview */}
                  <div className="border rounded-lg p-6 bg-card">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <Target className="w-5 h-5" />
                      성과 요약
                    </h3>

                    {/* Key Metrics with Better Explanations */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                      {/* Win Rate Section */}
                      <div className="p-5 border-2 rounded-lg bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <p className="text-sm text-muted-foreground mb-1">예측 정확도 (승률)</p>
                            <p className="text-xs text-muted-foreground">AI가 수익을 낸 거래 비율</p>
                          </div>
                          <div className={`text-4xl font-bold ${
                            backtest.summary.win_rate >= 60 ? 'text-green-600' :
                            backtest.summary.win_rate >= 50 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {backtest.summary.win_rate.toFixed(1)}%
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-green-600 font-semibold">✓ {backtest.summary.wins}승</span>
                          <span className="text-muted-foreground">•</span>
                          <span className="text-red-600 font-semibold">✗ {backtest.summary.losses}패</span>
                          <span className="text-muted-foreground">•</span>
                          <span className="text-muted-foreground">총 {backtest.summary.total_trades}회</span>
                        </div>
                        <div className="mt-3 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full ${
                              backtest.summary.win_rate >= 60 ? 'bg-green-600' :
                              backtest.summary.win_rate >= 50 ? 'bg-yellow-600' :
                              'bg-red-600'
                            }`}
                            style={{ width: `${backtest.summary.win_rate}%` }}
                          />
                        </div>
                      </div>

                      {/* Return Section */}
                      <div className="p-5 border-2 rounded-lg bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <p className="text-sm text-muted-foreground mb-1">누적 수익률</p>
                            <p className="text-xs text-muted-foreground">전체 기간 동안의 총 수익</p>
                          </div>
                          <div className={`text-4xl font-bold ${
                            backtest.summary.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {backtest.summary.total_return >= 0 && '+'}
                            {backtest.summary.total_return.toFixed(1)}%
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-sm mb-3">
                          <span className="text-muted-foreground">거래당 평균:</span>
                          <span className={`font-bold ${
                            backtest.summary.avg_return >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {backtest.summary.avg_return >= 0 && '+'}
                            {backtest.summary.avg_return.toFixed(2)}%
                          </span>
                        </div>
                        {backtest.summary.total_return >= 0 ? (
                          <div className="flex items-center gap-2 p-2 bg-green-100 dark:bg-green-900/30 rounded text-xs text-green-800 dark:text-green-200">
                            <TrendingUp className="w-4 h-4" />
                            <span>AI 모델이 수익을 창출했습니다</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 p-2 bg-red-100 dark:bg-red-900/30 rounded text-xs text-red-800 dark:text-red-200">
                            <TrendingDown className="w-4 h-4" />
                            <span>전략 개선이 필요합니다</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Detailed Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="p-3 bg-muted/30 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">총 거래</p>
                        <p className="text-xl font-bold">{backtest.summary.total_trades}회</p>
                      </div>
                      <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg text-center">
                        <p className="text-xs text-green-800 dark:text-green-200 mb-1">성공 거래</p>
                        <p className="text-xl font-bold text-green-600">{backtest.summary.wins}회</p>
                      </div>
                      <div className="p-3 bg-red-50 dark:bg-red-950/20 rounded-lg text-center">
                        <p className="text-xs text-red-800 dark:text-red-200 mb-1">실패 거래</p>
                        <p className="text-xl font-bold text-red-600">{backtest.summary.losses}회</p>
                      </div>
                      <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg text-center">
                        <p className="text-xs text-blue-800 dark:text-blue-200 mb-1">평균 수익</p>
                        <p className={`text-xl font-bold ${
                          backtest.summary.avg_return >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {backtest.summary.avg_return >= 0 && '+'}
                          {backtest.summary.avg_return.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Best Trades */}
                  <div className="border rounded-lg p-6 bg-card">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-yellow-500" />
                        최고 수익 거래 TOP 5
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        💡 가장 성공적이었던 예측들
                      </p>
                    </div>
                    {backtest.best_trades.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground">
                        <p className="text-sm">수익 거래 기록이 없습니다</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {backtest.best_trades.map((trade, idx) => (
                          <div
                            key={idx}
                            className="border-2 border-green-200 dark:border-green-800 rounded-lg p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-green-600 text-white font-bold">
                                  {idx + 1}
                                </div>
                                <div>
                                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                    trade.predicted_action === 'BUY'
                                      ? 'bg-green-600 text-white'
                                      : 'bg-red-600 text-white'
                                  }`}>
                                    {trade.predicted_action === 'BUY' ? '🎯 매수 예측' : '🎯 매도 예측'}
                                  </span>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="text-xs text-muted-foreground mb-1">수익률</p>
                                <p className="text-3xl font-bold text-green-600">
                                  +{trade.profit.toFixed(2)}%
                                </p>
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm pt-3 border-t border-green-200 dark:border-green-800">
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">📅 진입일</p>
                                <p className="font-semibold text-sm">{trade.entry_date}</p>
                                <p className="text-green-700 dark:text-green-400 font-mono mt-1">
                                  ${trade.entry_price.toFixed(2)}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">📅 청산일</p>
                                <p className="font-semibold text-sm">{trade.exit_date}</p>
                                <p className="text-green-700 dark:text-green-400 font-mono mt-1">
                                  ${trade.exit_price.toFixed(2)}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Worst Trades */}
                  <div className="border rounded-lg p-6 bg-card">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                        최대 손실 거래 TOP 5
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        💡 개선이 필요한 예측들
                      </p>
                    </div>
                    {backtest.worst_trades.length === 0 ? (
                      <div className="p-8 text-center text-muted-foreground">
                        <p className="text-sm">손실 거래 기록이 없습니다</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {backtest.worst_trades.map((trade, idx) => (
                          <div
                            key={idx}
                            className="border-2 border-red-200 dark:border-red-800 rounded-lg p-4 bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-950/20 dark:to-orange-950/20 hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-red-600 text-white font-bold">
                                  {idx + 1}
                                </div>
                                <div>
                                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                    trade.predicted_action === 'BUY'
                                      ? 'bg-green-600 text-white'
                                      : 'bg-red-600 text-white'
                                  }`}>
                                    {trade.predicted_action === 'BUY' ? '🎯 매수 예측' : '🎯 매도 예측'}
                                  </span>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="text-xs text-muted-foreground mb-1">손실률</p>
                                <p className="text-3xl font-bold text-red-600">
                                  {trade.profit.toFixed(2)}%
                                </p>
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm pt-3 border-t border-red-200 dark:border-red-800">
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">📅 진입일</p>
                                <p className="font-semibold text-sm">{trade.entry_date}</p>
                                <p className="text-red-700 dark:text-red-400 font-mono mt-1">
                                  ${trade.entry_price.toFixed(2)}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">📅 청산일</p>
                                <p className="font-semibold text-sm">{trade.exit_date}</p>
                                <p className="text-red-700 dark:text-red-400 font-mono mt-1">
                                  ${trade.exit_price.toFixed(2)}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {selectedTicker && !backtestLoading && !backtest && (
                <div className="border rounded-lg p-12 text-center bg-muted/30">
                  <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg text-muted-foreground">
                    백테스트 결과를 불러올 수 없습니다
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
