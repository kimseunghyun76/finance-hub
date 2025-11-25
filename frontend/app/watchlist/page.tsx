'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { watchlistManager, WatchlistItem } from '@/lib/watchlist'
import { predictionApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { LoadingProgress } from '@/components/loading-progress'
import { X, TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface WatchlistStockData extends WatchlistItem {
  prediction?: any
  info?: any
}

export default function WatchlistPage() {
  const router = useRouter()
  const [watchlist, setWatchlist] = useState<WatchlistStockData[]>([])
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    loadWatchlist()
  }, [])

  useEffect(() => {
    if (!mounted) return

    const handleUpdate = () => {
      loadWatchlist()
    }

    window.addEventListener('watchlist-updated', handleUpdate)
    return () => window.removeEventListener('watchlist-updated', handleUpdate)
  }, [mounted])

  const loadWatchlist = async () => {
    setLoading(true)
    const items = watchlistManager.getAll()

    // Load prediction and info data for each ticker
    const enrichedItems: WatchlistStockData[] = []

    for (const item of items) {
      try {
        const [predictionRes, infoRes] = await Promise.all([
          predictionApi.getPrediction(item.ticker).catch(() => null),
          fetch(`http://localhost:8001/api/v1/stocks/${item.ticker}/info`).catch(() => null)
        ])

        const prediction = predictionRes?.data || null
        const info = infoRes ? await infoRes.json() : null

        enrichedItems.push({
          ...item,
          prediction,
          info: info?.name ? info : null
        })
      } catch (error) {
        console.error(`Failed to load ${item.ticker}:`, error)
        enrichedItems.push(item)
      }
    }

    setWatchlist(enrichedItems)
    setLoading(false)
  }

  const removeFromWatchlist = (ticker: string) => {
    watchlistManager.remove(ticker)
    setWatchlist(prev => prev.filter(item => item.ticker !== ticker))
  }

  const clearWatchlist = () => {
    if (confirm('모든 관심 종목을 삭제하시겠습니까?')) {
      watchlistManager.clear()
      setWatchlist([])
    }
  }

  if (!mounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-950 dark:to-orange-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">⭐ 관심 종목</h1>
          <p className="text-lg text-muted-foreground">
            저장한 종목을 한눈에 확인하고 관리하세요
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <LoadingProgress message="관심 종목 데이터를 불러오는 중..." estimatedSeconds={watchlist.length * 2} />
        ) : watchlist.length === 0 ? (
          <div className="text-center py-12 border rounded-lg bg-muted/30">
            <div className="mb-6">
              <div className="text-6xl mb-4">⭐</div>
              <h3 className="text-xl font-semibold mb-2">관심 종목이 없습니다</h3>
              <p className="text-muted-foreground mb-6">
                종목 상세 페이지에서 ⭐ 버튼을 눌러 관심 종목에 추가해보세요
              </p>
              <Button onClick={() => router.push('/stocks-list')}>
                인기 종목 둘러보기
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* Stats */}
            <div className="mb-6 flex items-center justify-between">
              <div className="text-lg font-semibold">
                총 {watchlist.length}개 종목
              </div>
              <Button variant="outline" onClick={clearWatchlist} className="text-red-500 hover:text-red-700">
                전체 삭제
              </Button>
            </div>

            {/* Watchlist Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {watchlist.map((stock) => (
                <div
                  key={stock.ticker}
                  className="p-6 border rounded-lg bg-card hover:border-primary transition-colors relative"
                >
                  {/* Remove Button */}
                  <button
                    onClick={() => removeFromWatchlist(stock.ticker)}
                    className="absolute top-3 right-3 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>

                  {/* Header */}
                  <div className="mb-4">
                    <h3 className="text-xl font-bold mb-1">
                      {stock.name || stock.info?.name || stock.ticker}
                    </h3>
                    <p className="text-sm text-muted-foreground font-mono">
                      {stock.ticker}
                    </p>
                  </div>

                  {/* Prediction */}
                  {stock.prediction ? (
                    <div className="space-y-3 mb-4">
                      {/* Action */}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">AI 추천</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          stock.prediction.action === 'BUY' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          stock.prediction.action === 'SELL' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                        }`}>
                          {stock.prediction.action === 'BUY' && '💰 매수'}
                          {stock.prediction.action === 'SELL' && '📉 매도'}
                          {stock.prediction.action === 'HOLD' && '⏸️ 보유'}
                        </span>
                      </div>

                      {/* Expected Change */}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">예상 변동률</span>
                        <div className="flex items-center gap-1">
                          {stock.prediction.predicted_change_percent > 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-600" />
                          ) : stock.prediction.predicted_change_percent < 0 ? (
                            <TrendingDown className="w-4 h-4 text-red-600" />
                          ) : (
                            <Minus className="w-4 h-4 text-gray-600" />
                          )}
                          <span className={`font-bold ${
                            stock.prediction.predicted_change_percent > 0 ? 'text-green-600' :
                            stock.prediction.predicted_change_percent < 0 ? 'text-red-600' :
                            'text-gray-600'
                          }`}>
                            {stock.prediction.predicted_change_percent > 0 && '+'}
                            {stock.prediction.predicted_change_percent?.toFixed(2)}%
                          </span>
                        </div>
                      </div>

                      {/* Confidence */}
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">AI 확신도</span>
                          <span className="font-semibold">
                            {(stock.prediction.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${stock.prediction.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mb-4 p-3 bg-muted/50 rounded text-center text-sm text-muted-foreground">
                      AI 예측 데이터 없음
                    </div>
                  )}

                  {/* View Details Button */}
                  <Button
                    onClick={() => router.push(`/stocks/${stock.ticker}`)}
                    className="w-full"
                    variant="outline"
                  >
                    상세 보기
                  </Button>
                </div>
              ))}
            </div>

            {/* Comparison Link */}
            {watchlist.length >= 2 && (
              <div className="mt-8 p-6 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950">
                <h3 className="font-semibold mb-2">💡 Tip</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  관심 종목을 비교하여 최적의 투자 결정을 내려보세요
                </p>
                <Button
                  onClick={() => {
                    const tickers = watchlist.map(s => s.ticker).slice(0, 5).join(',')
                    router.push(`/compare?tickers=${tickers}`)
                  }}
                >
                  전체 비교하기
                </Button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
