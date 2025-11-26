'use client'

import { AlertTriangle, Info, Shield } from 'lucide-react'

interface LegalDisclaimerProps {
  variant?: 'full' | 'compact' | 'banner'
  className?: string
}

export function LegalDisclaimer({ variant = 'compact', className = '' }: LegalDisclaimerProps) {
  if (variant === 'banner') {
    return (
      <div className={`fixed bottom-0 left-0 right-0 z-50 border-t bg-yellow-50 dark:bg-yellow-950/30 border-yellow-200 dark:border-yellow-800 ${className}`}>
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center gap-3 text-sm">
            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
            <p className="text-yellow-800 dark:text-yellow-200">
              <strong>투자 유의사항:</strong> 본 서비스는 금융투자업법에 따른 투자자문업이 아니며,
              제공되는 정보는 투자 판단의 참고자료일 뿐입니다. 모든 투자 결정과 손실에 대한 책임은 투자자 본인에게 있습니다.
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <div className={`p-4 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800 ${className}`}>
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium mb-1">
              투자 유의사항
            </p>
            <p className="text-xs text-yellow-700 dark:text-yellow-300">
              본 서비스는 <strong>금융투자업법에 따른 투자자문업이 아니며</strong>,
              AI 예측 및 제공되는 모든 정보는 투자 판단의 참고자료일 뿐입니다.
              과거 데이터 기반 분석이므로 미래 수익을 보장하지 않으며,
              모든 투자 결정과 그에 따른 손실은 투자자 본인의 책임입니다.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Full variant
  return (
    <div className={`border rounded-xl p-6 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/20 dark:to-yellow-950/20 border-amber-200 dark:border-amber-800 ${className}`}>
      <div className="flex items-center gap-3 mb-4">
        <Shield className="w-6 h-6 text-amber-600" />
        <h3 className="text-lg font-bold text-amber-900 dark:text-amber-100">
          법적 고지 및 투자 유의사항
        </h3>
      </div>

      <div className="space-y-4 text-sm text-amber-800 dark:text-amber-200">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold mb-1">투자자문업 아님</p>
            <p className="text-xs">
              본 서비스는 <strong>금융투자업법에 따른 투자자문업, 투자일임업, 신탁업 등에 해당하지 않습니다</strong>.
              금융위원회 또는 금융감독원의 인가를 받지 않은 일반 정보 제공 서비스입니다.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold mb-1">참고자료 목적</p>
            <p className="text-xs">
              제공되는 AI 예측, 매매 신호, 종목 분석 등 모든 정보는 <strong>투자 권유가 아닌 참고자료</strong>일 뿐이며,
              투자자 본인의 독자적인 판단과 책임 하에 활용되어야 합니다.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold mb-1">투자 위험 고지</p>
            <ul className="text-xs space-y-1 list-disc list-inside">
              <li><strong>과거 성과는 미래 수익을 보장하지 않습니다</strong></li>
              <li>AI 예측 모델은 역사적 데이터에 기반하며, 예측이 틀릴 수 있습니다</li>
              <li>주식 투자는 원금 손실의 위험이 있으며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다</li>
              <li>투자하기 전 반드시 금융감독원 전자공시시스템(DART) 등에서 기업 정보를 확인하세요</li>
              <li>투자 결정 시 금융투자 전문가와 상담하실 것을 권장합니다</li>
            </ul>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold mb-1">데이터 정확성</p>
            <p className="text-xs">
              본 서비스에서 제공하는 주가, 재무 정보 등은 제3자 데이터 소스(yfinance 등)에 의존하며,
              실시간성 및 정확성을 보장하지 않습니다. 투자 전 반드시 공식 거래소 데이터를 확인하세요.
            </p>
          </div>
        </div>

        <div className="pt-3 border-t border-amber-300 dark:border-amber-700">
          <p className="text-xs font-medium">
            본 서비스 이용 시 위 유의사항을 충분히 이해하고 동의한 것으로 간주합니다.
            자세한 내용은 <a href="/terms" className="underline hover:text-amber-600">이용약관</a> 및 <a href="/privacy" className="underline hover:text-amber-600">개인정보처리방침</a>을 참조하세요.
          </p>
        </div>
      </div>
    </div>
  )
}
