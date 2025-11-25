'use client'

import Link from 'next/link'
import { Settings, BarChart3, Activity, GitCompare, Bot, Clock } from 'lucide-react'

export default function SettingsPage() {
  const settingsItems = [
    {
      icon: Activity,
      title: '예측 정확도',
      description: 'AI 모델의 예측 정확도를 확인하고 검증합니다',
      href: '/accuracy',
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: BarChart3,
      title: '백테스팅',
      description: '과거 데이터로 전략을 테스트하고 성능을 분석합니다',
      href: '/backtest',
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: GitCompare,
      title: '비교 분석',
      description: '여러 종목을 비교하고 분석합니다',
      href: '/compare',
      color: 'from-green-500 to-green-600'
    },
    {
      icon: Bot,
      title: 'AI 모델 관리',
      description: 'AI 학습 모델을 관리하고 성능을 모니터링합니다',
      href: '/models',
      color: 'from-orange-500 to-orange-600'
    },
    {
      icon: Clock,
      title: '스케줄러',
      description: '자동화된 작업 스케줄을 관리합니다',
      href: '/scheduler',
      color: 'from-pink-500 to-pink-600'
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-slate-50 to-gray-50 dark:from-slate-950 dark:to-gray-950">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-3 mb-2">
            <Settings className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-bold">설정</h1>
          </div>
          <p className="text-lg text-muted-foreground">
            시스템 관리 및 고급 기능
          </p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {settingsItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className="group border rounded-xl p-6 bg-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">
                  {item.title}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {item.description}
                </p>
              </Link>
            )
          })}
        </div>

        {/* Info Section */}
        <div className="mt-12 p-6 border rounded-xl bg-blue-50 dark:bg-blue-950/20">
          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            시스템 설정 안내
          </h3>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>• <strong>예측 정확도</strong>: AI 모델의 예측 성능을 모니터링하고 검증 결과를 확인합니다</p>
            <p>• <strong>백테스팅</strong>: 과거 데이터를 활용하여 투자 전략의 성능을 테스트합니다</p>
            <p>• <strong>비교 분석</strong>: 여러 종목의 예측 결과와 성능을 비교 분석합니다</p>
            <p>• <strong>AI 모델 관리</strong>: 학습된 모델을 관리하고 재훈련을 수행합니다</p>
            <p>• <strong>스케줄러</strong>: 자동화된 데이터 수집 및 모델 업데이트 작업을 관리합니다</p>
          </div>
        </div>
      </div>
    </div>
  )
}
