"use client"

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react'
import { LoadingProgress } from './loading-progress'

interface SectorData {
  sector: string
  avg_change_percent: number
  total_stocks: number
  buy_count: number
  sell_count: number
  hold_count: number
  us_count: number
  kr_count: number
  momentum_score: number
  recommendation: 'STRONG_BUY' | 'BUY' | 'NEUTRAL' | 'AVOID'
  top_picks: Array<{
    ticker: string
    action: string
    change_percent: number
    confidence: number
    market: string
  }>
}

interface SectorAnalysis {
  sectors: SectorData[]
  us_sectors: SectorData[]
  kr_sectors: SectorData[]
  top_momentum_sectors: SectorData[]
}

export function SectorRecommendations() {
  const [data, setData] = useState<SectorAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedMarket, setSelectedMarket] = useState<'all' | 'us' | 'kr'>('all')

  useEffect(() => {
    loadSectorAnalysis()
  }, [])

  const loadSectorAnalysis = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8001/api/v1/predictions/sectors/analysis')
      if (!response.ok) throw new Error('Failed to load')
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Error loading sector analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRecommendationBadge = (recommendation: string) => {
    const badges = {
      'STRONG_BUY': { color: 'bg-green-600', icon: TrendingUp, text: '강력 매수' },
      'BUY': { color: 'bg-green-500', icon: TrendingUp, text: '매수' },
      'NEUTRAL': { color: 'bg-gray-500', icon: Minus, text: '중립' },
      'AVOID': { color: 'bg-red-600', icon: AlertTriangle, text: '회피' }
    }
    const badge = badges[recommendation as keyof typeof badges] || badges.NEUTRAL
    const Icon = badge.icon

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 ${badge.color} text-white text-xs font-semibold rounded`}>
        <Icon className="w-3 h-3" />
        {badge.text}
      </span>
    )
  }

  const getSectorsToDisplay = () => {
    if (!data) return []

    if (selectedMarket === 'us') return data.us_sectors
    if (selectedMarket === 'kr') return data.kr_sectors
    return data.sectors
  }

  if (loading) {
    return <LoadingProgress message="섹터 데이터를 분석하는 중..." estimatedSeconds={12} />
  }

  if (!data || data.sectors.length === 0) {
    return (
      <div className="p-6 border rounded-lg bg-card text-center text-muted-foreground">
        섹터 분석 데이터가 없습니다
      </div>
    )
  }

  const sectors = getSectorsToDisplay()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">🎯 AI 섹터 추천</h2>
          <p className="text-sm text-muted-foreground mt-1">
            지금 주목해야 할 섹터와 추천 종목
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedMarket('all')}
            className={`px-3 py-1 text-sm rounded ${
              selectedMarket === 'all'
                ? 'bg-primary text-primary-foreground'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            전체
          </button>
          <button
            onClick={() => setSelectedMarket('us')}
            className={`px-3 py-1 text-sm rounded ${
              selectedMarket === 'us'
                ? 'bg-primary text-primary-foreground'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            🇺🇸 미국
          </button>
          <button
            onClick={() => setSelectedMarket('kr')}
            className={`px-3 py-1 text-sm rounded ${
              selectedMarket === 'kr'
                ? 'bg-primary text-primary-foreground'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            🇰🇷 한국
          </button>
        </div>
      </div>

      {/* Top Momentum Sectors Highlight */}
      {data.top_momentum_sectors.length > 0 && (
        <div className="p-6 border-2 border-green-500 rounded-lg bg-green-50 dark:bg-green-950">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            지금 가장 핫한 섹터 TOP {data.top_momentum_sectors.length}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.top_momentum_sectors.map((sector, index) => (
              <div key={sector.sector} className="p-4 bg-white dark:bg-gray-900 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="text-2xl font-bold text-green-600">#{index + 1}</span>
                    <h4 className="font-bold mt-1">{sector.sector}</h4>
                  </div>
                  {getRecommendationBadge(sector.recommendation)}
                </div>
                <div className="space-y-2 mt-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">예상 수익률</span>
                    <span className={`font-semibold ${sector.avg_change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {sector.avg_change_percent > 0 && '+'}{sector.avg_change_percent}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">모멘텀 점수</span>
                    <span className="font-semibold">{sector.momentum_score}</span>
                  </div>
                  {sector.top_picks.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-muted-foreground mb-1">추천 종목</p>
                      <div className="flex flex-wrap gap-1">
                        {sector.top_picks.slice(0, 3).map(pick => (
                          <span key={pick.ticker} className="text-xs bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded">
                            {pick.ticker}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Sectors Table */}
      <div className="border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">섹터</th>
                <th className="px-4 py-3 text-center text-sm font-medium">추천</th>
                <th className="px-4 py-3 text-right text-sm font-medium">예상 변화</th>
                <th className="px-4 py-3 text-right text-sm font-medium">모멘텀</th>
                <th className="px-4 py-3 text-center text-sm font-medium">종목 수</th>
                <th className="px-4 py-3 text-center text-sm font-medium">BUY/HOLD/SELL</th>
                <th className="px-4 py-3 text-left text-sm font-medium">추천 종목</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {sectors.map((sector) => (
                <tr key={sector.sector} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 font-medium">{sector.sector}</td>
                  <td className="px-4 py-3 text-center">
                    {getRecommendationBadge(sector.recommendation)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className={`font-semibold ${sector.avg_change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {sector.avg_change_percent > 0 && '+'}{sector.avg_change_percent}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="font-mono text-sm">{sector.momentum_score}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-sm text-muted-foreground">
                      {sector.total_stocks}개
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center gap-1 text-xs">
                      <span className="text-green-600 font-semibold">{sector.buy_count}</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-gray-600">{sector.hold_count}</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-red-600 font-semibold">{sector.sell_count}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {sector.top_picks.slice(0, 3).map(pick => (
                        <span
                          key={pick.ticker}
                          className="text-xs bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded"
                          title={`${pick.change_percent > 0 ? '+' : ''}${pick.change_percent.toFixed(1)}%`}
                        >
                          {pick.ticker}
                        </span>
                      ))}
                      {sector.top_picks.length === 0 && (
                        <span className="text-xs text-muted-foreground">-</span>
                      )}
                    </div>
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
