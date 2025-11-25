'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { stockApi, type StockInfo, type StockQuote, type StockPrediction } from '@/lib/api'
import { StockChart } from '@/components/stock-chart'
import { PredictionExplanation } from '@/components/prediction-explanation'
import { WatchlistToggle } from '@/components/watchlist-toggle'
import { InvestmentInsights } from '@/components/investment-insights'
import { formatCurrency, formatPercent, formatLargeNumber } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

export default function StockDetailPage() {
  const params = useParams()
  const router = useRouter()
  const ticker = params.ticker as string

  const [info, setInfo] = useState<StockInfo | null>(null)
  const [quote, setQuote] = useState<StockQuote | null>(null)
  const [prediction, setPrediction] = useState<StockPrediction | null>(null)
  const [period, setPeriod] = useState<'1mo' | '3mo' | '6mo' | '1y' | '5y'>('3mo')
  const [loading, setLoading] = useState(true)
  const [predictionLoading, setPredictionLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isKorean = ticker.includes('.KS') || ticker.includes('.KQ')
  const currency = isKorean ? 'KRW' : 'USD'

  useEffect(() => {
    loadStockData()
    loadPrediction()
  }, [ticker])

  const loadStockData = async () => {
    setLoading(true)
    setError(null)

    try {
      const [infoRes, quoteRes] = await Promise.all([
        stockApi.getInfo(ticker),
        stockApi.getQuote(ticker),
      ])

      setInfo(infoRes.data)
      setQuote(quoteRes.data)
    } catch (err) {
      setError('주식 정보를 불러올 수 없습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadPrediction = async () => {
    setPredictionLoading(true)
    try {
      const res = await stockApi.getPrediction(ticker)
      setPrediction(res.data)
    } catch (err) {
      console.error('Prediction error:', err)
      // Don't show error to user, just don't display prediction
      setPrediction(null)
    } finally {
      setPredictionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <Skeleton className="h-4 w-24 mb-2" />
            <Skeleton className="h-9 w-48 mb-2" />
            <Skeleton className="h-5 w-32" />
            <div className="flex justify-end mt-4">
              <div className="text-right">
                <Skeleton className="h-9 w-32 mb-2" />
                <Skeleton className="h-6 w-24" />
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          {/* Info Cards Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="p-4 border rounded-lg bg-card">
                <Skeleton className="h-4 w-16 mb-2" />
                <Skeleton className="h-6 w-24" />
              </div>
            ))}
          </div>

          {/* Chart Skeleton */}
          <div className="border rounded-lg p-6 bg-card mb-8">
            <div className="flex items-center justify-between mb-6">
              <Skeleton className="h-6 w-24" />
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-8 w-16" />
                ))}
              </div>
            </div>
            <Skeleton className="h-80 w-full" />
          </div>

          {/* Prediction Skeleton */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="flex items-center justify-between mb-4">
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-8 w-20" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-8 w-32" />
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error || !info || !quote) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-destructive">{error || '주식을 찾을 수 없습니다.'}</p>
          <Button onClick={() => router.push('/dashboard')} className="mt-4">
            대시보드로 돌아가기
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => router.back()}
            className="text-sm text-muted-foreground hover:text-foreground mb-2"
          >
            ← 뒤로 가기
          </button>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{info.name}</h1>
                <WatchlistToggle ticker={ticker} name={info.name} variant="icon" />
              </div>
              <p className="text-muted-foreground">
                {ticker} · {info.sector || 'N/A'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold">
                {formatCurrency(quote.current_price, currency)}
              </p>
              <p
                className={`text-lg font-medium mt-1 ${
                  quote.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {quote.change >= 0 ? '+' : ''}
                {formatCurrency(quote.change, currency)} (
                {formatPercent(quote.change_percent)})
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="p-4 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">시가총액</h3>
            <p className="text-xl font-bold mt-2">
              {info.market_cap
                ? formatLargeNumber(info.market_cap)
                : 'N/A'}
            </p>
          </div>

          <div className="p-4 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">산업</h3>
            <p className="text-xl font-bold mt-2">{info.industry || 'N/A'}</p>
          </div>

          <div className="p-4 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">거래량</h3>
            <p className="text-xl font-bold mt-2">
              {formatLargeNumber(quote.volume)}
            </p>
          </div>

          <div className="p-4 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">통화</h3>
            <p className="text-xl font-bold mt-2">{currency}</p>
          </div>
        </div>

        {/* Investment Insights */}
        <div className="mb-8">
          <InvestmentInsights ticker={ticker} />
        </div>

        {/* Chart */}
        <div className="border rounded-lg p-6 bg-card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">주가 차트</h2>
            <div className="flex gap-2">
              {(['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1 text-sm rounded-md ${
                    period === p
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  {p === '1d'
                    ? '1일'
                    : p === '5d'
                    ? '5일'
                    : p === '1mo'
                    ? '1개월'
                    : p === '3mo'
                    ? '3개월'
                    : p === '6mo'
                    ? '6개월'
                    : p === '1y'
                    ? '1년'
                    : '5년'}
                </button>
              ))}
            </div>
          </div>

          <StockChart ticker={ticker} period={period} currency={currency} />
        </div>

        {/* AI Predictions */}
        <div className="mt-8 border rounded-lg p-6 bg-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">🤖 AI 주가 예측</h2>
            <button
              onClick={loadPrediction}
              disabled={predictionLoading}
              className="px-3 py-1 text-sm bg-secondary hover:bg-secondary/80 rounded-md disabled:opacity-50"
            >
              {predictionLoading ? '로딩 중...' : '새로고침'}
            </button>
          </div>

          {predictionLoading && !prediction ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : prediction ? (
            <div className="space-y-6">
              {/* Prediction Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">
                    예측 가격 (5일 후)
                  </h3>
                  <p className="text-2xl font-bold">
                    {formatCurrency(prediction.prediction.predicted_price, currency)}
                  </p>
                  <p
                    className={`text-sm font-medium mt-1 ${
                      prediction.prediction.change >= 0
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {prediction.prediction.change >= 0 ? '+' : ''}
                    {formatCurrency(prediction.prediction.change, currency)} (
                    {formatPercent(prediction.prediction.change_percent)})
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">
                    투자 의견
                  </h3>
                  <p
                    className={`text-2xl font-bold ${
                      prediction.action === 'BUY'
                        ? 'text-green-600'
                        : prediction.action === 'SELL'
                        ? 'text-red-600'
                        : 'text-yellow-600'
                    }`}
                  >
                    {prediction.action === 'BUY'
                      ? '매수 ▲'
                      : prediction.action === 'SELL'
                      ? '매도 ▼'
                      : '보유 ─'}
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">
                    신뢰도
                  </h3>
                  <div className="flex items-center">
                    <p className="text-2xl font-bold">
                      {Math.round(prediction.prediction.confidence * 100)}%
                    </p>
                    <div className="ml-3 flex-1">
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div
                          className="bg-primary rounded-full h-2 transition-all"
                          style={{
                            width: `${prediction.prediction.confidence * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed Explanation */}
              <div className="border-t pt-6">
                <PredictionExplanation
                  prediction={prediction}
                  currentPrice={quote.current_price}
                  currency={currency}
                  ticker={ticker}
                />
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="max-w-md mx-auto">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-yellow-100 flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-yellow-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">
                  AI 예측 모델 학습 필요
                </h3>
                <p className="text-muted-foreground mb-4">
                  이 종목({ticker})에 대한 AI 예측 모델이 아직 학습되지 않았습니다.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-left">
                  <p className="font-medium text-blue-900 mb-2">💡 현재 학습된 종목:</p>
                  <ul className="text-blue-800 space-y-1">
                    <li>• AAPL (Apple)</li>
                    <li>• GOOGL (Alphabet)</li>
                    <li>• 005930.KS (삼성전자)</li>
                  </ul>
                  <p className="text-blue-700 mt-3 text-xs">
                    더 많은 종목의 AI 예측 기능이 곧 추가될 예정입니다.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
