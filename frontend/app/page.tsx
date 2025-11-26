'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Activity, ArrowRight, BarChart3 } from 'lucide-react'
import { LegalDisclaimer } from '@/components/legal-disclaimer'
import { formatPrice } from '@/lib/utils'
import { getStockName } from '@/lib/stock-names'

interface PredictionSummary {
  ticker: string
  action: 'BUY' | 'SELL' | 'HOLD'
  predicted_change_percent: number
  confidence: number
  current_price?: number
}

export default function Home() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [predictions, setPredictions] = useState<PredictionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    trainedModels: 0,
    accuracy: 0,
    totalPredictions: 0
  })

  useEffect(() => {
    setMounted(true)
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Load AI predictions summary
      const [predictionsRes, summaryRes] = await Promise.all([
        fetch('http://localhost:8001/api/v1/predictions/summary'),
        fetch('http://localhost:8001/api/v1/predictions/daily/accuracy')
      ])

      const predictionsData = await predictionsRes.json()
      const summaryData = await summaryRes.json()

      if (predictionsData.predictions?.length > 0) {
        const mapped = predictionsData.predictions
          .slice(0, 5)
          .map((p: any) => ({
            ticker: p.ticker,
            action: p.action,
            predicted_change_percent: p.change_percent || 0,
            confidence: p.confidence || 0,
            current_price: p.current_price
          }))
        setPredictions(mapped)
      }

      setStats({
        trainedModels: predictionsData.trained_models?.length || 0,
        accuracy: summaryData.direction_accuracy || 0,
        totalPredictions: summaryData.count || 0
      })
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!mounted) {
    return null
  }

  const buyPredictions = predictions.filter(p => p.action === 'BUY')
  const topBuys = buyPredictions.slice(0, 5)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Section 1: Overview Stats */}
        <section>
          <h1 className="text-3xl font-bold mb-6">Finance Hub 대시보드</h1>

          <div className="grid md:grid-cols-3 gap-6">
            {/* AI Models */}
            <div className="p-6 border rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
              <div className="flex items-center justify-between mb-2">
                <BarChart3 className="w-8 h-8 text-blue-600" />
                <span className="text-3xl font-bold text-blue-600">{stats.trainedModels}</span>
              </div>
              <p className="text-sm font-medium text-muted-foreground">학습된 AI 모델</p>
            </div>

            {/* Accuracy */}
            <div className="p-6 border rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20">
              <div className="flex items-center justify-between mb-2">
                <Activity className="w-8 h-8 text-green-600" />
                <span className="text-3xl font-bold text-green-600">
                  {(stats.accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-sm font-medium text-muted-foreground">예측 정확도</p>
            </div>

            {/* Total Predictions */}
            <div className="p-6 border rounded-lg bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
              <div className="flex items-center justify-between mb-2">
                <DollarSign className="w-8 h-8 text-purple-600" />
                <span className="text-3xl font-bold text-purple-600">{stats.totalPredictions}</span>
              </div>
              <p className="text-sm font-medium text-muted-foreground">총 예측 수</p>
            </div>
          </div>
        </section>

        {/* Section 2: Top AI Recommendations */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">오늘의 AI 추천 종목 (매수)</h2>
            <button
              onClick={() => router.push('/prediction-map')}
              className="flex items-center gap-2 text-primary hover:underline"
            >
              전체 보기
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-muted-foreground">AI 예측 로딩 중...</p>
            </div>
          ) : topBuys.length === 0 ? (
            <div className="p-12 border rounded-lg text-center">
              <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">현재 활성화된 매수 추천이 없습니다.</p>
              <button
                onClick={() => router.push('/admin/models')}
                className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
              >
                AI 모델 학습하기
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {topBuys.map((pred) => (
                <div
                  key={pred.ticker}
                  onClick={() => router.push(`/stocks/${pred.ticker}`)}
                  className="p-5 border rounded-lg hover:bg-accent cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-lg">{pred.ticker}</h3>
                      <p className="text-sm text-muted-foreground">{getStockName(pred.ticker)}</p>
                    </div>
                    <div className="flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-950/30 text-green-700 dark:text-green-400 rounded text-xs font-medium">
                      <TrendingUp className="w-3 h-3" />
                      BUY
                    </div>
                  </div>

                  {pred.current_price && (
                    <div className="mb-3">
                      <p className="text-2xl font-bold">
                        {formatPrice(pred.current_price, pred.ticker)}
                      </p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <div>
                      <p className="text-muted-foreground">예상 수익률</p>
                      <p className="font-semibold text-green-600">
                        +{pred.predicted_change_percent.toFixed(2)}%
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-muted-foreground">신뢰도</p>
                      <p className="font-semibold">
                        {(pred.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quick Actions */}
          <div className="mt-6 grid md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/explore')}
              className="p-4 border rounded-lg hover:bg-accent transition-colors text-left"
            >
              <h3 className="font-semibold mb-1">내 포트폴리오</h3>
              <p className="text-sm text-muted-foreground">보유 종목 관리 및 분석</p>
            </button>

            <button
              onClick={() => router.push('/stocks-list')}
              className="p-4 border rounded-lg hover:bg-accent transition-colors text-left"
            >
              <h3 className="font-semibold mb-1">종목 탐색</h3>
              <p className="text-sm text-muted-foreground">인기 종목 및 AI 예측 확인</p>
            </button>

            <button
              onClick={() => router.push('/education')}
              className="p-4 border rounded-lg hover:bg-accent transition-colors text-left"
            >
              <h3 className="font-semibold mb-1">투자 교육</h3>
              <p className="text-sm text-muted-foreground">AI 기반 투자 학습</p>
            </button>
          </div>
        </section>

        {/* Section 3: Legal Disclaimer */}
        <section>
          <LegalDisclaimer variant="compact" />
        </section>
      </div>
    </div>
  )
}
