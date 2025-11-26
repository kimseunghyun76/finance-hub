'use client'

import Link from 'next/link'
import { Settings, Brain, Clock } from 'lucide-react'

export default function AdminPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">관리자 페이지</h1>
        <p className="text-muted-foreground mb-8">
          시스템 관리 및 AI 모델 관련 고급 기능
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          {/* AI Models Management */}
          <Link
            href="/admin/models"
            className="p-6 border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center gap-3 mb-3">
              <Brain className="w-8 h-8 text-primary" />
              <h2 className="text-xl font-semibold">AI 모델 관리</h2>
            </div>
            <p className="text-sm text-muted-foreground">
              AI 예측 모델 학습 상태 확인, 새 모델 학습, 모델 정확도 모니터링
            </p>
          </Link>

          {/* Scheduler Management */}
          <Link
            href="/admin/scheduler"
            className="p-6 border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center gap-3 mb-3">
              <Clock className="w-8 h-8 text-primary" />
              <h2 className="text-xl font-semibold">스케줄러 관리</h2>
            </div>
            <p className="text-sm text-muted-foreground">
              자동 학습 스케줄 설정, 작업 로그 확인, 예측 업데이트 모니터링
            </p>
          </Link>
        </div>

        <div className="mt-8 p-4 border rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>알림:</strong> 관리자 기능은 시스템 설정 및 AI 모델 관리를 위한 고급 기능입니다.
            잘못된 설정은 서비스 성능에 영향을 줄 수 있으니 주의해서 사용하세요.
          </p>
        </div>

        <div className="mt-6">
          <Link href="/" className="text-primary hover:underline">
            ← 홈으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  )
}
