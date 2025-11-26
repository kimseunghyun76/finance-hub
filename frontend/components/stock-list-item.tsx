'use client'

import { ChevronRight, RefreshCw } from 'lucide-react'
import { formatElapsedTime } from '@/lib/utils'
import { BuffettInsight } from './buffett-insight'

interface PredictionData {
  action: 'BUY' | 'SELL' | 'HOLD'
  prediction?: {
    change_percent?: number
    confidence?: number
  }
}

interface StockListItemProps {
  ticker: string
  name: string
  trained: boolean
  lastTrained?: string | null
  selected: boolean
  prediction?: PredictionData | null
  onClick: () => void
  onTrain: (e: React.MouseEvent) => void
}

export function StockListItem({
  ticker,
  name,
  trained,
  lastTrained,
  selected,
  prediction,
  onClick,
  onTrain
}: StockListItemProps) {
  return (
    <div
      className={`border-b last:border-b-0 ${
        selected ? 'bg-primary/10 border-l-4 border-l-primary' : ''
      }`}
    >
      <button
        onClick={onClick}
        className="w-full px-4 py-3 text-left hover:bg-accent transition-colors"
      >
        <div className="flex items-center justify-between mb-1">
          <p className="font-bold">{name}</p>
          <ChevronRight className={`w-4 h-4 transition-transform ${
            selected ? 'rotate-90' : ''
          }`} />
        </div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs text-muted-foreground font-mono">{ticker}</span>
          {trained && (
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          )}
        </div>

        {trained && (
          <div className="space-y-2 mt-2">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-muted-foreground">
                🕐 {formatElapsedTime(lastTrained)}
              </span>
              {prediction && (
                <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                  prediction.action === 'BUY' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200' :
                  prediction.action === 'SELL' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200' :
                  'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200'
                }`}>
                  {prediction.action === 'BUY' && '💰 매수'}
                  {prediction.action === 'SELL' && '📉 매도'}
                  {prediction.action === 'HOLD' && '⏸️ 보유'}
                </span>
              )}
            </div>
            {prediction && (
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs text-muted-foreground">
                  변동률: <span className={`font-semibold ${
                    (prediction.prediction?.change_percent || 0) > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {(prediction.prediction?.change_percent || 0) > 0 && '+'}
                    {(prediction.prediction?.change_percent || 0).toFixed(2)}%
                  </span>
                </span>
                <span className="text-xs text-muted-foreground">
                  확신도: <span className="font-semibold text-primary">
                    {((prediction.prediction?.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </span>
              </div>
            )}
            {prediction && (
              <div className="mt-2">
                <BuffettInsight
                  ticker={ticker}
                  prediction={prediction}
                  compact={true}
                />
              </div>
            )}
          </div>
        )}
      </button>

      <div className="px-4 pb-2">
        <button
          onClick={onTrain}
          className="text-xs px-3 py-1 rounded bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 transition-colors flex items-center gap-1"
        >
          <RefreshCw className="w-3 h-3" />
          {trained ? '재훈련' : '훈련'}
        </button>
      </div>
    </div>
  )
}
