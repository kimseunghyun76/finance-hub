'use client'

import { SectorRecommendations } from '@/components/sector-recommendations'

export default function SectorsPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">🎯 AI 섹터 분석</h1>
          <p className="text-lg text-muted-foreground">
            인공지능 기반 섹터 순환 전략과 투자 추천
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Description Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <span className="text-2xl">📈</span>
              섹터 순환 전략
            </h3>
            <p className="text-sm text-muted-foreground">
              경기 사이클에 따른 섹터별 투자 타이밍 포착
            </p>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <span className="text-2xl">🤖</span>
              AI 기반 분석
            </h3>
            <p className="text-sm text-muted-foreground">
              머신러닝으로 예측한 섹터별 수익률과 모멘텀
            </p>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              종목 추천
            </h3>
            <p className="text-sm text-muted-foreground">
              각 섹터별 상위 성과 예상 종목 자동 선별
            </p>
          </div>
        </div>

        {/* Main Content */}
        <SectorRecommendations />
      </main>
    </div>
  )
}
