'use client'

import { useState } from 'react'
import {
  Home,
  TrendingUp,
  Map,
  Search,
  Scale,
  PieChart,
  Star,
  BarChart3,
  Wallet,
  Briefcase,
  Brain,
  ChevronRight,
  BookOpen
} from 'lucide-react'

interface GuideSection {
  id: string
  icon: React.ReactNode
  title: string
  description: string
  features: string[]
  howToUse: string[]
  tips?: string[]
}

const guideSections: GuideSection[] = [
  {
    id: 'home',
    icon: <Home className="w-6 h-6" />,
    title: '🏠 홈 대시보드',
    description: 'AI 기반 주식 투자 현황을 한눈에 확인할 수 있는 메인 대시보드입니다.',
    features: [
      '총 자산 현황 및 수익률 실시간 조회',
      '관심 종목 개수 및 빠른 접근',
      'AI 매수/매도 신호 개수 확인',
      'Top 6 AI 추천 종목 (확신도 순)',
      '포트폴리오 요약 (보유 종목, 현금, 거래 횟수)',
      'AI 승률 통계',
      '주요 기능 빠른 실행 링크'
    ],
    howToUse: [
      '대시보드에서 전체 투자 현황을 확인합니다',
      'AI 추천 종목을 클릭하여 상세 분석 페이지로 이동합니다',
      '빠른 실행 버튼으로 원하는 기능에 바로 접근합니다',
      '포트폴리오 카드에서 전체 보기를 클릭하여 상세 내역을 확인합니다'
    ],
    tips: [
      'AI 추천은 확신도가 높은 순으로 정렬되어 있습니다',
      '총 자산의 수익률을 주기적으로 확인하여 투자 성과를 모니터링하세요',
      'AI 승률이 50% 이상일 때 AI 추천을 더 신뢰할 수 있습니다'
    ]
  },
  {
    id: 'stocks-list',
    icon: <TrendingUp className="w-6 h-6" />,
    title: '📋 인기 종목',
    description: 'AI가 분석한 주요 종목들의 예측 정보를 한눈에 비교하고 확인할 수 있습니다.',
    features: [
      '미국 주요 기술주 및 한국 주요 종목 리스트',
      '각 종목의 AI 예측 결과 (매수/매도/보유)',
      '예상 변동률 및 확신도 표시',
      '현재가 및 기본 정보',
      '관심 종목 등록/해제 기능',
      '종목 클릭 시 상세 분석 페이지 이동'
    ],
    howToUse: [
      '종목 목록에서 관심 있는 종목을 찾습니다',
      '별표 아이콘을 클릭하여 관심 종목에 추가/제거합니다',
      'AI 추천 배지(매수/매도/보유)를 확인합니다',
      '예상 변동률과 확신도를 참고하여 투자 판단을 합니다',
      '종목 카드를 클릭하면 상세 분석 페이지로 이동합니다'
    ],
    tips: [
      '확신도가 70% 이상인 종목에 주목하세요',
      '여러 종목을 관심 종목에 추가하여 비교 관찰하세요',
      '예상 변동률이 크다고 무조건 좋은 것은 아닙니다 - 확신도를 함께 확인하세요'
    ]
  },
  {
    id: 'prediction-map',
    icon: <Map className="w-6 h-6" />,
    title: '🗺️ 예측 맵',
    description: '모든 종목의 AI 예측을 시각적으로 한눈에 파악할 수 있는 인터랙티브 맵입니다.',
    features: [
      '전체 종목의 AI 추천 시각화',
      '매수/매도/보유 구분 색상 표시',
      '예상 변동률 크기에 따른 정렬',
      '확신도 바 차트 표시',
      '필터 및 정렬 기능',
      '클릭하여 상세 정보 확인'
    ],
    howToUse: [
      '예측 맵에서 전체 종목의 분포를 확인합니다',
      '녹색(매수), 빨간색(매도), 회색(보유) 배지로 AI 추천을 파악합니다',
      '예상 변동률이 큰 종목을 찾아 투자 기회를 발견합니다',
      '확신도 바를 확인하여 AI의 확신 정도를 판단합니다'
    ],
    tips: [
      '매수 신호가 많은 구간에서 투자 기회를 찾아보세요',
      '확신도와 예상 변동률을 함께 고려하세요',
      '전체적인 시장 분위기(매수/매도 비율)를 파악할 수 있습니다'
    ]
  },
  {
    id: 'discovery',
    icon: <Search className="w-6 h-6" />,
    title: '🔍 신규 발굴',
    description: 'AI가 추천하는 새로운 투자 기회를 발견할 수 있는 페이지입니다.',
    features: [
      '강력한 매수 신호 종목 발굴',
      '높은 확신도 기반 추천',
      '섹터별 유망 종목',
      '성장 가능성 높은 종목',
      '실시간 업데이트',
      '다양한 필터 옵션'
    ],
    howToUse: [
      '신규 발굴 페이지에서 AI가 선별한 종목을 확인합니다',
      '매수 신호가 강한 종목부터 검토합니다',
      '확신도와 예상 변동률을 함께 분석합니다',
      '마음에 드는 종목은 관심 종목에 추가합니다',
      '상세 분석을 통해 최종 투자 결정을 합니다'
    ],
    tips: [
      '신규 발굴은 투자 기회 발견용입니다 - 반드시 상세 분석을 확인하세요',
      '여러 종목을 비교하여 가장 좋은 기회를 선택하세요',
      '섹터 분산 투자를 고려하세요'
    ]
  },
  {
    id: 'compare',
    icon: <Scale className="w-6 h-6" />,
    title: '⚖️ 종목 비교',
    description: '최대 5개 종목을 동시에 비교하여 최적의 투자 선택을 할 수 있습니다.',
    features: [
      '최대 5개 종목 동시 비교',
      'AI 추천 비교',
      '예상 변동률 비교',
      'AI 확신도 비교',
      '현재가 및 시가총액 비교',
      '섹터 정보',
      'URL 공유 가능'
    ],
    howToUse: [
      '종목 코드 입력란에 비교하고 싶은 종목을 입력합니다 (예: AAPL)',
      '추가 버튼을 클릭하여 종목을 추가합니다 (최대 5개)',
      '비교 테이블에서 각 항목을 비교합니다',
      'X 버튼을 클릭하여 종목을 제거할 수 있습니다',
      'URL을 복사하여 다른 사람과 비교 결과를 공유할 수 있습니다'
    ],
    tips: [
      'URL에 직접 입력도 가능합니다: /compare?tickers=AAPL,GOOGL,TSLA',
      '같은 섹터 내 종목을 비교하면 더 의미있는 분석이 가능합니다',
      'AI 확신도가 비슷할 때는 예상 변동률을 기준으로 선택하세요'
    ]
  },
  {
    id: 'sectors',
    icon: <PieChart className="w-6 h-6" />,
    title: '📊 섹터 분석',
    description: '산업 섹터별 투자 동향과 AI 추천을 분석할 수 있습니다.',
    features: [
      '섹터별 종목 그룹핑',
      '섹터별 AI 추천 통계',
      '섹터별 평균 수익률',
      '섹터 트렌드 분석',
      '섹터별 대표 종목',
      '섹터 비교 기능'
    ],
    howToUse: [
      '섹터 목록에서 관심 있는 산업을 선택합니다',
      '해당 섹터의 전체 통계를 확인합니다',
      '섹터 내 주요 종목들을 비교합니다',
      'AI 추천 비율을 확인하여 섹터 전망을 파악합니다',
      '여러 섹터를 비교하여 분산 투자 전략을 수립합니다'
    ],
    tips: [
      '섹터 분산 투자로 리스크를 줄일 수 있습니다',
      '특정 섹터에 매수 신호가 집중되면 해당 산업의 성장 가능성이 높습니다',
      '경제 상황에 따라 유망 섹터가 달라질 수 있습니다'
    ]
  },
  {
    id: 'watchlist',
    icon: <Star className="w-6 h-6" />,
    title: '⭐ 관심 종목',
    description: '자주 확인하는 종목을 등록하여 빠르게 모니터링할 수 있습니다.',
    features: [
      '무제한 종목 등록',
      '실시간 AI 예측 업데이트',
      '빠른 접근 및 관리',
      '상세 정보 바로가기',
      '일괄 비교 기능',
      '로컬 저장 (브라우저)'
    ],
    howToUse: [
      '인기 종목 또는 다른 페이지에서 별표 아이콘을 클릭하여 추가합니다',
      '관심 종목 페이지에서 등록된 모든 종목을 확인합니다',
      '각 종목의 최신 AI 예측을 모니터링합니다',
      '더 이상 관심 없는 종목은 별표를 다시 클릭하여 제거합니다',
      '"전체 비교" 버튼으로 관심 종목들을 한번에 비교할 수 있습니다'
    ],
    tips: [
      '5-10개 정도의 종목을 관심 종목으로 유지하는 것이 좋습니다',
      '매일 관심 종목의 AI 예측 변화를 확인하세요',
      '관심 종목 데이터는 브라우저에 저장되므로 다른 기기에서는 보이지 않습니다'
    ]
  },
  {
    id: 'backtest',
    icon: <BarChart3 className="w-6 h-6" />,
    title: '📈 백테스팅',
    description: 'AI 예측의 과거 성과를 검증하여 신뢰도를 확인할 수 있습니다.',
    features: [
      '과거 데이터 기반 AI 성과 검증',
      '기간 선택 (1개월, 3개월, 6개월, 1년)',
      '승률 및 평균 수익률 계산',
      '최고/최악 거래 내역',
      '월별 성과 분석',
      '실제 투자 전 전략 검증'
    ],
    howToUse: [
      '종목 코드를 입력합니다 (예: AAPL)',
      '백테스트 기간을 선택합니다 (1개월 ~ 1년)',
      '분석 시작 버튼을 클릭합니다',
      '총 거래 횟수, 승률, 평균 수익률을 확인합니다',
      '최고/최악 거래를 보고 AI의 장단점을 파악합니다',
      '월별 성과를 분석하여 시기별 특성을 이해합니다'
    ],
    tips: [
      '승률 60% 이상이면 신뢰할 만한 AI 예측입니다',
      '최근 3개월 데이터가 가장 현재 시장 상황과 유사합니다',
      '백테스팅 결과가 좋다고 미래 성과를 보장하지는 않습니다',
      '여러 기간으로 테스트하여 일관성을 확인하세요'
    ]
  },
  {
    id: 'paper-trading',
    icon: <Wallet className="w-6 h-6" />,
    title: '💼 가상투자',
    description: '실제 돈을 쓰지 않고 AI 전략을 테스트할 수 있는 모의 투자 시스템입니다.',
    features: [
      '초기 자본 $100,000',
      '실시간 가격 기반 매수/매도',
      '포트폴리오 자동 계산',
      '수익률 실시간 추적',
      'AI 추천 거래 추적',
      'AI 승률 통계',
      '거래 내역 기록',
      '포트폴리오 초기화 기능'
    ],
    howToUse: [
      '매수 버튼을 클릭하여 종목 코드, 수량, 가격을 입력합니다',
      '매수 확정을 클릭하여 거래를 실행합니다',
      '보유 종목 테이블에서 실시간 손익을 확인합니다',
      '매도하고 싶은 종목의 매도 버튼을 클릭합니다',
      '시세 갱신 버튼으로 최신 가격을 업데이트합니다',
      '거래 내역에서 과거 모든 거래를 확인합니다',
      '처음부터 다시 시작하려면 초기화 버튼을 클릭합니다'
    ],
    tips: [
      'AI 추천에 따라 거래하면 AI 승률 통계에 반영됩니다',
      '실제 투자 전에 충분히 연습하세요',
      '분산 투자를 연습하여 리스크 관리 능력을 키우세요',
      '감정적인 거래를 피하고 데이터 기반으로 판단하세요',
      '데이터는 브라우저에 저장되므로 삭제하지 않도록 주의하세요'
    ]
  },
  {
    id: 'portfolio',
    icon: <Briefcase className="w-6 h-6" />,
    title: '💼 포트폴리오',
    description: '가상투자 포트폴리오의 상세 내역과 통계를 확인할 수 있습니다.',
    features: [
      '전체 자산 현황',
      '보유 종목별 상세 정보',
      '종목별 손익 분석',
      '평균 단가 계산',
      '포트폴리오 구성 비율',
      '전체 수익률',
      '거래 히스토리'
    ],
    howToUse: [
      '대시보드 또는 가상투자에서 포트폴리오를 확인합니다',
      '각 종목의 평균 단가와 현재가를 비교합니다',
      '손익률을 확인하여 투자 성과를 평가합니다',
      '포트폴리오 구성 비율을 보고 분산 투자 정도를 파악합니다',
      '수익률이 낮은 종목은 재검토하거나 손절을 고려합니다'
    ],
    tips: [
      '한 종목에 전체 자산의 30% 이상 투자하지 마세요',
      '정기적으로 포트폴리오를 리밸런싱하세요',
      '손실이 -10% 이하로 가면 전략을 재검토하세요',
      '수익이 나면 일부 현금화하여 리스크를 관리하세요'
    ]
  },
  {
    id: 'models',
    icon: <Brain className="w-6 h-6" />,
    title: '🤖 AI 모델',
    description: 'AI 예측 모델의 성능과 학습 상태를 확인할 수 있습니다.',
    features: [
      '모델 정확도 정보',
      '학습 데이터 기간',
      '예측 알고리즘 설명',
      '모델 업데이트 이력',
      '성능 지표',
      '신뢰도 평가'
    ],
    howToUse: [
      'AI 모델 페이지에서 현재 사용 중인 모델 정보를 확인합니다',
      '모델 정확도와 신뢰도를 확인합니다',
      '학습 데이터 기간을 보고 최신성을 판단합니다',
      '예측 알고리즘을 이해하여 AI의 판단 근거를 파악합니다',
      '모델 업데이트 이력으로 개선 사항을 확인합니다'
    ],
    tips: [
      'AI 모델은 과거 데이터로 학습하므로 예측이 100% 정확하지는 않습니다',
      '모델 정확도가 70% 이상이면 신뢰할 만합니다',
      '시장 상황이 급변하면 AI 예측의 신뢰도가 낮아질 수 있습니다',
      '여러 지표를 종합적으로 판단하세요'
    ]
  }
]

export default function GuidePage() {
  const [selectedSection, setSelectedSection] = useState<string>('home')

  const currentSection = guideSections.find(s => s.id === selectedSection) || guideSections[0]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-950 dark:to-blue-950">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen className="w-8 h-8" />
            <h1 className="text-4xl font-bold">📖 사용 가이드</h1>
          </div>
          <p className="text-lg text-muted-foreground">
            Finance-Hub의 모든 기능을 효과적으로 활용하는 방법을 알아보세요
          </p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Navigation */}
          <div className="lg:col-span-1">
            <div className="sticky top-4 border rounded-lg bg-card p-4">
              <h2 className="font-bold mb-4 text-lg">기능 목록</h2>
              <nav className="space-y-2">
                {guideSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setSelectedSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      selectedSection === section.id
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-accent'
                    }`}
                  >
                    {section.icon}
                    <span className="text-sm font-medium">{section.title}</span>
                    <ChevronRight className="w-4 h-4 ml-auto" />
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Right Content - Guide Details */}
          <div className="lg:col-span-3">
            <div className="border rounded-lg bg-card p-8">
              {/* Section Header */}
              <div className="flex items-center gap-4 mb-6 pb-6 border-b">
                <div className="p-3 rounded-lg bg-primary/10 text-primary">
                  {currentSection.icon}
                </div>
                <div>
                  <h2 className="text-3xl font-bold mb-2">{currentSection.title}</h2>
                  <p className="text-muted-foreground">{currentSection.description}</p>
                </div>
              </div>

              {/* Features */}
              <div className="mb-8">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="text-2xl">✨</span>
                  주요 기능
                </h3>
                <ul className="space-y-2">
                  {currentSection.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="text-primary mt-1">•</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* How to Use */}
              <div className="mb-8">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="text-2xl">📝</span>
                  사용 방법
                </h3>
                <ol className="space-y-3">
                  {currentSection.howToUse.map((step, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </span>
                      <span className="pt-0.5">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* Tips */}
              {currentSection.tips && currentSection.tips.length > 0 && (
                <div className="bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
                    <span className="text-2xl">💡</span>
                    활용 팁
                  </h3>
                  <ul className="space-y-2">
                    {currentSection.tips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-3 text-yellow-800 dark:text-yellow-200">
                        <span className="mt-1">▸</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* General Tips */}
            {selectedSection === 'home' && (
              <div className="mt-8 border rounded-lg bg-card p-8">
                <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <span className="text-2xl">🎯</span>
                  성공적인 투자를 위한 일반 원칙
                </h3>
                <div className="space-y-4">
                  <div className="p-4 border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/20">
                    <p className="font-semibold text-blue-900 dark:text-blue-100">분산 투자</p>
                    <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
                      한 종목에 모든 자산을 투자하지 마세요. 여러 종목과 섹터에 분산하여 리스크를 관리하세요.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-green-500 bg-green-50 dark:bg-green-950/20">
                    <p className="font-semibold text-green-900 dark:text-green-100">장기 관점</p>
                    <p className="text-sm text-green-800 dark:text-green-200 mt-1">
                      단기 변동에 일희일비하지 말고 장기적인 관점에서 투자하세요.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-950/20">
                    <p className="font-semibold text-purple-900 dark:text-purple-100">데이터 기반 의사결정</p>
                    <p className="text-sm text-purple-800 dark:text-purple-200 mt-1">
                      감정이 아닌 데이터와 AI 분석을 기반으로 투자 결정을 내리세요.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-950/20">
                    <p className="font-semibold text-orange-900 dark:text-orange-100">리스크 관리</p>
                    <p className="text-sm text-orange-800 dark:text-orange-200 mt-1">
                      손실 한도를 정하고 지키세요. 투자 금액은 잃어도 괜찮은 수준으로 제한하세요.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-red-500 bg-red-50 dark:bg-red-950/20">
                    <p className="font-semibold text-red-900 dark:text-red-100">⚠️ 투자 유의사항</p>
                    <p className="text-sm text-red-800 dark:text-red-200 mt-1">
                      본 서비스의 AI 예측은 참고용이며 투자 권유가 아닙니다. 모든 투자 결정은 본인의 책임 하에 신중히 하시기 바랍니다.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
