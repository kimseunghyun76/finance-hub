'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { holdingApi, stockApi, type Holding, StockSearchResult } from '@/lib/api'
import { StockSearchInput } from '@/components/stock-search-input'

interface HoldingDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  portfolioId: number
  holding?: Holding | null
  onSuccess: () => void
}

export function HoldingDialog({
  open,
  onOpenChange,
  portfolioId,
  holding,
  onSuccess,
}: HoldingDialogProps) {
  const [ticker, setTicker] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [market, setMarket] = useState<'KRX' | 'NYSE' | 'NASDAQ'>('NASDAQ')
  const [quantity, setQuantity] = useState('')
  const [avgPrice, setAvgPrice] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [fetchingInfo, setFetchingInfo] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isEdit = !!holding

  useEffect(() => {
    if (holding) {
      setTicker(holding.ticker)
      setCompanyName(holding.company_name || '')
      setMarket(holding.market)
      setQuantity(holding.quantity.toString())
      setAvgPrice(holding.avg_price.toString())
      setPurchaseDate(holding.purchase_date)
    } else {
      setTicker('')
      setCompanyName('')
      setMarket('NASDAQ')
      setQuantity('')
      setAvgPrice('')
      setPurchaseDate(new Date().toISOString().split('T')[0])
    }
    setError(null)
  }, [holding, open])

  const handleStockSelect = (stock: StockSearchResult) => {
    setTicker(stock.ticker)
    setCompanyName(stock.name)

    // Auto-detect market
    if (stock.market === 'KRX') {
      setMarket('KRX')
    } else if (stock.market.includes('NYSE')) {
      setMarket('NYSE')
    } else {
      setMarket('NASDAQ')
    }
  }

  const handleTickerBlur = async () => {
    if (!ticker || isEdit || fetchingInfo) return

    setFetchingInfo(true)
    try {
      const response = await stockApi.getInfo(ticker)
      setCompanyName(response.data.name)

      // Auto-detect market
      if (ticker.includes('.KS') || ticker.includes('.KQ')) {
        setMarket('KRX')
      } else {
        setMarket('NASDAQ')
      }
    } catch (err) {
      console.log('종목 정보를 가져올 수 없습니다.')
    } finally {
      setFetchingInfo(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const data = {
        portfolio_id: portfolioId,
        ticker: ticker.toUpperCase(),
        company_name: companyName,
        market,
        quantity: parseFloat(quantity),
        avg_price: parseFloat(avgPrice),
        purchase_date: purchaseDate,
      }

      if (isEdit && holding) {
        await holdingApi.update(holding.id, {
          quantity: data.quantity,
          avg_price: data.avg_price,
          purchase_date: data.purchase_date,
        })
      } else {
        await holdingApi.create(data)
      }

      onSuccess()
      onOpenChange(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || '오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {isEdit ? '종목 수정' : '종목 추가'}
            </DialogTitle>
            <DialogDescription>
              {isEdit
                ? '보유 수량 및 평단가를 수정하세요.'
                : '포트폴리오에 새 종목을 추가하세요.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {!isEdit && (
              <div className="space-y-2">
                <Label>종목 검색 *</Label>
                <StockSearchInput
                  onSelect={handleStockSelect}
                  placeholder="티커 또는 종목명으로 검색 (예: AAPL, 삼성전자)"
                />
                {ticker && (
                  <div className="text-sm text-green-600 dark:text-green-400">
                    ✓ {companyName} ({ticker}) 선택됨
                  </div>
                )}
              </div>
            )}

            {isEdit && (
              <div className="space-y-2">
                <Label htmlFor="ticker">티커 심볼</Label>
                <Input
                  id="ticker"
                  value={ticker}
                  disabled
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="companyName">회사명</Label>
              <Input
                id="companyName"
                placeholder="자동으로 가져옵니다..."
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                disabled={fetchingInfo || isEdit}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="market">시장 *</Label>
              <Select
                id="market"
                value={market}
                onChange={(e) =>
                  setMarket(e.target.value as 'KRX' | 'NYSE' | 'NASDAQ')
                }
                disabled={isEdit}
              >
                <option value="NASDAQ">NASDAQ (미국)</option>
                <option value="NYSE">NYSE (미국)</option>
                <option value="KRX">KRX (한국)</option>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quantity">보유 수량 *</Label>
                <Input
                  id="quantity"
                  type="number"
                  step="0.01"
                  placeholder="10"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="avgPrice">평단가 *</Label>
                <Input
                  id="avgPrice"
                  type="number"
                  step="0.01"
                  placeholder="150.00"
                  value={avgPrice}
                  onChange={(e) => setAvgPrice(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="purchaseDate">매수일 *</Label>
              <Input
                id="purchaseDate"
                type="date"
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="text-sm text-destructive">{error}</div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              취소
            </Button>
            <Button
              type="submit"
              disabled={loading || !ticker || !quantity || !avgPrice}
            >
              {loading ? '저장 중...' : isEdit ? '수정' : '추가'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
