'use client'

import { useEffect, useState } from 'react'
import { accuracyApi, type AccuracyDashboard } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Target, AlertCircle } from 'lucide-react'

export default function AccuracyPage() {
  const [dashboard, setDashboard] = useState<AccuracyDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    loadDashboard()
  }, [days])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const response = await accuracyApi.getDashboard(days)
      setDashboard(response.data)
    } catch (error) {
      console.error('Failed to load accuracy dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">로딩 중...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-muted-foreground">
          데이터를 불러올 수 없습니다
        </div>
      </div>
    )
  }

  const { overall_metrics, by_ticker, time_series, top_performers, worst_performers } = dashboard

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">예측 정확도 대시보드</h1>
        <p className="text-muted-foreground">AI 모델의 예측 정확도를 실시간으로 모니터링합니다</p>
      </div>

      {/* Period Selector */}
      <div className="flex gap-2 mb-6">
        {[7, 14, 30, 60, 90].map((period) => (
          <button
            key={period}
            onClick={() => setDays(period)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              days === period
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            {period}일
          </button>
        ))}
      </div>

      {/* Overall Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">전체 예측</span>
            <Target className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-3xl font-bold">{overall_metrics.total_predictions}</div>
          <p className="text-xs text-muted-foreground mt-1">총 예측 건수</p>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">방향 정확도</span>
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-3xl font-bold">{(overall_metrics.direction_accuracy * 100).toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground mt-1">
            {overall_metrics.correct_direction}/{overall_metrics.total_predictions} 정확
          </p>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">평균 오차</span>
            <AlertCircle className="w-5 h-5 text-orange-500" />
          </div>
          <div className="text-3xl font-bold">{overall_metrics.avg_price_error_percent.toFixed(2)}%</div>
          <p className="text-xs text-muted-foreground mt-1">가격 오차율</p>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">종합 점수</span>
            <Target className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-3xl font-bold">{(overall_metrics.overall_score * 100).toFixed(1)}</div>
          <p className="text-xs text-muted-foreground mt-1">100점 만점</p>
        </div>
      </div>

      {/* Time Series Chart */}
      <div className="bg-card p-6 rounded-lg border mb-8">
        <h2 className="text-xl font-bold mb-4">시간별 정확도 추이</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={time_series}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
            />
            <YAxis yAxisId="left" domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip
              labelFormatter={(value) => new Date(value).toLocaleDateString('ko-KR')}
              formatter={(value: number, name: string) => {
                if (name === '방향 정확도') return `${(value * 100).toFixed(1)}%`
                if (name === '평균 오차') return `${value.toFixed(2)}%`
                return value
              }}
            />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="direction_accuracy" stroke="#10b981" name="방향 정확도" strokeWidth={2} />
            <Line yAxisId="left" type="monotone" dataKey="avg_error_percent" stroke="#f59e0b" name="평균 오차" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Top and Worst Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Top Performers */}
        <div className="bg-card p-6 rounded-lg border">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-500" />
            최고 성과 종목 TOP 5
          </h2>
          <div className="space-y-3">
            {top_performers.map((ticker, idx) => (
              <div key={ticker.ticker} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-sm">
                    {idx + 1}
                  </div>
                  <div>
                    <div className="font-bold">{ticker.ticker}</div>
                    <div className="text-xs text-muted-foreground">{ticker.total_predictions}개 예측</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-green-600">{(ticker.overall_score * 100).toFixed(1)}</div>
                  <div className="text-xs text-muted-foreground">방향 {(ticker.direction_accuracy * 100).toFixed(0)}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Worst Performers */}
        <div className="bg-card p-6 rounded-lg border">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-red-500" />
            개선 필요 종목 TOP 5
          </h2>
          <div className="space-y-3">
            {worst_performers.map((ticker, idx) => (
              <div key={ticker.ticker} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center font-bold text-sm">
                    {idx + 1}
                  </div>
                  <div>
                    <div className="font-bold">{ticker.ticker}</div>
                    <div className="text-xs text-muted-foreground">{ticker.total_predictions}개 예측</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-red-600">{(ticker.overall_score * 100).toFixed(1)}</div>
                  <div className="text-xs text-muted-foreground">방향 {(ticker.direction_accuracy * 100).toFixed(0)}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* All Tickers Performance */}
      <div className="bg-card p-6 rounded-lg border">
        <h2 className="text-xl font-bold mb-4">종목별 상세 정확도</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3 font-bold">종목</th>
                <th className="text-center p-3 font-bold">예측 수</th>
                <th className="text-center p-3 font-bold">방향 정확도</th>
                <th className="text-center p-3 font-bold">평균 오차</th>
                <th className="text-center p-3 font-bold">종합 점수</th>
              </tr>
            </thead>
            <tbody>
              {by_ticker.map((ticker) => (
                <tr key={ticker.ticker} className="border-b hover:bg-secondary/50 transition-colors">
                  <td className="p-3 font-bold">{ticker.ticker}</td>
                  <td className="p-3 text-center">{ticker.total_predictions}</td>
                  <td className="p-3 text-center">
                    <span className={ticker.direction_accuracy >= 0.6 ? 'text-green-600' : 'text-red-600'}>
                      {(ticker.direction_accuracy * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3 text-center">{ticker.avg_price_error_percent.toFixed(2)}%</td>
                  <td className="p-3 text-center">
                    <span className={`font-bold ${ticker.overall_score >= 60 ? 'text-green-600' : ticker.overall_score >= 40 ? 'text-orange-600' : 'text-red-600'}`}>
                      {(ticker.overall_score * 100).toFixed(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
