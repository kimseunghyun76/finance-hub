'use client'

import { useState } from 'react'
import StockTreemap from '@/components/stock-treemap'

export default function PredictionMapPage() {
  const [actionFilter, setActionFilter] = useState<'ALL' | 'BUY' | 'SELL' | 'HOLD'>('ALL')

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">🗺️ AI 예측 맵</h1>
          <p className="text-lg text-muted-foreground">
            한눈에 보는 AI 매매 의견과 수익률 예측
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Description */}
        <div className="mb-8 p-6 border rounded-lg bg-card">
          <h2 className="text-xl font-bold mb-4">트리맵 사용법</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2 text-sm">📊 색상 의미</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <span className="text-green-600 font-semibold">초록색</span>: 매수 추천 (BUY)</li>
                <li>• <span className="text-red-600 font-semibold">빨간색</span>: 매도 추천 (SELL)</li>
                <li>• <span className="text-gray-600 font-semibold">회색</span>: 보유 추천 (HOLD)</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-sm">📐 크기 의미</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• 박스 크기 = 예상 변동률의 절대값</li>
                <li>• 큰 박스 = 큰 변동 예상</li>
                <li>• 작은 박스 = 작은 변동 예상</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Action Filter Tabs */}
        <div className="flex gap-2 mb-6">
          {(['ALL', 'BUY', 'SELL', 'HOLD'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setActionFilter(filter)}
              className={`px-6 py-3 rounded-lg text-sm font-medium transition-colors ${
                actionFilter === filter
                  ? filter === 'BUY'
                    ? 'bg-green-500 text-white'
                    : filter === 'SELL'
                    ? 'bg-red-500 text-white'
                    : filter === 'HOLD'
                    ? 'bg-gray-500 text-white'
                    : 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              {filter === 'ALL' && '전체'}
              {filter === 'BUY' && '💰 매수'}
              {filter === 'SELL' && '📉 매도'}
              {filter === 'HOLD' && '⏸️ 보유'}
            </button>
          ))}
        </div>

        {/* Treemap Component */}
        <div className="border rounded-lg overflow-hidden bg-card">
          <StockTreemap filter={actionFilter} language="ko" />
        </div>

        {/* Legend */}
        <div className="mt-6 p-4 border rounded-lg bg-muted/30">
          <h3 className="text-sm font-semibold mb-3">💡 Tip</h3>
          <p className="text-sm text-muted-foreground">
            각 종목 박스를 클릭하면 상세 분석 페이지로 이동합니다.
            색이 진할수록 AI의 확신도가 높습니다.
          </p>
        </div>
      </main>
    </div>
  )
}
