"use client"

import { useRouter } from 'next/navigation'
import { formatCurrency } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface HoldingCardProps {
  holding: {
    id: number
    ticker: string
    company_name?: string
    quantity: number
    avg_price: number
    market: 'KRX' | 'NYSE' | 'NASDAQ'
    current_price?: number
    profit_loss?: number
    profit_loss_percent?: number
  }
  prediction?: {
    action: 'BUY' | 'SELL' | 'HOLD'
    change_percent: number
    confidence: number
  }
  onEdit: () => void
  onDelete: () => void
}

export function HoldingCard({ holding, prediction, onEdit, onDelete }: HoldingCardProps) {
  const router = useRouter()
  const currency = holding.market === 'KRX' ? 'KRW' : 'USD'
  const hasPrice = holding.current_price !== undefined
  const isProfit = (holding.profit_loss || 0) > 0
  const isLoss = (holding.profit_loss || 0) < 0

  const getPredictionColor = () => {
    if (!prediction) return 'text-gray-500'
    return prediction.action === 'BUY' ? 'text-green-600' :
           prediction.action === 'SELL' ? 'text-red-600' : 'text-gray-600'
  }

  const getPredictionIcon = () => {
    if (!prediction) return <Minus className="w-4 h-4" />
    return prediction.action === 'BUY' ? <TrendingUp className="w-4 h-4" /> :
           prediction.action === 'SELL' ? <TrendingDown className="w-4 h-4" /> :
           <Minus className="w-4 h-4" />
  }

  return (
    <div className="p-4 border rounded-lg hover:bg-accent/50 hover:border-primary transition-colors">
      <div className="flex items-start justify-between gap-4">
        {/* Left: Stock Info */}
        <button
          onClick={() => router.push(`/stocks/${holding.ticker}`)}
          className="flex-1 text-left min-w-0"
        >
          <p className="font-semibold text-lg">{holding.ticker}</p>
          <p className="text-sm text-muted-foreground truncate">
            {holding.company_name || 'Unknown'}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {holding.quantity}주 × {formatCurrency(holding.avg_price, currency)}
          </p>
        </button>

        {/* Center: Price & P/L */}
        <div className="text-right">
          {hasPrice ? (
            <>
              <p className="font-semibold">{formatCurrency(holding.current_price!, currency)}</p>
              <p className={`text-sm font-medium ${isProfit ? 'text-green-600' : isLoss ? 'text-red-600' : 'text-muted-foreground'}`}>
                {isProfit && '+'}{formatCurrency(holding.profit_loss || 0, currency)}
              </p>
              <p className={`text-xs ${isProfit ? 'text-green-600' : isLoss ? 'text-red-600' : 'text-muted-foreground'}`}>
                {isProfit && '+'}{(holding.profit_loss_percent || 0).toFixed(2)}%
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">가격 정보 없음</p>
          )}
        </div>

        {/* Right: AI Prediction */}
        {prediction && (
          <div className={`text-center px-3 py-2 rounded-lg bg-accent ${getPredictionColor()}`}>
            <div className="flex items-center gap-1 mb-1">
              {getPredictionIcon()}
              <span className="text-xs font-semibold">{prediction.action}</span>
            </div>
            <p className="text-xs">
              {prediction.change_percent > 0 && '+'}{prediction.change_percent.toFixed(1)}%
            </p>
            <p className="text-xs opacity-75">{(prediction.confidence * 100).toFixed(0)}%</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-1">
          <Button size="sm" variant="outline" onClick={onEdit}>수정</Button>
          <Button size="sm" variant="destructive" onClick={onDelete}>삭제</Button>
        </div>
      </div>
    </div>
  )
}
