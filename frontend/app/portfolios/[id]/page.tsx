'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  portfolioApi,
  holdingApi,
  type PortfolioWithHoldings,
  type HoldingWithPrice,
} from '@/lib/api'
import { formatCurrency, formatPercent, formatDate } from '@/lib/utils'
import { HoldingDialog } from '@/components/holding-dialog'
import { PortfolioEditDialog } from '@/components/portfolio-edit-dialog'
import { PortfolioChart } from '@/components/portfolio-chart'
import { PortfolioInsightsCard } from '@/components/portfolio-insights-card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/ui/toast'

export default function PortfolioDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { addToast } = useToast()
  const portfolioId = parseInt(params.id as string)

  const [portfolio, setPortfolio] = useState<PortfolioWithHoldings | null>(null)
  const [holdingsWithPrice, setHoldingsWithPrice] = useState<HoldingWithPrice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showHoldingDialog, setShowHoldingDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)

  useEffect(() => {
    loadPortfolio()
  }, [portfolioId])

  const loadPortfolio = async () => {
    try {
      setLoading(true)
      const response = await portfolioApi.getById(portfolioId)
      setPortfolio(response.data)

      // Load current prices for all holdings
      const holdingsWithPrices = await Promise.all(
        response.data.holdings.map(async (holding) => {
          try {
            const priceResponse = await holdingApi.getWithPrice(holding.id)
            return priceResponse.data
          } catch {
            return {
              ...holding,
              current_price: null,
              total_value: null,
              total_cost: null,
              profit_loss: null,
              profit_loss_percent: null,
            } as HoldingWithPrice
          }
        })
      )

      setHoldingsWithPrice(holdingsWithPrices)
      setError(null)
    } catch (err) {
      setError('포트폴리오를 불러오는 중 오류가 발생했습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const calculateTotals = () => {
    const byCurrency: Record<string, { cost: number; value: number }> = {}

    holdingsWithPrice.forEach((holding) => {
      const currency = holding.market === 'KRX' ? 'KRW' : 'USD'
      if (!byCurrency[currency]) {
        byCurrency[currency] = { cost: 0, value: 0 }
      }
      if (holding.total_cost) byCurrency[currency].cost += holding.total_cost
      if (holding.total_value) byCurrency[currency].value += holding.total_value
    })

    return byCurrency
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <Skeleton className="h-4 w-32 mb-2" />
            <Skeleton className="h-9 w-48 mb-1" />
            <Skeleton className="h-5 w-64" />
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          {/* Summary Skeleton */}
          <div className="mb-8">
            <Skeleton className="h-6 w-32 mb-4" />
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="p-6 border rounded-lg bg-card">
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-8 w-32" />
                </div>
              ))}
            </div>
          </div>

          {/* Table Skeleton */}
          <div className="border rounded-lg bg-card">
            <div className="p-6 border-b flex items-center justify-between">
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-10 w-24" />
            </div>
            <div className="p-6 space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error || !portfolio) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-destructive">{error || '포트폴리오를 찾을 수 없습니다.'}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
          >
            대시보드로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  const totals = calculateTotals()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-sm text-muted-foreground hover:text-foreground mb-2"
          >
            ← 대시보드로 돌아가기
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold">{portfolio.name}</h1>
              {portfolio.description && (
                <p className="text-muted-foreground mt-1">{portfolio.description}</p>
              )}
            </div>
            <Button
              variant="outline"
              onClick={() => setShowEditDialog(true)}
            >
              포트폴리오 수정
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Portfolio 2.0 Insights */}
        {holdingsWithPrice.length > 0 && (
          <div className="mb-8">
            <PortfolioInsightsCard portfolioId={portfolioId} />
          </div>
        )}

        {/* Summary by Currency */}
        {Object.entries(totals).map(([currency, data]) => {
          const profitLoss = data.value - data.cost
          const profitLossPercent = data.cost > 0 ? (profitLoss / data.cost) * 100 : 0
          const currencyHoldings = holdingsWithPrice.filter(
            (h) => (h.market === 'KRX' ? 'KRW' : 'USD') === currency
          )

          return (
            <div key={currency} className="mb-8">
              <h2 className="text-xl font-bold mb-4">
                {currency === 'KRW' ? '🇰🇷 한국 주식' : '🇺🇸 미국 주식'}
              </h2>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-6">
                <div className="p-4 md:p-6 border rounded-lg bg-card">
                  <h3 className="text-xs md:text-sm font-medium text-muted-foreground">총 투자금</h3>
                  <p className="text-lg md:text-2xl font-bold mt-1 md:mt-2">
                    {formatCurrency(data.cost, currency as 'USD' | 'KRW')}
                  </p>
                </div>

                <div className="p-4 md:p-6 border rounded-lg bg-card">
                  <h3 className="text-xs md:text-sm font-medium text-muted-foreground">평가액</h3>
                  <p className="text-lg md:text-2xl font-bold mt-1 md:mt-2">
                    {formatCurrency(data.value, currency as 'USD' | 'KRW')}
                  </p>
                </div>

                <div className="p-4 md:p-6 border rounded-lg bg-card">
                  <h3 className="text-xs md:text-sm font-medium text-muted-foreground">평가손익</h3>
                  <p
                    className={`text-lg md:text-2xl font-bold mt-1 md:mt-2 ${
                      profitLoss >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {formatCurrency(profitLoss, currency as 'USD' | 'KRW')}
                  </p>
                </div>

                <div className="p-4 md:p-6 border rounded-lg bg-card">
                  <h3 className="text-xs md:text-sm font-medium text-muted-foreground">수익률</h3>
                  <p
                    className={`text-lg md:text-2xl font-bold mt-1 md:mt-2 ${
                      profitLossPercent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {formatPercent(profitLossPercent)}
                  </p>
                </div>
              </div>

              {/* Portfolio Composition Chart */}
              {currencyHoldings.length > 0 && (
                <div className="border rounded-lg p-6 bg-card mb-6">
                  <h3 className="text-lg font-bold mb-4">포트폴리오 구성</h3>
                  <PortfolioChart
                    holdings={currencyHoldings}
                    currency={currency as 'USD' | 'KRW'}
                  />
                </div>
              )}
            </div>
          )
        })}

        {/* Holdings Table */}
        <div className="border rounded-lg bg-card">
          <div className="p-6 border-b flex items-center justify-between">
            <h2 className="text-xl font-bold">보유 종목</h2>
            <Button onClick={() => setShowHoldingDialog(true)}>
              + 종목 추가
            </Button>
          </div>

          {holdingsWithPrice.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-muted-foreground mb-4">보유 종목이 없습니다.</p>
              <Button onClick={() => setShowHoldingDialog(true)}>
                첫 종목 추가하기
              </Button>
            </div>
          ) : (
            <>
              {/* Desktop Table View */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-medium">종목</th>
                      <th className="px-6 py-3 text-right text-sm font-medium">보유량</th>
                      <th className="px-6 py-3 text-right text-sm font-medium">평단가</th>
                      <th className="px-6 py-3 text-right text-sm font-medium">현재가</th>
                      <th className="px-6 py-3 text-right text-sm font-medium">평가액</th>
                      <th className="px-6 py-3 text-right text-sm font-medium">손익</th>
                      <th className="px-6 py-3 text-right text-sm font-medium">수익률</th>
                    </tr>
                  </thead>
                  <tbody>
                    {holdingsWithPrice.map((holding) => (
                      <tr
                        key={holding.id}
                        className="border-b hover:bg-muted/50 cursor-pointer"
                        onClick={() => router.push(`/stocks/${holding.ticker}`)}
                      >
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium hover:text-primary">
                              {holding.ticker}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {holding.company_name || 'Unknown'}
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">{holding.quantity}</td>
                        <td className="px-6 py-4 text-right">
                          {formatCurrency(
                            holding.avg_price,
                            holding.market === 'KRX' ? 'KRW' : 'USD'
                          )}
                        </td>
                        <td className="px-6 py-4 text-right">
                          {holding.current_price
                            ? formatCurrency(
                                holding.current_price,
                                holding.market === 'KRX' ? 'KRW' : 'USD'
                              )
                            : '-'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          {holding.total_value
                            ? formatCurrency(
                                holding.total_value,
                                holding.market === 'KRX' ? 'KRW' : 'USD'
                              )
                            : '-'}
                        </td>
                        <td
                          className={`px-6 py-4 text-right font-medium ${
                            (holding.profit_loss || 0) >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {holding.profit_loss
                            ? formatCurrency(
                                holding.profit_loss,
                                holding.market === 'KRX' ? 'KRW' : 'USD'
                              )
                            : '-'}
                        </td>
                        <td
                          className={`px-6 py-4 text-right font-medium ${
                            (holding.profit_loss_percent || 0) >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {holding.profit_loss_percent
                            ? formatPercent(holding.profit_loss_percent)
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Card View */}
              <div className="md:hidden divide-y">
                {holdingsWithPrice.map((holding) => (
                  <div
                    key={holding.id}
                    className="p-4 hover:bg-muted/50 cursor-pointer active:bg-muted"
                    onClick={() => router.push(`/stocks/${holding.ticker}`)}
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-bold text-lg">{holding.ticker}</p>
                        <p className="text-sm text-muted-foreground">
                          {holding.company_name || 'Unknown'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p
                          className={`font-bold text-lg ${
                            (holding.profit_loss_percent || 0) >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {holding.profit_loss_percent
                            ? formatPercent(holding.profit_loss_percent)
                            : '-'}
                        </p>
                        <p
                          className={`text-sm ${
                            (holding.profit_loss || 0) >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {holding.profit_loss
                            ? formatCurrency(
                                holding.profit_loss,
                                holding.market === 'KRX' ? 'KRW' : 'USD'
                              )
                            : '-'}
                        </p>
                      </div>
                    </div>

                    {/* Details Grid */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-muted-foreground">보유량</p>
                        <p className="font-medium">{holding.quantity}주</p>
                      </div>
                      <div className="text-right">
                        <p className="text-muted-foreground">평가액</p>
                        <p className="font-medium">
                          {holding.total_value
                            ? formatCurrency(
                                holding.total_value,
                                holding.market === 'KRX' ? 'KRW' : 'USD'
                              )
                            : '-'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">평단가</p>
                        <p className="font-medium">
                          {formatCurrency(
                            holding.avg_price,
                            holding.market === 'KRX' ? 'KRW' : 'USD'
                          )}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-muted-foreground">현재가</p>
                        <p className="font-medium">
                          {holding.current_price
                            ? formatCurrency(
                                holding.current_price,
                                holding.market === 'KRX' ? 'KRW' : 'USD'
                              )
                            : '-'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </main>

      {/* Holding Dialog */}
      <HoldingDialog
        open={showHoldingDialog}
        onOpenChange={setShowHoldingDialog}
        portfolioId={portfolioId}
        onSuccess={loadPortfolio}
      />

      {/* Portfolio Edit Dialog */}
      <PortfolioEditDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        portfolio={portfolio}
        onSuccess={() => {
          loadPortfolio()
          addToast('success', '포트폴리오가 업데이트되었습니다')
        }}
      />
    </div>
  )
}
