'use client'

import { StockDiscovery } from '@/components/stock-discovery'

export default function DiscoveryPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950 dark:to-amber-950">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold mb-2">🔍 신규 종목 발굴</h1>
          <p className="text-lg text-muted-foreground">
            AI 기반 투자 기회 발견과 자동 훈련 추천
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Description Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <span className="text-2xl">📊</span>
              시가총액 기반
            </h3>
            <p className="text-sm text-muted-foreground">
              주요 지수의 시가총액 상위 종목 자동 추출
            </p>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <span className="text-2xl">⚡</span>
              실시간 시그널
            </h3>
            <p className="text-sm text-muted-foreground">
              거래량 급증, 가격 급변 등 시장 시그널 감지
            </p>
          </div>
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <span className="text-2xl">🤖</span>
              원클릭 훈련
            </h3>
            <p className="text-sm text-muted-foreground">
              관심 종목 즉시 AI 모델 훈련 시작
            </p>
          </div>
        </div>

        {/* Discovery Component */}
        <StockDiscovery />

        {/* Additional Info */}
        <div className="mt-8 p-6 border rounded-lg bg-muted/30">
          <h3 className="font-semibold mb-3">📌 발굴 기준</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
            <div>
              <p className="font-semibold text-foreground mb-1">HIGH 우선순위</p>
              <p>복합 시그널 (거래량 급증 + 가격 급변)</p>
            </div>
            <div>
              <p className="font-semibold text-foreground mb-1">MEDIUM 우선순위</p>
              <p>단일 시그널 (거래량 급증 또는 가격 급변)</p>
            </div>
            <div>
              <p className="font-semibold text-foreground mb-1">LOW 우선순위</p>
              <p>시가총액 상위 종목 (시그널 없음)</p>
            </div>
            <div>
              <p className="font-semibold text-foreground mb-1">시그널 기준</p>
              <p>거래량: 평균 대비 2배 이상 / 가격: 5일간 10% 이상 변동</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
