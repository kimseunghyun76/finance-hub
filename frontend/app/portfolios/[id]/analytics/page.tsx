'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { portfolioApi, recommendationApi, type PortfolioAnalytics, type StockRecommendation } from '@/lib/api'
import { formatCurrency, formatPercent } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function PortfolioAnalyticsPage() {
  const params = useParams()
  const router = useRouter()
  const portfolioId = parseInt(params.id as string)

  const [analytics, setAnalytics] = useState<PortfolioAnalytics | null>(null)
  const [recommendations, setRecommendations] = useState<StockRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [portfolioId])

  const loadData = async () => {
    try {
      setLoading(true)

      // Load analytics
      const analyticsResponse = await portfolioApi.getAnalytics(portfolioId)
      setAnalytics(analyticsResponse.data.analysis)

      // Load recommendations
      const recsResponse = await recommendationApi.getRecommendations(portfolioId, undefined, 20)
      setRecommendations(recsResponse.data.recommendations)

      setError(null)
    } catch (err) {
      setError('분석 데이터를 불러오는 중 오류가 발생했습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <Skeleton className="h-9 w-64" />
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <Skeleton className="h-96 w-full" />
        </main>
      </div>
    )
  }

  if (error || !analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-destructive">{error || '분석 데이터를 찾을 수 없습니다.'}</p>
          <button
            onClick={() => router.push(`/portfolios/${portfolioId}`)}
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
          >
            포트폴리오로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  const { performance, risk, diversification, holdings } = analytics

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => router.push(`/portfolios/${portfolioId}`)}
            className="text-sm text-muted-foreground hover:text-foreground mb-2"
          >
            ← 포트폴리오로 돌아가기
          </button>
          <h1 className="text-3xl font-bold">📊 포트폴리오 상세 분석</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="performance" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="performance">성과</TabsTrigger>
            <TabsTrigger value="risk">리스크</TabsTrigger>
            <TabsTrigger value="diversification">다각화</TabsTrigger>
            <TabsTrigger value="recommendations">AI 추천</TabsTrigger>
          </TabsList>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <div className="border rounded-lg p-6 bg-card">
              <h2 className="text-xl font-bold mb-6">📈 성과 지표</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">총 평가액</h3>
                  <p className="text-2xl font-bold">{formatCurrency(performance.total_value, 'USD')}</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">총 투자금</h3>
                  <p className="text-2xl font-bold">{formatCurrency(performance.total_cost, 'USD')}</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">평가 손익</h3>
                  <p className={`text-2xl font-bold ${performance.total_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(performance.total_gain, 'USD')}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">총 수익률</h3>
                  <p className={`text-2xl font-bold ${performance.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(performance.total_return)}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">일일 수익률</h3>
                  <p className={`text-2xl font-bold ${performance.daily_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(performance.daily_return)}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">연간 수익률 (예상)</h3>
                  <p className={`text-2xl font-bold ${performance.annualized_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(performance.annualized_return)}
                  </p>
                </div>
              </div>
            </div>

            {/* Holdings Performance */}
            <div className="border rounded-lg p-6 bg-card">
              <h2 className="text-xl font-bold mb-4">종목별 성과</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium">종목</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">비중</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">현재가</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">평가액</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">손익</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">수익률</th>
                    </tr>
                  </thead>
                  <tbody>
                    {holdings.map((holding) => (
                      <tr key={holding.ticker} className="border-b hover:bg-muted/50">
                        <td className="px-4 py-3">
                          <div>
                            <p className="font-medium">{holding.ticker}</p>
                            <p className="text-sm text-muted-foreground">{holding.name}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right">{holding.weight.toFixed(1)}%</td>
                        <td className="px-4 py-3 text-right">${holding.current_price.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right">${holding.total_value.toFixed(2)}</td>
                        <td className={`px-4 py-3 text-right font-medium ${holding.gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ${holding.gain.toFixed(2)}
                        </td>
                        <td className={`px-4 py-3 text-right font-medium ${holding.gain_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatPercent(holding.gain_percent)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </TabsContent>

          {/* Risk Tab */}
          <TabsContent value="risk" className="space-y-6">
            <div className="border rounded-lg p-6 bg-card">
              <h2 className="text-xl font-bold mb-6">⚠️ 리스크 지표</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">변동성 (Volatility)</h3>
                  <p className="text-2xl font-bold">{risk.volatility?.toFixed(2) || '-'}%</p>
                  <p className="text-xs text-muted-foreground mt-1">연간화된 표준편차</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">샤프 비율 (Sharpe Ratio)</h3>
                  <p className="text-2xl font-bold">{risk.sharpe_ratio?.toFixed(2) || '-'}</p>
                  <p className="text-xs text-muted-foreground mt-1">위험 대비 수익 (높을수록 좋음)</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">최대 낙폭 (Max Drawdown)</h3>
                  <p className="text-2xl font-bold text-red-600">{risk.max_drawdown?.toFixed(2) || '-'}%</p>
                  <p className="text-xs text-muted-foreground mt-1">최고점 대비 최대 하락</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">베타 (Beta)</h3>
                  <p className="text-2xl font-bold">{risk.beta?.toFixed(2) || '-'}</p>
                  <p className="text-xs text-muted-foreground mt-1">시장 대비 민감도 (SPY 기준)</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">알파 (Alpha)</h3>
                  <p className="text-2xl font-bold">{risk.alpha?.toFixed(2) || '-'}%</p>
                  <p className="text-xs text-muted-foreground mt-1">시장 초과 수익</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">VaR 95%</h3>
                  <p className="text-2xl font-bold text-amber-600">{risk.var_95?.toFixed(2) || '-'}%</p>
                  <p className="text-xs text-muted-foreground mt-1">95% 신뢰수준 손실 예상</p>
                </div>
              </div>

              {/* Risk Interpretation */}
              <div className="mt-6 p-4 bg-muted/30 rounded-lg">
                <h3 className="font-medium mb-2">해석</h3>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• 샤프 비율 {risk.sharpe_ratio > 1 ? '> 1: 우수한 위험 대비 수익' : risk.sharpe_ratio > 0.5 ? '> 0.5: 적절한 위험 대비 수익' : '< 0.5: 낮은 위험 대비 수익'}</li>
                  <li>• 베타 {risk.beta > 1 ? '> 1: 시장보다 높은 변동성' : risk.beta < 1 ? '< 1: 시장보다 낮은 변동성' : '= 1: 시장과 동일한 변동성'}</li>
                  <li>• 알파 {risk.alpha > 0 ? '> 0: 시장 초과 수익 달성' : '< 0: 시장 대비 저조한 성과'}</li>
                </ul>
              </div>
            </div>
          </TabsContent>

          {/* Diversification Tab */}
          <TabsContent value="diversification" className="space-y-6">
            <div className="border rounded-lg p-6 bg-card">
              <h2 className="text-xl font-bold mb-6">🌐 다각화 분석</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">섹터 다양성 점수</h3>
                  <p className="text-2xl font-bold">{diversification.sector_diversity_score?.toFixed(0) || '-'}</p>
                  <p className="text-xs text-muted-foreground mt-1">0-100 (높을수록 다각화)</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">지역 다양성 점수</h3>
                  <p className="text-2xl font-bold">{diversification.geographic_diversity_score?.toFixed(0) || '-'}</p>
                  <p className="text-xs text-muted-foreground mt-1">0-100 (높을수록 다각화)</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">집중도 리스크</h3>
                  <p className="text-2xl font-bold text-amber-600">{diversification.concentration_risk?.toFixed(1) || '-'}%</p>
                  <p className="text-xs text-muted-foreground mt-1">상위 5개 종목 비중</p>
                </div>
              </div>

              {/* Sector Distribution */}
              <div className="mb-6">
                <h3 className="font-medium mb-4">섹터별 분포</h3>
                <div className="space-y-3">
                  {Object.entries(diversification.sector_distribution || {}).map(([sector, weight]) => (
                    <div key={sector}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{sector}</span>
                        <span className="font-medium">{weight.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{ width: `${Math.min(weight, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Country Distribution */}
              <div>
                <h3 className="font-medium mb-4">국가별 분포</h3>
                <div className="space-y-3">
                  {Object.entries(diversification.country_distribution || {}).map(([country, weight]) => (
                    <div key={country}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{country === 'US' ? '🇺🇸 미국' : country === 'KR' ? '🇰🇷 한국' : country}</span>
                        <span className="font-medium">{weight.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{ width: `${Math.min(weight, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            <div className="border rounded-lg p-6 bg-card">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold">🎯 AI 종목 추천</h2>
                  <p className="text-sm text-muted-foreground mt-1">
                    {recommendations.length}개 추천 ({analytics.snapshot_date})
                  </p>
                </div>
                <Button onClick={loadData} variant="outline" size="sm">
                  새로고침
                </Button>
              </div>

              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div
                    key={rec.ticker}
                    className="border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => router.push(`/stocks/${rec.ticker}`)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-bold text-lg">{rec.ticker}</h3>
                          {rec.is_etf === 1 && (
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">ETF</span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{rec.name}</p>
                        {rec.sector && (
                          <p className="text-xs text-muted-foreground mt-1">{rec.sector}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div
                          className={`text-lg font-bold ${
                            rec.action === 'BUY' || rec.action === 'ADD'
                              ? 'text-green-600'
                              : rec.action === 'SELL' || rec.action === 'REDUCE'
                              ? 'text-red-600'
                              : 'text-gray-600'
                          }`}
                        >
                          {rec.action}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          목표 비중: {rec.target_weight.toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-xs text-muted-foreground">신뢰도</div>
                        <div className="font-medium">{(rec.confidence_score * 100).toFixed(0)}%</div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground">AI 예측</div>
                        <div className="font-medium">{(rec.ai_prediction_score * 100).toFixed(0)}%</div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground">기술적 분석</div>
                        <div className="font-medium">{(rec.technical_score * 100).toFixed(0)}%</div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground">현재가</div>
                        <div className="font-medium">${rec.current_price.toFixed(2)}</div>
                      </div>
                    </div>

                    <div className="p-3 bg-muted/30 rounded">
                      <div className="text-xs font-medium text-muted-foreground mb-1">
                        {rec.reason_category}
                      </div>
                      <div className="text-sm">{rec.reason_detail}</div>
                    </div>
                  </div>
                ))}

                {recommendations.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    추천 종목이 없습니다.
                  </div>
                )}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
