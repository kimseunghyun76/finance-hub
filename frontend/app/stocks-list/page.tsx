'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { predictionApi } from '@/lib/api'
import { watchlistManager } from '@/lib/watchlist'
import { STOCK_NAMES } from '@/lib/stock-names'
import { formatElapsedTime } from '@/lib/utils'
import { Star, TrendingUp, TrendingDown, DollarSign, Activity, Target, ChevronRight, BarChart3, Info, RefreshCw } from 'lucide-react'
import { LoadingProgress } from '@/components/loading-progress'
import { StockChart } from '@/components/stock-chart'
import { PredictionExplanation } from '@/components/prediction-explanation'
import { BuffettInsight } from '@/components/buffett-insight'

interface ModelDetail {
  ticker: string
  name: string
  market: string
  trained: boolean
  lastTrained?: string | null
}

interface StockDetailData {
  prediction: any
  info: any
  quote: any
  history: any
  analystTargets: any
}

export default function StocksListPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [models, setModels] = useState<ModelDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)
  const [stockDetail, setStockDetail] = useState<StockDetailData | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [isInWatchlist, setIsInWatchlist] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [chartPeriod, setChartPeriod] = useState<'1mo' | '3mo' | '6mo' | '1y' | '5y'>('3mo')
  const [activeTab, setActiveTab] = useState<'US' | 'KR'>('US')
  const [allPredictions, setAllPredictions] = useState<Map<string, any>>(new Map())
  const [sortOption, setSortOption] = useState<'confidence' | 'accuracy' | 'change' | 'name'>('confidence')

  useEffect(() => {
    setMounted(true)
    loadModels()
  }, [])

  // Pre-load predictions for all trained stocks
  useEffect(() => {
    const loadAllPredictions = async () => {
      const trainedTickers = models.filter(m => m.trained).map(m => m.ticker)
      if (trainedTickers.length === 0) return

      try {
        const predictionPromises = trainedTickers.map(ticker =>
          predictionApi.getPrediction(ticker)
            .then(res => ({ ticker, prediction: res.data }))
            .catch(() => ({ ticker, prediction: null }))
        )

        const results = await Promise.all(predictionPromises)
        const predictionsMap = new Map<string, any>()
        results.forEach(({ ticker, prediction }) => {
          if (prediction) {
            predictionsMap.set(ticker, prediction)
          }
        })

        setAllPredictions(predictionsMap)
      } catch (error) {
        console.error('Failed to load predictions:', error)
      }
    }

    if (models.length > 0) {
      loadAllPredictions()
    }
  }, [models])

  useEffect(() => {
    if (!mounted || !selectedTicker) return
    setIsInWatchlist(watchlistManager.has(selectedTicker))
  }, [selectedTicker, mounted])

  const loadModels = async () => {
    try {
      const [trainedResponse, detailsResponse] = await Promise.all([
        predictionApi.getTrainedModels(),
        predictionApi.getModelsDetails()
      ])

      const trainedTickers = trainedResponse.data.trained_models
      const modelsDetails = detailsResponse.data.models || []

      // Create a map of ticker -> last_trained
      const lastTrainedMap = new Map(
        modelsDetails.map(m => [m.ticker, m.last_trained])
      )

      // Create list combining trained models and popular stocks
      // Use Set to prevent duplicates
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

      // Remove any potential duplicates based on ticker (should not happen, but extra safety)
      const uniqueModels = Array.from(
        new Map(modelList.map(item => [item.ticker, item])).values()
      )

      // Sort: trained first, then alphabetically
      uniqueModels.sort((a, b) => {
        if (a.trained !== b.trained) return a.trained ? -1 : 1
        return a.ticker.localeCompare(b.ticker)
      })

      setModels(uniqueModels)

      // Don't auto-select any stock - let user choose
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      handleStockClick(searchQuery.trim().toUpperCase())
    }
  }

  const handleStockClick = async (ticker: string) => {
    console.log('handleStockClick called with ticker:', ticker)
    console.log('current selectedTicker:', selectedTicker)

    // Single selection mode
    if (selectedTicker === ticker) {
      // Deselect
      console.log('Deselecting ticker')
      setSelectedTicker(null)
      setStockDetail(null)
    } else {
      // Select
      console.log('Selecting ticker and loading detail')
      setSelectedTicker(ticker)
      await loadStockDetail(ticker)
    }
  }

  const loadStockDetail = async (ticker: string) => {
    console.log('loadStockDetail called for:', ticker)
    setDetailLoading(true)

    try {
      console.log('Fetching stock detail data...')
      const [predictionRes, infoRes, quoteRes, historyRes, analystRes] = await Promise.all([
        predictionApi.getPrediction(ticker).catch(() => ({ data: null })),
        fetch(`http://localhost:8001/api/v1/stocks/${ticker}/info`).catch(() => null),
        fetch(`http://localhost:8001/api/v1/stocks/${ticker}/quote`).catch(() => null),
        fetch(`http://localhost:8001/api/v1/stocks/${ticker}/history?period=1mo`).catch(() => null),
        fetch(`http://localhost:8001/api/v1/stocks/${ticker}/analyst-targets`).catch(() => null)
      ])

      const info = infoRes && infoRes.ok ? await infoRes.json().catch(() => null) : null
      const quote = quoteRes && quoteRes.ok ? await quoteRes.json().catch(() => null) : null
      const history = historyRes && historyRes.ok ? await historyRes.json().catch(() => null) : null
      const analystTargets = analystRes && analystRes.ok ? await analystRes.json().catch(() => null) : null

      // Get current price and volume from chart data (last value)
      let currentPrice = quote?.current_price
      let volume = quote?.volume

      if (history?.data?.length > 0) {
        const lastData = history.data[history.data.length - 1]
        currentPrice = lastData.close || currentPrice
        volume = lastData.volume || volume
      }

      const detailData = {
        prediction: predictionRes.data,
        info: info,
        quote: {
          ...quote,
          current_price: currentPrice,
          volume: volume
        },
        history: history?.data,
        analystTargets: analystTargets
      }

      console.log('Stock detail data loaded:', detailData)
      setStockDetail(detailData)
      console.log('Stock detail state updated')
    } catch (error) {
      console.error('Failed to load stock detail:', error)
    } finally {
      console.log('Setting detail loading to false')
      setDetailLoading(false)
    }
  }

  const toggleWatchlist = (ticker: string) => {
    const inWatchlist = watchlistManager.has(ticker)

    if (inWatchlist) {
      watchlistManager.remove(ticker)
    } else {
      const stockInfo = STOCK_NAMES[ticker]
      watchlistManager.add(ticker, stockInfo?.name || ticker)
    }

    setIsInWatchlist(!inWatchlist)
  }

  const handleTrainModel = async (ticker: string, event: React.MouseEvent) => {
    event.stopPropagation() // Prevent stock selection

    if (!confirm(`${ticker} 모델을 훈련하시겠습니까? 훈련은 백그라운드에서 실행되며 2-5분 소요됩니다.`)) {
      return
    }

    try {
      await predictionApi.trainModel(ticker)
      alert(`${ticker} 모델 훈련이 시작되었습니다. 백그라운드에서 실행 중입니다.`)

      // Reload models after a few seconds to show training started
      setTimeout(() => loadModels(), 3000)
    } catch (error) {
      console.error('Failed to train model:', error)
      alert('모델 훈련 요청 실패')
    }
  }

  // Calculate Buffett rating score for sorting
  const getBuffettScore = (prediction: any): number => {
    if (!prediction) return -1

    const confidence = prediction.prediction?.confidence || prediction.confidence || 0
    const changePercent = prediction.prediction?.change_percent || prediction.predicted_change_percent || 0

    if (prediction.action === 'BUY' && confidence > 0.7 && changePercent > 3) {
      return 100 // Highest priority: Strong Buy
    } else if (prediction.action === 'BUY' && (confidence > 0.6 || changePercent > 2)) {
      return 80 // High priority: Buy
    } else if (prediction.action === 'SELL' || changePercent < -3) {
      return 40 // Medium priority: Sell
    } else if (Math.abs(changePercent) < 2) {
      return 60 // Medium priority: Hold
    }
    return 50 // Low priority: Caution
  }

  // Sort stocks based on selected option
  const sortStocks = (stocks: ModelDetail[]) => {
    return [...stocks].sort((a, b) => {
      const predA = allPredictions.get(a.ticker)
      const predB = allPredictions.get(b.ticker)

      // Stocks without predictions go to the bottom
      const hasPredA = !!predA
      const hasPredB = !!predB
      if (hasPredA !== hasPredB) return hasPredA ? -1 : 1

      // Warren Buffett recommendation score (default sort)
      const buffettScoreA = getBuffettScore(predA)
      const buffettScoreB = getBuffettScore(predB)

      // Always prioritize by Buffett score first for stocks with predictions
      if (hasPredA && hasPredB && buffettScoreB !== buffettScoreA) {
        return buffettScoreB - buffettScoreA
      }

      switch (sortOption) {
        case 'confidence':
          // Sort by confidence (high to low)
          const confA = predA?.prediction?.confidence || predA?.confidence || 0
          const confB = predB?.prediction?.confidence || predB?.confidence || 0
          if (confB !== confA) return confB - confA
          break

        case 'accuracy':
          // Sort by model accuracy/confidence score (using confidence as proxy)
          // In a real implementation, this would use historical accuracy data
          const accA = predA?.prediction?.confidence || predA?.confidence || 0
          const accB = predB?.prediction?.confidence || predB?.confidence || 0
          if (accB !== accA) return accB - accA
          break

        case 'change':
          // Sort by absolute change percent (high to low)
          const changeA = Math.abs(predA?.prediction?.change_percent || predA?.predicted_change_percent || 0)
          const changeB = Math.abs(predB?.prediction?.change_percent || predB?.predicted_change_percent || 0)
          if (changeB !== changeA) return changeB - changeA
          break

        case 'name':
          // Sort alphabetically by name
          return a.name.localeCompare(b.name)
      }

      // Secondary sort: trained first, then alphabetically
      if (a.trained !== b.trained) return a.trained ? -1 : 1
      return a.ticker.localeCompare(b.ticker)
    })
  }

  const usStocks = sortStocks(models.filter((s) => s.market !== 'KRX'))
  const krStocks = sortStocks(models.filter((s) => s.market === 'KRX'))

  // Count trained models
  const trainedCount = models.filter(m => m.trained).length

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">📋 인기 종목 목록</h1>
          <p className="text-lg text-muted-foreground">
            자주 조회되는 종목을 빠르게 확인하세요
          </p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="종목 코드 입력 (예: AAPL, 005930.KS)"
              className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <Button type="submit" className="px-6">
              검색
            </Button>
          </form>
        </div>

        {/* Stats */}
        <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 rounded-lg border">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-1">AI 학습 완료 종목</h3>
              <p className="text-sm text-muted-foreground">
                총 {trainedCount}개 종목에서 AI 예측이 가능합니다
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-primary">
                {trainedCount}
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
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
                    🇺🇸 미국 주식 ({usStocks.filter(s => s.trained).length}/{usStocks.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('KR')}
                    className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${
                      activeTab === 'KR'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted text-muted-foreground'
                    }`}
                  >
                    🇰🇷 한국 주식 ({krStocks.filter(s => s.trained).length}/{krStocks.length})
                  </button>
                </div>

                {/* Sort Dropdown */}
                <div className="px-3 py-2 border-b bg-muted/30">
                  <select
                    value={sortOption}
                    onChange={(e) => setSortOption(e.target.value as 'confidence' | 'accuracy' | 'change' | 'name')}
                    className="w-full px-3 py-2 text-sm rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="confidence">확신도 높은순</option>
                    <option value="accuracy">예측 정확도 높은순</option>
                    <option value="change">변동률 높은순</option>
                    <option value="name">이름순</option>
                  </select>
                </div>

                {/* Stock List Content - US Stocks */}
                {activeTab === 'US' && (
                  <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                    {usStocks.map((stock) => {
                      // Use pre-loaded predictions from allPredictions map
                      const prediction = allPredictions.get(stock.ticker)

                      return (
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
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs text-muted-foreground font-mono">{stock.ticker}</span>
                              {stock.trained && (
                                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              )}
                            </div>

                            {/* Training Time & AI Opinion - Always visible for trained stocks */}
                            {stock.trained && (
                              <div className="space-y-2 mt-2">
                                <div className="flex items-center justify-between gap-2">
                                  <span className="text-xs text-muted-foreground">
                                    🕐 {formatElapsedTime(stock.lastTrained)}
                                  </span>
                                  {prediction && (
                                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                                      prediction.action === 'BUY' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200' :
                                      prediction.action === 'SELL' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200' :
                                      'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200'
                                    }`}>
                                      {prediction.action === 'BUY' && '💰 매수'}
                                      {prediction.action === 'SELL' && '📉 매도'}
                                      {prediction.action === 'HOLD' && '⏸️ 보유'}
                                    </span>
                                  )}
                                </div>
                                {prediction && (
                                  <div className="flex items-center justify-between gap-2">
                                    <span className="text-xs text-muted-foreground">
                                      변동률: <span className={`font-semibold ${
                                        prediction.prediction?.change_percent > 0 ? 'text-green-600' : 'text-red-600'
                                      }`}>
                                        {prediction.prediction?.change_percent > 0 && '+'}
                                        {(prediction.prediction?.change_percent || 0).toFixed(2)}%
                                      </span>
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                      확신도: <span className="font-semibold text-primary">
                                        {((prediction.prediction?.confidence || 0) * 100).toFixed(0)}%
                                      </span>
                                    </span>
                                  </div>
                                )}
                                {/* Warren Buffett Investment Insight - Compact */}
                                {prediction && (
                                  <div className="mt-2">
                                    <BuffettInsight
                                      ticker={stock.ticker}
                                      prediction={prediction}
                                      compact={true}
                                    />
                                  </div>
                                )}
                              </div>
                            )}
                          </button>

                          {/* Train Button */}
                          <div className="px-4 pb-2">
                            <button
                              onClick={(e) => handleTrainModel(stock.ticker, e)}
                              className="text-xs px-3 py-1 rounded bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 transition-colors flex items-center gap-1"
                            >
                              <RefreshCw className="w-3 h-3" />
                              {stock.trained ? '재훈련' : '훈련'}
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}

                {/* Stock List Content - Korean Stocks */}
                {activeTab === 'KR' && (
                  <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                    {krStocks.map((stock) => {
                      // Use pre-loaded predictions from allPredictions map
                      const prediction = allPredictions.get(stock.ticker)

                      return (
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
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs text-muted-foreground font-mono">{stock.ticker}</span>
                              {stock.trained && (
                                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              )}
                            </div>

                            {/* Training Time & AI Opinion - Always visible for trained stocks */}
                            {stock.trained && (
                              <div className="space-y-2 mt-2">
                                <div className="flex items-center justify-between gap-2">
                                  <span className="text-xs text-muted-foreground">
                                    🕐 {formatElapsedTime(stock.lastTrained)}
                                  </span>
                                  {prediction && (
                                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                                      prediction.action === 'BUY' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200' :
                                      prediction.action === 'SELL' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200' :
                                      'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200'
                                    }`}>
                                      {prediction.action === 'BUY' && '💰 매수'}
                                      {prediction.action === 'SELL' && '📉 매도'}
                                      {prediction.action === 'HOLD' && '⏸️ 보유'}
                                    </span>
                                  )}
                                </div>
                                {prediction && (
                                  <div className="flex items-center justify-between gap-2">
                                    <span className="text-xs text-muted-foreground">
                                      변동률: <span className={`font-semibold ${
                                        prediction.prediction?.change_percent > 0 ? 'text-green-600' : 'text-red-600'
                                      }`}>
                                        {prediction.prediction?.change_percent > 0 && '+'}
                                        {(prediction.prediction?.change_percent || 0).toFixed(2)}%
                                      </span>
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                      확신도: <span className="font-semibold text-primary">
                                        {((prediction.prediction?.confidence || 0) * 100).toFixed(0)}%
                                      </span>
                                    </span>
                                  </div>
                                )}
                                {/* Warren Buffett Investment Insight - Compact */}
                                {prediction && (
                                  <div className="mt-2">
                                    <BuffettInsight
                                      ticker={stock.ticker}
                                      prediction={prediction}
                                      compact={true}
                                    />
                                  </div>
                                )}
                              </div>
                            )}
                          </button>

                          {/* Train Button */}
                          <div className="px-4 pb-2">
                            <button
                              onClick={(e) => handleTrainModel(stock.ticker, e)}
                              className="text-xs px-3 py-1 rounded bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 transition-colors flex items-center gap-1"
                            >
                              <RefreshCw className="w-3 h-3" />
                              {stock.trained ? '재훈련' : '훈련'}
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel - Stock Detail */}
            <div className="lg:col-span-8 xl:col-span-9">
              {!selectedTicker && (
                <div className="border rounded-lg p-12 text-center bg-muted/30">
                  <BarChart3 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg text-muted-foreground mb-2">
                    좌측에서 종목을 선택하면 상세 정보가 표시됩니다
                  </p>
                </div>
              )}

              {selectedTicker && detailLoading && (
                <LoadingProgress message="종목 상세 정보를 불러오는 중..." estimatedSeconds={3} />
              )}

              {/* Single Stock View */}
              {selectedTicker && !detailLoading && stockDetail && (
                <div className="space-y-6">
                  {/* Stock Header */}
                  <header className="border-b bg-card border rounded-lg">
                    <div className="px-6 py-4">
                      <button
                        onClick={() => router.push('/stocks-list')}
                        className="text-sm text-muted-foreground hover:text-foreground mb-2"
                      >
                        ← 목록으로
                      </button>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-3xl font-bold">
                              {STOCK_NAMES[selectedTicker]?.name || selectedTicker}
                            </h1>
                            <button
                              onClick={() => toggleWatchlist(selectedTicker)}
                              className={`p-2 rounded-lg transition-colors ${
                                isInWatchlist
                                  ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-200'
                                  : 'bg-muted hover:bg-muted/80'
                              }`}
                            >
                              <Star className={`w-5 h-5 ${isInWatchlist ? 'fill-current' : ''}`} />
                            </button>
                          </div>
                          <p className="text-muted-foreground">
                            {selectedTicker} · {stockDetail.info?.sector || 'N/A'}
                          </p>
                        </div>
                        <div className="text-right">
                          {stockDetail.quote?.current_price ? (
                            <>
                              <p className="text-3xl font-bold">
                                {selectedTicker.includes('.KS') || selectedTicker.includes('.KQ')
                                  ? `₩${Math.round(stockDetail.quote.current_price).toLocaleString()}`
                                  : `$${(stockDetail.quote.current_price || 0).toFixed(2)}`}
                              </p>
                              {stockDetail.quote?.change !== undefined && (
                                <p className={`text-lg font-medium mt-1 ${
                                  stockDetail.quote.change >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {stockDetail.quote.change >= 0 && '+'}
                                  {selectedTicker.includes('.KS') || selectedTicker.includes('.KQ')
                                    ? `₩${Math.round(stockDetail.quote.change).toLocaleString()}`
                                    : `$${(stockDetail.quote.change || 0).toFixed(2)}`}
                                  {' '}({(stockDetail.quote.change_percent || 0).toFixed(2)}%)
                                </p>
                              )}
                            </>
                          ) : (
                            <p className="text-sm text-muted-foreground italic">데이터 로딩 중...</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </header>

                  {/* Info Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="p-4 border rounded-lg bg-card">
                      <h3 className="text-sm font-medium text-muted-foreground">시가총액</h3>
                      <p className="text-xl font-bold mt-2">
                        {stockDetail.info?.market_cap
                          ? (stockDetail.info.market_cap >= 1e12
                              ? `$${((stockDetail.info.market_cap || 0) / 1e12).toFixed(1)}T`
                              : stockDetail.info.market_cap >= 1e9
                              ? `$${((stockDetail.info.market_cap || 0) / 1e9).toFixed(1)}B`
                              : `$${((stockDetail.info.market_cap || 0) / 1e6).toFixed(1)}M`)
                          : 'N/A'}
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg bg-card">
                      <h3 className="text-sm font-medium text-muted-foreground">산업</h3>
                      <p className="text-xl font-bold mt-2">{stockDetail.info?.industry || 'N/A'}</p>
                    </div>

                    <div className="p-4 border rounded-lg bg-card">
                      <h3 className="text-sm font-medium text-muted-foreground">거래량</h3>
                      <p className="text-xl font-bold mt-2">
                        {stockDetail.quote?.volume
                          ? ((stockDetail.quote.volume || 0) >= 1e9
                              ? `${((stockDetail.quote.volume || 0) / 1e9).toFixed(1)}B`
                              : (stockDetail.quote.volume || 0) >= 1e6
                              ? `${((stockDetail.quote.volume || 0) / 1e6).toFixed(1)}M`
                              : (stockDetail.quote.volume || 0).toLocaleString())
                          : 'N/A'}
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg bg-card">
                      <h3 className="text-sm font-medium text-muted-foreground">통화</h3>
                      <p className="text-xl font-bold mt-2">
                        {selectedTicker.includes('.KS') || selectedTicker.includes('.KQ') ? 'KRW' : 'USD'}
                      </p>
                    </div>
                  </div>

                  {/* Price Chart */}
                  <div className="border rounded-lg p-6 bg-card">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-bold flex items-center gap-2">
                        <BarChart3 className="w-5 h-5" />
                        주가 차트
                      </h2>
                      <div className="flex gap-2">
                        {(['1mo', '3mo', '6mo', '1y', '5y'] as const).map((p) => (
                          <button
                            key={p}
                            onClick={() => setChartPeriod(p)}
                            className={`px-3 py-1 text-sm rounded-md transition-colors ${
                              chartPeriod === p
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                            }`}
                          >
                            {p === '1mo' ? '1개월' : p === '3mo' ? '3개월' : p === '6mo' ? '6개월' : p === '1y' ? '1년' : '5년'}
                          </button>
                        ))}
                      </div>
                    </div>

                    <StockChart
                      ticker={selectedTicker}
                      period={chartPeriod}
                      currency={selectedTicker.includes('.KS') || selectedTicker.includes('.KQ') ? 'KRW' : 'USD'}
                    />
                  </div>

                  {/* AI Prediction */}
                  {stockDetail.prediction && (
                    <div className="border rounded-lg p-6 bg-card">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        AI 예측 분석
                      </h3>

                      {/* AI Recommendation */}
                      <div className="mb-6">
                        <div className="flex items-center gap-4 mb-4">
                          <span className={`px-6 py-3 rounded-lg text-lg font-bold ${
                            stockDetail.prediction.action === 'BUY'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : stockDetail.prediction.action === 'SELL'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                          }`}>
                            {stockDetail.prediction.action === 'BUY' && '💰 매수'}
                            {stockDetail.prediction.action === 'SELL' && '📉 매도'}
                            {stockDetail.prediction.action === 'HOLD' && '⏸️ 보유'}
                          </span>
                          <div>
                            <p className="text-sm text-muted-foreground">예상 변동률</p>
                            <p className={`text-2xl font-bold ${
                              (stockDetail.prediction.prediction?.change_percent || 0) > 0
                                ? 'text-green-600'
                                : 'text-red-600'
                            }`}>
                              {(stockDetail.prediction.prediction?.change_percent || 0) > 0 && '+'}
                              {(stockDetail.prediction.prediction?.change_percent || 0).toFixed(2)}%
                            </p>
                          </div>
                        </div>

                        {/* Confidence Bar */}
                        <div>
                          <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                            <span>AI 확신도</span>
                            <span className="font-bold">
                              {((stockDetail.prediction.prediction?.confidence || 0) * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                              className="bg-primary h-3 rounded-full transition-all"
                              style={{ width: `${(stockDetail.prediction.prediction?.confidence || 0) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Analyst Target Prices */}
                      {stockDetail.analystTargets && stockDetail.analystTargets.target_high && (
                        <div className="grid grid-cols-2 gap-4 mb-6">
                          <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
                            <div className="flex items-center gap-2 mb-2">
                              <TrendingUp className="w-4 h-4 text-green-600" />
                              <p className="text-sm text-green-800 dark:text-green-200">목표 상단가</p>
                            </div>
                            <p className="text-2xl font-bold text-green-600">
                              {selectedTicker.includes('.KS') || selectedTicker.includes('.KQ')
                                ? `₩${Math.round(stockDetail.analystTargets.target_high || 0).toLocaleString()}`
                                : `$${(stockDetail.analystTargets.target_high || 0).toFixed(2)}`
                              }
                            </p>
                            <p className="text-xs text-green-700 mt-1">애널리스트 컨센서스</p>
                          </div>
                          <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <div className="flex items-center gap-2 mb-2">
                              <Target className="w-4 h-4 text-blue-600" />
                              <p className="text-sm text-blue-800 dark:text-blue-200">평균 목표가</p>
                            </div>
                            <p className="text-2xl font-bold text-blue-600">
                              {selectedTicker.includes('.KS') || selectedTicker.includes('.KQ')
                                ? `₩${Math.round(stockDetail.analystTargets.target_mean || 0).toLocaleString()}`
                                : `$${(stockDetail.analystTargets.target_mean || 0).toFixed(2)}`
                              }
                            </p>
                            <p className="text-xs text-blue-700 mt-1">{stockDetail.analystTargets.number_of_analysts || 0}명 분석</p>
                          </div>
                        </div>
                      )}

                      {/* Detailed Prediction Explanation */}
                      <div className="border-t pt-6">
                        <PredictionExplanation
                          prediction={stockDetail.prediction}
                          currentPrice={stockDetail.quote?.current_price || 0}
                          currency={selectedTicker.includes('.KS') || selectedTicker.includes('.KQ') ? 'KRW' : 'USD'}
                          ticker={selectedTicker}
                          onRefresh={() => loadStockDetail(selectedTicker)}
                        />
                      </div>
                    </div>
                  )}

                  {/* Warren Buffett Investment Insight */}
                  {stockDetail.prediction && (
                    <BuffettInsight
                      ticker={selectedTicker}
                      prediction={stockDetail.prediction}
                      stockInfo={stockDetail.info}
                    />
                  )}

                  {/* Company Info */}
                  {stockDetail.info && (
                    <div className="border rounded-lg p-6 bg-card">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <Info className="w-5 h-5" />
                        기업 정보
                      </h3>
                      <div className="space-y-3">
                        {stockDetail.info.sector && (
                          <div className="flex items-center justify-between py-2 border-b">
                            <span className="text-muted-foreground">섹터</span>
                            <span className="font-semibold">{stockDetail.info.sector}</span>
                          </div>
                        )}
                        {stockDetail.info.industry && (
                          <div className="flex items-center justify-between py-2 border-b">
                            <span className="text-muted-foreground">산업</span>
                            <span className="font-semibold">{stockDetail.info.industry}</span>
                          </div>
                        )}
                        {stockDetail.info.website && (
                          <div className="flex items-center justify-between py-2">
                            <span className="text-muted-foreground">웹사이트</span>
                            <a
                              href={stockDetail.info.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary hover:underline"
                            >
                              방문하기 →
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Comparison feature has been moved to /compare page */}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
