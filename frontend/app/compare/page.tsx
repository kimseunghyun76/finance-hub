'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { predictionApi } from '@/lib/api'
import { STOCK_NAMES } from '@/lib/stock-names'
import { formatElapsedTime } from '@/lib/utils'
import { ChevronRight, BarChart3, RefreshCw, X } from 'lucide-react'
import { LoadingProgress } from '@/components/loading-progress'

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
}

export default function ComparePage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [models, setModels] = useState<ModelDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTickers, setSelectedTickers] = useState<string[]>([])
  const [stockDetails, setStockDetails] = useState<Map<string, StockDetailData>>(new Map())
  const [detailLoading, setDetailLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'US' | 'KR'>('US')
  const [allPredictions, setAllPredictions] = useState<Map<string, any>>(new Map())
  const [sortOption, setSortOption] = useState<'confidence' | 'accuracy' | 'change' | 'name'>('confidence')

  useEffect(() => {
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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      handleStockClick(searchQuery.trim().toUpperCase())
    }
  }

  const handleStockClick = async (ticker: string) => {
    if (selectedTickers.includes(ticker)) {
      // Deselect
      setSelectedTickers(prev => prev.filter(t => t !== ticker))
    } else {
      // Select
      if (selectedTickers.length >= 5) {
        alert('최대 5개 종목까지만 선택할 수 있습니다.')
        return
      }

      setSelectedTickers(prev => [...prev, ticker])

      // Load stock detail if not already loaded
      if (!stockDetails.has(ticker)) {
        await loadStockDetail(ticker)
      }
    }
  }

  const loadStockDetail = async (ticker: string) => {
    setDetailLoading(true)

    try {
      const [predictionRes, infoRes, quoteRes] = await Promise.all([
        predictionApi.getPrediction(ticker).catch(() => ({ data: null })),
        fetch(`http://localhost:8001/api/v1/stocks/${ticker}/info`).catch(() => null),
        fetch(`http://localhost:8001/api/v1/stocks/${ticker}/quote`).catch(() => null)
      ])

      const info = infoRes ? await infoRes.json() : null
      const quote = quoteRes ? await quoteRes.json() : null

      setStockDetails(prev => {
        const newMap = new Map(prev)
        newMap.set(ticker, {
          prediction: predictionRes.data,
          info: info,
          quote: quote
        })
        return newMap
      })
    } catch (error) {
      console.error('Failed to load stock detail:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  const handleTrainModel = async (ticker: string, event: React.MouseEvent) => {
    event.stopPropagation()

    if (!confirm(`${ticker} 모델을 훈련하시겠습니까? 훈련은 백그라운드에서 실행되며 2-5분 소요됩니다.`)) {
      return
    }

    try {
      await predictionApi.trainModel(ticker)
      alert(`${ticker} 모델 훈련이 시작되었습니다. 백그라운드에서 실행 중입니다.`)
      setTimeout(() => loadModels(), 3000)
    } catch (error) {
      console.error('Failed to train model:', error)
      alert('모델 훈련 요청 실패')
    }
  }

  const sortStocks = (stocks: ModelDetail[]) => {
    return [...stocks].sort((a, b) => {
      const predA = allPredictions.get(a.ticker)
      const predB = allPredictions.get(b.ticker)

      const hasPredA = !!predA
      const hasPredB = !!predB
      if (hasPredA !== hasPredB) return hasPredA ? -1 : 1

      switch (sortOption) {
        case 'confidence':
          const confA = predA?.prediction?.confidence || predA?.confidence || 0
          const confB = predB?.prediction?.confidence || predB?.confidence || 0
          if (confB !== confA) return confB - confA
          break

        case 'accuracy':
          const accA = predA?.prediction?.confidence || predA?.confidence || 0
          const accB = predB?.prediction?.confidence || predB?.confidence || 0
          if (accB !== accA) return accB - accA
          break

        case 'change':
          const changeA = Math.abs(predA?.prediction?.change_percent || predA?.predicted_change_percent || 0)
          const changeB = Math.abs(predB?.prediction?.change_percent || predB?.predicted_change_percent || 0)
          if (changeB !== changeA) return changeB - changeA
          break

        case 'name':
          return a.name.localeCompare(b.name)
      }

      if (a.trained !== b.trained) return a.trained ? -1 : 1
      return a.ticker.localeCompare(b.ticker)
    })
  }

  const usStocks = sortStocks(models.filter((s) => s.market !== 'KRX'))
  const krStocks = sortStocks(models.filter((s) => s.market === 'KRX'))

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">⚖️ 종목 비교</h1>
          <p className="text-lg text-muted-foreground">
            최대 5개 종목을 선택하여 AI 예측을 비교하세요
            {selectedTickers.length > 0 && ` · ${selectedTickers.length}개 종목 선택됨`}
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
              <h3 className="text-lg font-semibold mb-1">선택된 종목</h3>
              <p className="text-sm text-muted-foreground">
                {selectedTickers.length === 0
                  ? '좌측에서 종목을 선택하세요 (최대 5개)'
                  : `${selectedTickers.length}개 종목 비교 중`}
              </p>
            </div>
            {selectedTickers.length > 0 && (
              <Button
                variant="outline"
                onClick={() => setSelectedTickers([])}
              >
                전체 선택 해제
              </Button>
            )}
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

                {/* Stock List Content */}
                <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                  {(activeTab === 'US' ? usStocks : krStocks).map((stock) => {
                    const prediction = allPredictions.get(stock.ticker)

                    return (
                      <div
                        key={stock.ticker}
                        className={`border-b last:border-b-0 ${
                          selectedTickers.includes(stock.ticker) ? 'bg-primary/10 border-l-4 border-l-primary' : ''
                        }`}
                      >
                        <button
                          onClick={() => handleStockClick(stock.ticker)}
                          className="w-full px-4 py-3 text-left hover:bg-accent transition-colors"
                        >
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-bold">{stock.name}</p>
                            <ChevronRight className={`w-4 h-4 transition-transform ${
                              selectedTickers.includes(stock.ticker) ? 'rotate-90' : ''
                            }`} />
                          </div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-muted-foreground font-mono">{stock.ticker}</span>
                            {stock.trained && (
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            )}
                          </div>

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
                            </div>
                          )}
                        </button>

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
              </div>
            </div>

            {/* Right Panel - Comparison Table */}
            <div className="lg:col-span-8 xl:col-span-9">
              {selectedTickers.length === 0 && (
                <div className="border rounded-lg p-12 text-center bg-muted/30">
                  <BarChart3 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg text-muted-foreground mb-2">
                    좌측에서 종목을 선택하면 비교 분석이 시작됩니다
                  </p>
                  <p className="text-sm text-muted-foreground">
                    💡 최대 5개 종목을 동시에 비교할 수 있습니다
                  </p>
                </div>
              )}

              {selectedTickers.length > 0 && detailLoading && (
                <LoadingProgress message="종목 정보를 불러오는 중..." estimatedSeconds={3} />
              )}

              {selectedTickers.length > 0 && !detailLoading && (
                <div className="space-y-6">
                  <div className="border rounded-lg p-6 bg-card">
                    <h2 className="text-2xl font-bold mb-4">⚖️ 종목 비교 ({selectedTickers.length}개)</h2>

                    {/* Selected Stock Chips */}
                    <div className="flex flex-wrap gap-2 mb-6">
                      {selectedTickers.map(ticker => (
                        <div
                          key={ticker}
                          className="flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full"
                        >
                          <span className="text-sm font-medium">{STOCK_NAMES[ticker]?.name || ticker}</span>
                          <button
                            onClick={() => handleStockClick(ticker)}
                            className="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>

                    {/* Comparison Table */}
                    <div className="border rounded-lg overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead className="bg-muted/50">
                            <tr>
                              <th className="px-4 py-3 text-left text-sm font-medium">항목</th>
                              {selectedTickers.map(ticker => {
                                return (
                                  <th key={ticker} className="px-4 py-3 text-center text-sm font-medium min-w-[150px]">
                                    <div className="flex flex-col items-center">
                                      <span className="font-bold">{STOCK_NAMES[ticker]?.name || ticker}</span>
                                      <span className="text-xs font-normal text-muted-foreground font-mono mt-1">
                                        {ticker}
                                      </span>
                                    </div>
                                  </th>
                                )
                              })}
                            </tr>
                          </thead>
                          <tbody className="divide-y">
                            {/* AI 추천 */}
                            <tr>
                              <td className="px-4 py-3 font-medium">AI 추천</td>
                              {selectedTickers.map(ticker => {
                                const stock = stockDetails.get(ticker)
                                return (
                                  <td key={ticker} className="px-4 py-3 text-center">
                                    {stock?.prediction ? (
                                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                                        stock.prediction.action === 'BUY' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                        stock.prediction.action === 'SELL' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                                        'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                                      }`}>
                                        {stock.prediction.action === 'BUY' && '💰 매수'}
                                        {stock.prediction.action === 'SELL' && '📉 매도'}
                                        {stock.prediction.action === 'HOLD' && '⏸️ 보유'}
                                      </span>
                                    ) : 'N/A'}
                                  </td>
                                )
                              })}
                            </tr>

                            {/* 예상 변동률 */}
                            <tr>
                              <td className="px-4 py-3 font-medium">예상 변동률</td>
                              {selectedTickers.map(ticker => {
                                const stock = stockDetails.get(ticker)
                                const changePercent = stock?.prediction?.prediction?.change_percent || 0
                                return (
                                  <td key={ticker} className="px-4 py-3 text-center">
                                    {stock?.prediction ? (
                                      <span className={`text-lg font-bold ${
                                        changePercent > 0 ? 'text-green-600' : 'text-red-600'
                                      }`}>
                                        {changePercent > 0 && '+'}
                                        {changePercent.toFixed(2)}%
                                      </span>
                                    ) : 'N/A'}
                                  </td>
                                )
                              })}
                            </tr>

                            {/* AI 확신도 */}
                            <tr>
                              <td className="px-4 py-3 font-medium">AI 확신도</td>
                              {selectedTickers.map(ticker => {
                                const stock = stockDetails.get(ticker)
                                const confidence = stock?.prediction?.prediction?.confidence || 0
                                return (
                                  <td key={ticker} className="px-4 py-3 text-center">
                                    {stock?.prediction ? (
                                      <div>
                                        <div className="text-sm font-semibold mb-1">
                                          {(confidence * 100).toFixed(1)}%
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                          <div
                                            className="bg-primary h-2 rounded-full"
                                            style={{ width: `${confidence * 100}%` }}
                                          />
                                        </div>
                                      </div>
                                    ) : 'N/A'}
                                  </td>
                                )
                              })}
                            </tr>

                            {/* 현재가 */}
                            <tr>
                              <td className="px-4 py-3 font-medium">현재가</td>
                              {selectedTickers.map(ticker => {
                                const stock = stockDetails.get(ticker)
                                return (
                                  <td key={ticker} className="px-4 py-3 text-center text-sm">
                                    {stock?.quote?.current_price
                                      ? (ticker.includes('.KS') || ticker.includes('.KQ')
                                          ? `₩${Math.round(stock.quote.current_price).toLocaleString()}`
                                          : `$${stock.quote.current_price.toFixed(2)}`)
                                      : 'N/A'}
                                  </td>
                                )
                              })}
                            </tr>

                            {/* 섹터 */}
                            <tr>
                              <td className="px-4 py-3 font-medium">섹터</td>
                              {selectedTickers.map(ticker => {
                                const stock = stockDetails.get(ticker)
                                return (
                                  <td key={ticker} className="px-4 py-3 text-center text-sm text-muted-foreground">
                                    {stock?.info?.sector || 'N/A'}
                                  </td>
                                )
                              })}
                            </tr>

                            {/* 시가총액 */}
                            <tr>
                              <td className="px-4 py-3 font-medium">시가총액</td>
                              {selectedTickers.map(ticker => {
                                const stock = stockDetails.get(ticker)
                                const marketCap = stock?.info?.market_cap
                                const formatted = marketCap
                                  ? marketCap >= 1e12 ? `$${(marketCap / 1e12).toFixed(1)}T`
                                  : marketCap >= 1e9 ? `$${(marketCap / 1e9).toFixed(1)}B`
                                  : `$${(marketCap / 1e6).toFixed(1)}M`
                                  : 'N/A'
                                return (
                                  <td key={ticker} className="px-4 py-3 text-center text-sm text-muted-foreground">
                                    {formatted}
                                  </td>
                                )
                              })}
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                      {selectedTickers.map(ticker => (
                        <button
                          key={ticker}
                          onClick={() => router.push(`/stocks/${ticker}`)}
                          className="p-3 border rounded-lg hover:border-primary hover:bg-accent transition-colors text-left"
                        >
                          <p className="font-semibold text-sm mb-1">{ticker}</p>
                          <p className="text-xs text-muted-foreground">상세 분석 →</p>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
