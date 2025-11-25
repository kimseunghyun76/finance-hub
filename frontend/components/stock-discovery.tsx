"use client"

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Search, TrendingUp, AlertCircle, Zap, Trash2 } from 'lucide-react'
import { LoadingProgress } from './loading-progress'
import { getStockName } from '@/lib/stock-names'

interface StockCandidate {
  ticker: string
  name: string
  sector: string
  market_cap: number
  current_price: number
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  reason: string
  signals: string[]
}

interface DiscoveryData {
  trained_count: number
  untrained_count: number
  recommendations: StockCandidate[]
  signals: {
    volume_spikes: number
    price_movements: number
    high_priority: number
  }
}

export function StockDiscovery() {
  const router = useRouter()
  const [data, setData] = useState<DiscoveryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedMarket, setSelectedMarket] = useState<'ALL' | 'US' | 'KR'>('ALL')
  const [selectedPriority, setSelectedPriority] = useState<'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'>('HIGH') // 기본값: HIGH (중간/높은 우선순위)
  const [trainingTicker, setTrainingTicker] = useState<string | null>(null)
  const [deletingTicker, setDeletingTicker] = useState<string | null>(null)
  const [deletingAll, setDeletingAll] = useState(false)
  const [discovering, setDiscovering] = useState(false)

  useEffect(() => {
    loadCandidates()
  }, [selectedMarket])

  const loadCandidates = async (forceRefresh: boolean = false) => {
    try {
      setLoading(true)
      const response = await fetch(
        `http://localhost:8001/api/v1/predictions/discover/candidates?market=${selectedMarket}&check_signals=true&force_refresh=${forceRefresh}`
      )
      if (!response.ok) throw new Error('Failed to load')
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Error loading candidates:', error)
    } finally {
      setLoading(false)
    }
  }

  const trainModel = async (ticker: string) => {
    try {
      setTrainingTicker(ticker)
      const response = await fetch(
        `http://localhost:8001/api/v1/predictions/train/${ticker}`,
        { method: 'POST' }
      )

      if (response.ok) {
        alert(`${ticker} 모델 훈련이 시작되었습니다!`)
        // Reload after a delay
        setTimeout(() => {
          loadCandidates()
          setTrainingTicker(null)
        }, 2000)
      } else {
        alert('훈련 시작에 실패했습니다')
        setTrainingTicker(null)
      }
    } catch (error) {
      console.error('Failed to train model:', error)
      alert('훈련 시작에 실패했습니다')
      setTrainingTicker(null)
    }
  }

  const deleteCandidate = async (ticker: string) => {
    if (!confirm(`${ticker} 종목을 발굴 목록에서 제외하시겠습니까?`)) {
      return
    }

    try {
      setDeletingTicker(ticker)

      // Call backend API to exclude the ticker
      const response = await fetch(
        `http://localhost:8001/api/v1/predictions/discover/exclude/${ticker}`,
        { method: 'POST' }
      )

      if (response.ok) {
        // Filter out the ticker from the current data
        if (data) {
          setData({
            ...data,
            recommendations: data.recommendations.filter(r => r.ticker !== ticker),
            untrained_count: data.untrained_count - 1
          })
        }
        setDeletingTicker(null)
        alert(`${ticker} 종목이 목록에서 영구적으로 제외되었습니다`)
      } else {
        throw new Error('Failed to exclude ticker')
      }
    } catch (error) {
      console.error('Failed to delete candidate:', error)
      alert('삭제에 실패했습니다')
      setDeletingTicker(null)
    }
  }

  const deleteAllCandidates = async () => {
    if (!confirm(`현재 표시된 모든 종목을 발굴 목록에서 제외하시겠습니까?`)) {
      return
    }

    try {
      setDeletingAll(true)
      const response = await fetch(
        `http://localhost:8001/api/v1/predictions/discover/exclude-all?market=${selectedMarket}`,
        { method: 'POST' }
      )

      if (response.ok) {
        const result = await response.json()
        setData({
          ...data!,
          recommendations: [],
          untrained_count: 0
        })
        alert(`${result.excluded_count}개 종목이 목록에서 영구적으로 제외되었습니다`)
      } else {
        throw new Error('Failed to exclude all tickers')
      }
    } catch (error) {
      console.error('Failed to delete all candidates:', error)
      alert('전체 삭제에 실패했습니다')
    } finally {
      setDeletingAll(false)
    }
  }

  const discoverNew = async () => {
    try {
      setDiscovering(true)
      await loadCandidates(true) // force_refresh=true로 캐시 무시하고 재실행
      alert('신규 종목 발굴이 완료되었습니다!')
    } catch (error) {
      console.error('Failed to discover new candidates:', error)
      alert('신규 발굴에 실패했습니다')
    } finally {
      setDiscovering(false)
    }
  }

  const getPriorityBadge = (priority: string) => {
    const badges = {
      'HIGH': { color: 'bg-red-600', text: '높음', icon: AlertCircle },
      'MEDIUM': { color: 'bg-orange-500', text: '중간', icon: Zap },
      'LOW': { color: 'bg-blue-500', text: '낮음', icon: Search }
    }
    const badge = badges[priority as keyof typeof badges]
    const Icon = badge.icon

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 ${badge.color} text-white text-xs font-semibold rounded`}>
        <Icon className="w-3 h-3" />
        {badge.text}
      </span>
    )
  }

  const formatMarketCap = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
    return `$${value.toFixed(0)}`
  }

  if (loading) {
    return <LoadingProgress message="종목 데이터를 분석하는 중..." estimatedSeconds={15} />
  }

  if (!data) {
    return (
      <div className="p-6 border rounded-lg bg-card text-center text-muted-foreground">
        종목 발굴 데이터를 불러올 수 없습니다
      </div>
    )
  }

  const filteredRecommendations = selectedPriority === 'ALL'
    ? data.recommendations.filter(r => r.priority === 'HIGH' || r.priority === 'MEDIUM') // LOW 우선순위 제외
    : data.recommendations.filter(r => r.priority === selectedPriority)

  return (
    <div className="space-y-6">
      {/* Header & Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">훈련된 종목</p>
          <p className="text-2xl font-bold mt-1">{data.trained_count}개</p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">미훈련 종목</p>
          <p className="text-2xl font-bold mt-1 text-orange-600">{data.untrained_count}개</p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">거래량 급증</p>
          <p className="text-2xl font-bold mt-1 text-green-600">{data.signals.volume_spikes}개</p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">가격 급변</p>
          <p className="text-2xl font-bold mt-1 text-blue-600">{data.signals.price_movements}개</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex gap-2">
          <span className="text-sm font-medium text-muted-foreground">시장:</span>
          {['ALL', 'US', 'KR'].map(market => (
            <button
              key={market}
              onClick={() => setSelectedMarket(market as any)}
              disabled={trainingTicker !== null}
              className={`px-3 py-1 text-sm rounded transition-opacity ${
                selectedMarket === market
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-gray-100 hover:bg-gray-200'
              } ${trainingTicker !== null ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {market === 'ALL' ? '전체' : market === 'US' ? '🇺🇸 미국' : '🇰🇷 한국'}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <span className="text-sm font-medium text-muted-foreground">우선순위:</span>
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(priority => (
            <button
              key={priority}
              onClick={() => setSelectedPriority(priority as any)}
              disabled={trainingTicker !== null}
              className={`px-3 py-1 text-sm rounded transition-opacity ${
                selectedPriority === priority
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-gray-100 hover:bg-gray-200'
              } ${trainingTicker !== null ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {priority === 'ALL' ? '전체' : priority === 'HIGH' ? '높음' : priority === 'MEDIUM' ? '중간' : '낮음'}
            </button>
          ))}
        </div>

        <div className="flex gap-2 ml-auto">
          <Button
            onClick={discoverNew}
            disabled={discovering || trainingTicker !== null || deletingTicker !== null}
            className={discovering ? 'animate-pulse' : ''}
          >
            <Search className="w-4 h-4 mr-2" />
            {discovering ? '발굴 중...' : '신규 발굴'}
          </Button>
          <Button
            variant="destructive"
            onClick={deleteAllCandidates}
            disabled={deletingAll || trainingTicker !== null || deletingTicker !== null || filteredRecommendations.length === 0}
            className={deletingAll ? 'animate-pulse' : ''}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            {deletingAll ? '삭제 중...' : '전체 삭제'}
          </Button>
        </div>
      </div>

      {/* Recommendations Table */}
      <div className="border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">우선순위</th>
                <th className="px-4 py-3 text-left text-sm font-medium">티커</th>
                <th className="px-4 py-3 text-left text-sm font-medium">회사명</th>
                <th className="px-4 py-3 text-left text-sm font-medium">섹터</th>
                <th className="px-4 py-3 text-right text-sm font-medium">시가총액</th>
                <th className="px-4 py-3 text-right text-sm font-medium">현재가</th>
                <th className="px-4 py-3 text-left text-sm font-medium">추천 이유</th>
                <th className="px-4 py-3 text-center text-sm font-medium">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredRecommendations.map((stock) => (
                <tr key={stock.ticker} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3">
                    {getPriorityBadge(stock.priority)}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => router.push(`/stocks/${stock.ticker}`)}
                      className="font-mono font-semibold hover:text-primary transition-colors"
                    >
                      {stock.ticker}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm">{stock.name}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-muted-foreground">{stock.sector}</span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-medium">{formatMarketCap(stock.market_cap)}</span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm">${stock.current_price?.toFixed(2) || 'N/A'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-muted-foreground">{stock.reason}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <Button
                        size="sm"
                        onClick={() => trainModel(stock.ticker)}
                        disabled={trainingTicker !== null || deletingTicker !== null}
                        className={trainingTicker === stock.ticker ? 'animate-pulse' : ''}
                      >
                        {trainingTicker === stock.ticker ? '훈련 중...' : '훈련'}
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteCandidate(stock.ticker)}
                        disabled={trainingTicker !== null || deletingTicker !== null}
                        className={deletingTicker === stock.ticker ? 'animate-pulse' : ''}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredRecommendations.length === 0 && (
        <div className="p-12 text-center text-muted-foreground">
          선택한 필터에 해당하는 추천 종목이 없습니다
        </div>
      )}
    </div>
  )
}
