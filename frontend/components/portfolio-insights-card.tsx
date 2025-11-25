'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { portfolioApi, type PortfolioInsights } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { formatCurrency, formatPercent } from '@/lib/utils'

interface Props {
  portfolioId: number
}

export function PortfolioInsightsCard({ portfolioId }: Props) {
  const router = useRouter()
  const [insights, setInsights] = useState<PortfolioInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadInsights()
  }, [portfolioId])

  const loadInsights = async () => {
    try {
      setLoading(true)
      const response = await portfolioApi.getInsights(portfolioId)
      setInsights(response.data)
      setError(null)
    } catch (err) {
      setError('인사이트를 불러오는 중 오류가 발생했습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="border rounded-lg p-6 bg-card space-y-4">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    )
  }

  if (error || !insights) {
    return null
  }

  const { analysis, summary, rebalancing, top_recommendations, overall_score } = insights

  return (
    <div className="border rounded-lg p-6 bg-card space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold">📊 Portfolio 2.0 인사이트</h2>
          <p className="text-sm text-muted-foreground mt-1">
            AI 기반 포트폴리오 분석 및 추천
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">{overall_score}/100</div>
          <div className="text-xs text-muted-foreground">종합 점수</div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div className="text-xs text-muted-foreground">총 수익률</div>
          <div
            className={`text-lg font-bold ${
              analysis.performance.total_return >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {formatPercent(analysis.performance.total_return)}
          </div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">샤프 비율</div>
          <div className="text-lg font-bold">
            {analysis.risk.sharpe_ratio?.toFixed(2) || '-'}
          </div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">섹터 다각화</div>
          <div className="text-lg font-bold">
            {analysis.diversification.sector_diversity_score?.toFixed(0) || '-'}
          </div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">변동성</div>
          <div className="text-lg font-bold">
            {analysis.risk.volatility?.toFixed(1) || '-'}%
          </div>
        </div>
      </div>

      {/* Strengths & Warnings */}
      {(summary.strengths.length > 0 || summary.warnings.length > 0) && (
        <div className="space-y-3">
          {summary.strengths.length > 0 && (
            <div>
              <div className="text-sm font-medium text-green-600 mb-1">✓ 강점</div>
              <ul className="space-y-1">
                {summary.strengths.map((strength, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground pl-4">
                    • {strength}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {summary.warnings.length > 0 && (
            <div>
              <div className="text-sm font-medium text-amber-600 mb-1">⚠️ 경고</div>
              <ul className="space-y-1">
                {summary.warnings.map((warning, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground pl-4">
                    • {warning}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Recommendations Preview */}
      {top_recommendations.length > 0 && (
        <div>
          <div className="text-sm font-medium mb-2">🎯 AI 추천 종목 (상위 3개)</div>
          <div className="space-y-2">
            {top_recommendations.map((rec) => (
              <div
                key={rec.ticker}
                className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
              >
                <div>
                  <div className="font-medium">{rec.ticker}</div>
                  <div className="text-xs text-muted-foreground">{rec.name}</div>
                </div>
                <div className="text-right">
                  <div
                    className={`text-sm font-bold ${
                      rec.action === 'BUY' || rec.action === 'ADD'
                        ? 'text-green-600'
                        : rec.action === 'SELL' || rec.action === 'REDUCE'
                        ? 'text-red-600'
                        : 'text-gray-600'
                    }`}
                  >
                    {rec.action}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    신뢰도: {(rec.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rebalancing Status */}
      {rebalancing.needs_rebalancing && (
        <div
          className={`p-4 rounded-lg ${
            rebalancing.severity === 'HIGH'
              ? 'bg-red-50 border border-red-200'
              : rebalancing.severity === 'MEDIUM'
              ? 'bg-amber-50 border border-amber-200'
              : 'bg-blue-50 border border-blue-200'
          }`}
        >
          <div className="flex items-start justify-between">
            <div>
              <div className="font-medium text-sm">
                {rebalancing.severity === 'HIGH'
                  ? '🚨 리밸런싱 긴급 필요'
                  : rebalancing.severity === 'MEDIUM'
                  ? '⚠️ 리밸런싱 권장'
                  : 'ℹ️ 리밸런싱 제안'}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {rebalancing.triggers.slice(0, 2).join(', ')}
              </div>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => router.push(`/portfolios/${portfolioId}/rebalance`)}
            >
              상세보기
            </Button>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {summary.suggestions.length > 0 && (
        <div>
          <div className="text-sm font-medium mb-2">💡 제안사항</div>
          <ul className="space-y-1">
            {summary.suggestions.map((suggestion, idx) => (
              <li key={idx} className="text-sm text-muted-foreground pl-4">
                • {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <Button
          variant="default"
          size="sm"
          className="flex-1"
          onClick={() => router.push(`/portfolios/${portfolioId}/analytics`)}
        >
          상세 분석 보기
        </Button>
        <Button variant="outline" size="sm" onClick={loadInsights}>
          새로고침
        </Button>
      </div>
    </div>
  )
}
