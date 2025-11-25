'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { portfolioApi, holdingApi, stockApi, type PortfolioWithHoldings } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import { PortfolioDialog } from '@/components/portfolio-dialog'
import { PortfolioEditDialog } from '@/components/portfolio-edit-dialog'
import { HoldingDialog } from '@/components/holding-dialog'
import { HoldingCard } from '@/components/holding-card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/ui/toast'

interface PriceChange {
  value: number
  percent: number
}

interface EnrichedHolding {
  id: number
  portfolio_id: number
  ticker: string
  company_name?: string
  market: 'KRX' | 'NYSE' | 'NASDAQ'
  quantity: number
  avg_price: number
  current_price?: number
  profit_loss?: number
  profit_loss_percent?: number
  daily_change?: PriceChange
  weekly_change?: PriceChange
  monthly_change?: PriceChange
  prediction?: {
    action: 'BUY' | 'SELL' | 'HOLD'
    change_percent: number
    confidence: number
  }
}

interface PortfolioData extends PortfolioWithHoldings {
  enriched_holdings: EnrichedHolding[]
  total_value: number
  total_cost: number
  total_profit: number
  total_profit_percent: number
}

export default function DashboardPage() {
  const router = useRouter()
  const { addToast } = useToast()
  const [portfolios, setPortfolios] = useState<PortfolioData[]>([])
  const [predictions, setPredictions] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showDialog, setShowDialog] = useState(false)
  const [editingPortfolio, setEditingPortfolio] = useState<PortfolioWithHoldings | null>(null)
  const [showHoldingDialog, setShowHoldingDialog] = useState(false)
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null)
  const [editingHolding, setEditingHolding] = useState<any>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [portfoliosData, predictionsData] = await Promise.all([
        loadPortfolios(),
        loadPredictions()
      ])
      setPredictions(predictionsData)
      await enrichPortfoliosWithData(portfoliosData, predictionsData)
      setError(null)
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadPortfolios = async () => {
    const response = await portfolioApi.getAll()
    return Promise.all(
      response.data.map(p => portfolioApi.getById(p.id).then(r => r.data))
    )
  }

  const loadPredictions = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/predictions/summary')
      if (!response.ok) return {}
      const data = await response.json()
      return (data.predictions || []).reduce((acc: any, p: any) => {
        acc[p.ticker] = p
        return acc
      }, {})
    } catch {
      return {}
    }
  }

  const fetchPriceChanges = async (ticker: string, currentPrice: number) => {
    try {
      const historyResponse = await stockApi.getHistory(ticker, '1mo')
      const data = historyResponse.data?.data
      if (!data || data.length === 0) return {}

      const today = data[data.length - 1]
      const todayClose = currentPrice || today?.Close

      // Find prices for different periods
      const findPriceAtDaysAgo = (daysAgo: number) => {
        const targetIndex = data.length - 1 - daysAgo
        if (targetIndex >= 0 && data[targetIndex]) {
          return data[targetIndex].Close
        }
        return null
      }

      const yesterdayPrice = findPriceAtDaysAgo(1)
      const weekAgoPrice = findPriceAtDaysAgo(7) || (data.length >= 5 ? data[Math.max(0, data.length - 6)].Close : null)
      const monthAgoPrice = data[0]?.Close

      const calcChange = (oldPrice: number | null): PriceChange | undefined => {
        if (oldPrice === null || oldPrice === 0) return undefined
        const value = todayClose - oldPrice
        const percent = (value / oldPrice) * 100
        return { value, percent }
      }

      return {
        daily_change: calcChange(yesterdayPrice),
        weekly_change: calcChange(weekAgoPrice),
        monthly_change: calcChange(monthAgoPrice),
      }
    } catch (error) {
      console.error(`Failed to fetch history for ${ticker}:`, error)
      return {}
    }
  }

  const enrichPortfoliosWithData = async (portfoliosData: PortfolioWithHoldings[], predictionsData: Record<string, any>) => {
    const enriched = await Promise.all(
      portfoliosData.map(async (portfolio) => {
        const holdingsWithPrice = await Promise.all(
          portfolio.holdings.map(async (holding) => {
            try {
              const priceResponse = await holdingApi.getWithPrice(holding.id)
              const pred = predictionsData[holding.ticker]
              const currentPrice = priceResponse.data.current_price

              // Fetch price changes
              const priceChanges = currentPrice ? await fetchPriceChanges(holding.ticker, currentPrice) : {}

              return {
                ...priceResponse.data,
                ...priceChanges,
                prediction: pred ? {
                  action: pred.action,
                  change_percent: pred.change_percent,
                  confidence: pred.confidence
                } : undefined
              }
            } catch {
              return { ...holding, current_price: undefined, profit_loss: undefined, profit_loss_percent: undefined }
            }
          })
        )

        const totalValue = holdingsWithPrice.reduce((sum, h) => {
          const value = h.current_price ? h.current_price * h.quantity : h.avg_price * h.quantity
          return sum + value
        }, 0)

        const totalCost = holdingsWithPrice.reduce((sum, h) => sum + (h.avg_price * h.quantity), 0)
        const totalProfit = totalValue - totalCost
        const totalProfitPercent = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0

        return {
          ...portfolio,
          enriched_holdings: holdingsWithPrice,
          total_value: totalValue,
          total_cost: totalCost,
          total_profit: totalProfit,
          total_profit_percent: totalProfitPercent
        }
      })
    )

    setPortfolios(enriched)
  }

  const calculateTotals = () => {
    return portfolios.reduce((acc, p) => {
      const isKRW = p.enriched_holdings.some(h => h.market === 'KRX')
      return {
        usd_value: acc.usd_value + (isKRW ? 0 : p.total_value),
        usd_cost: acc.usd_cost + (isKRW ? 0 : p.total_cost),
        usd_profit: acc.usd_profit + (isKRW ? 0 : p.total_profit),
        krw_value: acc.krw_value + (isKRW ? p.total_value : 0),
        krw_cost: acc.krw_cost + (isKRW ? p.total_cost : 0),
        krw_profit: acc.krw_profit + (isKRW ? p.total_profit : 0)
      }
    }, { usd_value: 0, usd_cost: 0, usd_profit: 0, krw_value: 0, krw_cost: 0, krw_profit: 0 })
  }

  const handleAddHolding = (portfolioId: number) => {
    setSelectedPortfolioId(portfolioId)
    setEditingHolding(null)
    setShowHoldingDialog(true)
  }

  const handleEditHolding = (holding: any, portfolioId: number) => {
    setSelectedPortfolioId(portfolioId)
    setEditingHolding(holding)
    setShowHoldingDialog(true)
  }

  const handleDeleteHolding = async (holdingId: number) => {
    if (!confirm('정말 이 종목을 삭제하시겠습니까?')) return
    try {
      await holdingApi.delete(holdingId)
      addToast('success', '종목이 삭제되었습니다')
      loadData()
    } catch {
      addToast('error', '종목 삭제에 실패했습니다')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <Skeleton className="h-9 w-64 mb-2" />
            <Skeleton className="h-5 w-48" />
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="p-6 border rounded-lg">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-9 w-20" />
              </div>
            ))}
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-destructive">{error}</p>
          <Button onClick={loadData} className="mt-4">다시 시도</Button>
        </div>
      </div>
    )
  }

  const totals = calculateTotals()
  const usdProfitPercent = totals.usd_cost > 0 ? (totals.usd_profit / totals.usd_cost) * 100 : 0
  const krwProfitPercent = totals.krw_cost > 0 ? (totals.krw_profit / totals.krw_cost) * 100 : 0

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold">내 포트폴리오</h1>
          <p className="text-muted-foreground mt-1">실시간 자산 현황 및 AI 예측 분석</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">총 평가액</h3>
            <div className="mt-2">
              {totals.usd_value > 0 && <p className="text-2xl font-bold">{formatCurrency(totals.usd_value, 'USD')}</p>}
              {totals.krw_value > 0 && <p className={`${totals.usd_value > 0 ? 'text-xl mt-1' : 'text-2xl'} font-bold`}>{formatCurrency(totals.krw_value, 'KRW')}</p>}
              {totals.usd_value === 0 && totals.krw_value === 0 && <p className="text-3xl font-bold">-</p>}
            </div>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">총 투자금</h3>
            <div className="mt-2">
              {totals.usd_cost > 0 && <p className="text-2xl font-bold">{formatCurrency(totals.usd_cost, 'USD')}</p>}
              {totals.krw_cost > 0 && <p className={`${totals.usd_cost > 0 ? 'text-xl mt-1' : 'text-2xl'} font-bold`}>{formatCurrency(totals.krw_cost, 'KRW')}</p>}
              {totals.usd_cost === 0 && totals.krw_cost === 0 && <p className="text-3xl font-bold">-</p>}
            </div>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">총 수익</h3>
            <div className="mt-2">
              {totals.usd_cost > 0 && (
                <p className={`text-2xl font-bold ${totals.usd_profit > 0 ? 'text-green-600' : totals.usd_profit < 0 ? 'text-red-600' : ''}`}>
                  {totals.usd_profit > 0 && '+'}{formatCurrency(totals.usd_profit, 'USD')}
                </p>
              )}
              {totals.krw_cost > 0 && (
                <p className={`${totals.usd_cost > 0 ? 'text-xl mt-1' : 'text-2xl'} font-bold ${totals.krw_profit > 0 ? 'text-green-600' : totals.krw_profit < 0 ? 'text-red-600' : ''}`}>
                  {totals.krw_profit > 0 && '+'}{formatCurrency(totals.krw_profit, 'KRW')}
                </p>
              )}
              {totals.usd_cost === 0 && totals.krw_cost === 0 && <p className="text-3xl font-bold">-</p>}
            </div>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">수익률</h3>
            <div className="mt-2">
              {totals.usd_cost > 0 && (
                <p className={`text-2xl font-bold ${totals.usd_profit > 0 ? 'text-green-600' : totals.usd_profit < 0 ? 'text-red-600' : ''}`}>
                  {usdProfitPercent > 0 && '+'}{usdProfitPercent.toFixed(2)}%
                </p>
              )}
              {totals.krw_cost > 0 && (
                <p className={`${totals.usd_cost > 0 ? 'text-xl mt-1' : 'text-2xl'} font-bold ${totals.krw_profit > 0 ? 'text-green-600' : totals.krw_profit < 0 ? 'text-red-600' : ''}`}>
                  {krwProfitPercent > 0 && '+'}{krwProfitPercent.toFixed(2)}%
                </p>
              )}
              {totals.usd_cost === 0 && totals.krw_cost === 0 && <p className="text-3xl font-bold">-</p>}
            </div>
          </div>
        </div>

        {/* Portfolios */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">포트폴리오 목록</h2>
            <Button onClick={() => setShowDialog(true)}>+ 새 포트폴리오</Button>
          </div>

          {portfolios.length === 0 ? (
            <div className="text-center py-12 border rounded-lg">
              <p className="text-muted-foreground mb-4">아직 포트폴리오가 없습니다.</p>
              <Button onClick={() => setShowDialog(true)}>첫 포트폴리오 만들기</Button>
            </div>
          ) : (
            portfolios.map((portfolio) => (
              <div key={portfolio.id} className="border rounded-lg p-6 bg-card">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex-1">
                    <button
                      onClick={() => router.push(`/portfolios/${portfolio.id}`)}
                      className="text-xl font-semibold hover:text-primary transition-colors"
                    >
                      {portfolio.name}
                    </button>
                    {portfolio.description && (
                      <p className="text-sm text-muted-foreground mt-1">{portfolio.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      {(() => {
                        const currency = portfolio.enriched_holdings.some(h => h.market === 'KRX') ? 'KRW' : 'USD'
                        return (
                          <>
                            <p className="text-lg font-bold">{formatCurrency(portfolio.total_value, currency)}</p>
                            <p className={`text-sm font-medium ${
                              portfolio.total_profit > 0 ? 'text-green-600' :
                              portfolio.total_profit < 0 ? 'text-red-600' : 'text-muted-foreground'
                            }`}>
                              {portfolio.total_profit > 0 && '+'}{formatCurrency(portfolio.total_profit, currency)}
                              ({portfolio.total_profit > 0 && '+'}{portfolio.total_profit_percent.toFixed(2)}%)
                            </p>
                          </>
                        )
                      })()}
                    </div>
                    <Button variant="outline" size="sm" onClick={() => setEditingPortfolio(portfolio)}>
                      수정
                    </Button>
                  </div>
                </div>

                {/* Holdings */}
                <div className="space-y-2">
                  {portfolio.enriched_holdings.length === 0 ? (
                    <p className="text-muted-foreground text-sm">보유 종목이 없습니다.</p>
                  ) : (
                    portfolio.enriched_holdings.map((holding) => (
                      <HoldingCard
                        key={holding.id}
                        holding={holding}
                        prediction={holding.prediction}
                        onEdit={() => handleEditHolding(holding, portfolio.id)}
                        onDelete={() => handleDeleteHolding(holding.id)}
                      />
                    ))
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleAddHolding(portfolio.id)}
                    className="w-full"
                  >
                    + 주식 추가
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* Dialogs */}
      <PortfolioDialog open={showDialog} onOpenChange={setShowDialog} onSuccess={loadData} />
      <PortfolioEditDialog
        open={!!editingPortfolio}
        onOpenChange={(open) => !open && setEditingPortfolio(null)}
        portfolio={editingPortfolio}
        onSuccess={() => {
          loadData()
          addToast('success', '포트폴리오가 업데이트되었습니다')
        }}
      />
      {selectedPortfolioId && (
        <HoldingDialog
          open={showHoldingDialog}
          onOpenChange={(open) => {
            setShowHoldingDialog(open)
            if (!open) {
              setEditingHolding(null)
              setSelectedPortfolioId(null)
            }
          }}
          portfolioId={selectedPortfolioId}
          holding={editingHolding}
          onSuccess={() => {
            loadData()
            addToast('success', editingHolding ? '종목이 수정되었습니다' : '종목이 추가되었습니다')
          }}
        />
      )}
    </div>
  )
}
