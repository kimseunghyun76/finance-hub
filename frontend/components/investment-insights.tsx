'use client'

import { useEffect, useState } from 'react'
import { insightApi, type InvestmentInsight } from '@/lib/api'
import { Skeleton } from '@/components/ui/skeleton'
import ReactMarkdown from 'react-markdown'

interface InvestmentInsightsProps {
  ticker: string
}

export function InvestmentInsights({ ticker }: InvestmentInsightsProps) {
  const [insight, setInsight] = useState<InvestmentInsight | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'buffett' | 'lynch' | 'graham'>('buffett')

  useEffect(() => {
    loadInsight()
  }, [ticker])

  const loadInsight = async () => {
    setLoading(true)
    setError(null)

    try {
      const res = await insightApi.getInsight(ticker)
      setInsight(res.data)
    } catch (err) {
      setError('투자 분석을 불러올 수 없습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'BUY':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'SELL':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'HOLD':
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    }
  }

  const getRatingText = (rating: string) => {
    switch (rating) {
      case 'BUY':
        return '매수 ▲'
      case 'SELL':
        return '매도 ▼'
      case 'HOLD':
      default:
        return '보유 ─'
    }
  }

  if (loading) {
    return (
      <div className="border rounded-lg p-6 bg-card">
        <div className="flex items-center justify-between mb-6">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-9 w-32" />
        </div>
        <div className="flex gap-2 mb-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-10 w-32" />
          ))}
        </div>
        <Skeleton className="h-40 w-full" />
      </div>
    )
  }

  if (error || !insight) {
    return (
      <div className="border rounded-lg p-6 bg-card">
        <h2 className="text-xl font-bold mb-4">💼 전문가 투자 분석</h2>
        <p className="text-muted-foreground">{error || '분석을 불러올 수 없습니다.'}</p>
      </div>
    )
  }

  return (
    <div className="border rounded-lg p-6 bg-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">💼 전문가 투자 분석</h2>
        <div className={`px-4 py-2 rounded-lg border font-semibold ${getRatingColor(insight.overall_rating)}`}>
          {getRatingText(insight.overall_rating)}
          <span className="ml-2 text-sm font-normal">
            (신뢰도: {Math.round(insight.confidence_score)}%)
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 border-b">
        <button
          onClick={() => setActiveTab('buffett')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'buffett'
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          워렌 버핏
        </button>
        <button
          onClick={() => setActiveTab('lynch')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'lynch'
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          피터 린치
        </button>
        <button
          onClick={() => setActiveTab('graham')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'graham'
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          벤자민 그레이엄
        </button>
      </div>

      {/* Tab Content */}
      <div className="prose prose-sm max-w-none dark:prose-invert">
        {activeTab === 'buffett' && (
          <div className="text-foreground leading-relaxed">
            <ReactMarkdown>{insight.buffett_analysis}</ReactMarkdown>
          </div>
        )}
        {activeTab === 'lynch' && (
          <div className="text-foreground leading-relaxed">
            <ReactMarkdown>{insight.lynch_analysis}</ReactMarkdown>
          </div>
        )}
        {activeTab === 'graham' && (
          <div className="text-foreground leading-relaxed">
            <ReactMarkdown>{insight.graham_analysis}</ReactMarkdown>
          </div>
        )}
      </div>

      {/* Stock Metrics */}
      {(insight.current_price || insight.pe_ratio) && (
        <div className="mt-6 pt-6 border-t">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {insight.current_price && (
              <div className="p-3 bg-secondary/50 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">분석 시점 주가</p>
                <p className="text-lg font-semibold">
                  ${insight.current_price.toFixed(2)}
                </p>
              </div>
            )}
            {insight.pe_ratio && (
              <div className="p-3 bg-secondary/50 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">P/E 비율</p>
                <p className="text-lg font-semibold">
                  {insight.pe_ratio.toFixed(2)}
                </p>
              </div>
            )}
            {insight.generated_at && (
              <div className="p-3 bg-secondary/50 rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">분석 생성일</p>
                <p className="text-sm font-medium">
                  {new Date(insight.generated_at).toLocaleDateString('ko-KR')}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <p className="text-xs text-yellow-800 dark:text-yellow-200">
          ⚠️ 이 분석은 참고용이며, 투자 결정은 신중히 하시기 바랍니다.
          실제 투자 시 전문가와 상담하고 충분한 조사를 거치시기 바랍니다.
        </p>
      </div>
    </div>
  )
}
