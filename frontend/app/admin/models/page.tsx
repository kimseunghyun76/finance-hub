'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/ui/toast'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'
import { ModelTableRow } from '@/components/model-table-row'

interface ModelInfo {
  ticker: string
  trained: boolean
  last_trained: string | null
  file_size: number
  model_path: string
  company_name?: string
}

interface PredictionScore {
  ticker: string
  confidence: number
  predicted_change_percent: number
  action: string
}

// Popular and recommended stocks to display
const POPULAR_STOCKS = [
  // US Tech Giants (High Volume)
  { ticker: 'AAPL', name: 'Apple', market: 'US', category: 'popular', description: '시가총액 1위 기술주' },
  { ticker: 'MSFT', name: 'Microsoft', market: 'US', category: 'popular', description: '클라우드 & AI 선도' },
  { ticker: 'GOOGL', name: 'Alphabet (Google)', market: 'US', category: 'popular', description: '검색 & AI 기술' },
  { ticker: 'AMZN', name: 'Amazon', market: 'US', category: 'popular', description: '이커머스 & 클라우드' },
  { ticker: 'NVDA', name: 'NVIDIA', market: 'US', category: 'popular', description: 'AI 칩 선도 기업' },
  { ticker: 'META', name: 'Meta (Facebook)', market: 'US', category: 'popular', description: '소셜미디어 & VR' },
  { ticker: 'TSLA', name: 'Tesla', market: 'US', category: 'popular', description: '전기차 & 에너지' },

  // US High Volume Stocks
  { ticker: 'AVGO', name: 'Broadcom', market: 'US', category: 'recommended', description: '반도체 & 소프트웨어' },
  { ticker: 'ORCL', name: 'Oracle', market: 'US', category: 'recommended', description: '엔터프라이즈 소프트웨어' },
  { ticker: 'NFLX', name: 'Netflix', market: 'US', category: 'recommended', description: '스트리밍 서비스' },
  { ticker: 'AMD', name: 'AMD', market: 'US', category: 'recommended', description: '고성능 프로세서' },
  { ticker: 'INTC', name: 'Intel', market: 'US', category: 'recommended', description: '반도체 제조' },
  { ticker: 'QCOM', name: 'Qualcomm', market: 'US', category: 'recommended', description: '모바일 칩셋' },
  { ticker: 'CSCO', name: 'Cisco', market: 'US', category: 'recommended', description: '네트워크 장비' },
  { ticker: 'CRM', name: 'Salesforce', market: 'US', category: 'recommended', description: 'CRM 소프트웨어' },
  { ticker: 'ADBE', name: 'Adobe', market: 'US', category: 'recommended', description: '크리에이티브 소프트웨어' },

  // Korean Popular Stocks (High Volume)
  { ticker: '005930.KS', name: '삼성전자', market: 'KR', category: 'popular', description: '반도체 & 전자제품' },
  { ticker: '000660.KS', name: 'SK하이닉스', market: 'KR', category: 'popular', description: '메모리 반도체' },
  { ticker: '035420.KS', name: 'NAVER', market: 'KR', category: 'popular', description: '검색 & 플랫폼' },
  { ticker: '035720.KS', name: '카카오', market: 'KR', category: 'popular', description: '메신저 & 플랫폼' },

  // Korean Recommended Stocks
  { ticker: '051910.KS', name: 'LG화학', market: 'KR', category: 'recommended', description: '2차전지 & 화학' },
  { ticker: '006400.KS', name: '삼성SDI', market: 'KR', category: 'recommended', description: '2차전지' },
  { ticker: '207940.KS', name: '삼성바이오로직스', market: 'KR', category: 'recommended', description: '바이오 제조' },
  { ticker: '068270.KS', name: '셀트리온', market: 'KR', category: 'recommended', description: '바이오 의약품' },
  { ticker: '105560.KS', name: 'KB금융', market: 'KR', category: 'recommended', description: '금융 지주사' },
  { ticker: '055550.KS', name: '신한지주', market: 'KR', category: 'recommended', description: '금융 지주사' },
]

const getStockName = (ticker: string): string => {
  const stock = POPULAR_STOCKS.find(s => s.ticker === ticker)
  return stock?.name || ticker
}

interface StockStatus {
  ticker: string
  name: string
  market: string
  category: string
  description: string
  trained: boolean
  training: boolean
  last_trained: string | null
  file_size: number
}

interface TrainingStatus {
  ticker: string
  name: string
  last_trained: string
  hours_ago: number
  file_size_mb: number
}

export default function ModelsPage() {
  const { addToast } = useToast()
  const [models, setModels] = useState<ModelInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTicker, setSearchTicker] = useState('')
  const [trainingTickers, setTrainingTickers] = useState<Set<string>>(new Set())
  const [trainingStatus, setTrainingStatus] = useState<{
    recently_trained: TrainingStatus[]
    total_models: number
  } | null>(null)
  const [predictionScores, setPredictionScores] = useState<Map<string, PredictionScore>>(new Map())

  useEffect(() => {
    loadModels()
    loadTrainingStatus()
    loadPredictionScores()
  }, [])

  const loadModels = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/models/details`)
      const data = await response.json()
      setModels(data.models || [])
    } catch (error) {
      console.error('Failed to load models:', error)
      addToast('error', '모델 목록을 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const loadTrainingStatus = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/training/status`)
      const data = await response.json()
      setTrainingStatus({
        recently_trained: data.recently_trained || [],
        total_models: data.total_models || 0
      })
    } catch (error) {
      console.error('Failed to load training status:', error)
    }
  }

  const loadPredictionScores = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/`)
      const data = await response.json()

      const scoresMap = new Map<string, PredictionScore>()
      if (data.trained_models && Array.isArray(data.trained_models)) {
        for (const ticker of data.trained_models) {
          try {
            const predResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/${ticker}`)
            const predData = await predResponse.json()
            scoresMap.set(ticker, {
              ticker,
              confidence: predData.prediction?.confidence || 0,
              predicted_change_percent: predData.prediction?.change_percent || 0,
              action: predData.action || 'HOLD'
            })
          } catch (err) {
            console.error(`Failed to load prediction for ${ticker}:`, err)
          }
        }
      }
      setPredictionScores(scoresMap)
    } catch (error) {
      console.error('Failed to load prediction scores:', error)
    }
  }

  // Combine popular stocks with trained models
  const getStockStatuses = (): StockStatus[] => {
    const modelMap = new Map(models.map(m => [m.ticker, m]))
    const allTickers = new Set([
      ...POPULAR_STOCKS.map(s => s.ticker),
      ...models.map(m => m.ticker)
    ])

    return Array.from(allTickers).map(ticker => {
      const stock = POPULAR_STOCKS.find(s => s.ticker === ticker)
      const model = modelMap.get(ticker)

      // Use company name from API if available, otherwise use predefined name
      const companyName = model?.company_name || stock?.name || ticker

      return {
        ticker,
        name: companyName,
        market: stock?.market || (ticker.includes('.KS') || ticker.includes('.KQ') ? 'KR' : 'US'),
        category: stock?.category || 'other',
        description: stock?.description || '사용자 추가 종목',
        trained: !!model,
        training: trainingTickers.has(ticker),
        last_trained: model?.last_trained || null,
        file_size: model?.file_size || 0,
      }
    }).sort((a, b) => {
      // Sort by: training > trained (by confidence/change) > not trained > name
      if (a.training !== b.training) return a.training ? -1 : 1
      if (a.trained !== b.trained) return a.trained ? -1 : 1

      // If both are trained, sort by prediction confidence and change percent
      if (a.trained && b.trained) {
        const aPred = predictionScores.get(a.ticker)
        const bPred = predictionScores.get(b.ticker)

        if (aPred && bPred) {
          // Calculate ranking score: confidence * abs(change_percent)
          const aScore = aPred.confidence * Math.abs(aPred.predicted_change_percent)
          const bScore = bPred.confidence * Math.abs(bPred.predicted_change_percent)
          if (aScore !== bScore) return bScore - aScore  // Higher score first
        }

        // Fallback to most recently trained
        if (a.last_trained && b.last_trained) {
          return new Date(b.last_trained).getTime() - new Date(a.last_trained).getTime()
        }
      }

      return a.name.localeCompare(b.name)
    })
  }

  const allStocks = getStockStatuses()
  const usStocks = allStocks.filter(s => s.market === 'US')
  const krStocks = allStocks.filter(s => s.market === 'KR')
  const otherStocks = allStocks.filter(s => s.market !== 'US' && s.market !== 'KR')

  const trainModel = async (ticker: string) => {
    try {
      setTrainingTickers(prev => new Set(prev).add(ticker))
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/train/${ticker}`,
        { method: 'POST' }
      )

      if (response.ok) {
        addToast('success', `${ticker} 모델 훈련이 시작되었습니다`)
        setTimeout(() => {
          loadModels()
          setTrainingTickers(prev => {
            const next = new Set(prev)
            next.delete(ticker)
            return next
          })
        }, 60000) // Reload after 1 minute
      } else {
        addToast('error', '훈련 시작에 실패했습니다')
        setTrainingTickers(prev => {
          const next = new Set(prev)
          next.delete(ticker)
          return next
        })
      }
    } catch (error) {
      console.error('Failed to train model:', error)
      addToast('error', '훈련 시작에 실패했습니다')
      setTrainingTickers(prev => {
        const next = new Set(prev)
        next.delete(ticker)
        return next
      })
    }
  }

  const trainAllModels = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/train-all`,
        { method: 'POST' }
      )

      if (response.ok) {
        addToast('success', '전체 모델 훈련이 시작되었습니다 (백그라운드 실행)')
      } else {
        addToast('error', '전체 훈련 시작에 실패했습니다')
      }
    } catch (error) {
      console.error('Failed to train all models:', error)
      addToast('error', '전체 훈련 시작에 실패했습니다')
    }
  }

  const deleteModel = async (ticker: string) => {
    if (!confirm(`정말 ${ticker} 모델을 삭제하시겠습니까?`)) {
      return
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/${ticker}/model`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        addToast('success', `${ticker} 모델이 삭제되었습니다`)
        loadModels()
      } else {
        addToast('error', '모델 삭제에 실패했습니다')
      }
    } catch (error) {
      console.error('Failed to delete model:', error)
      addToast('error', '모델 삭제에 실패했습니다')
    }
  }

  const deleteAllModels = async () => {
    if (!confirm(`정말 모든 AI 모델을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) {
      return
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/predictions/models/all`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        const result = await response.json()
        addToast('success', `${result.deleted_count}개 모델이 삭제되었습니다`)
        loadModels()
      } else {
        addToast('error', '모델 삭제에 실패했습니다')
      }
    } catch (error) {
      console.error('Failed to delete all models:', error)
      addToast('error', '모델 삭제에 실패했습니다')
    }
  }

  const searchAndTrain = async () => {
    const ticker = searchTicker.trim().toUpperCase()
    if (!ticker) {
      addToast('error', '티커를 입력해주세요')
      return
    }

    await trainModel(ticker)
    setSearchTicker('')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }


  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <Skeleton className="h-9 w-64" />
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold">AI 모델 관리</h1>
          <p className="text-muted-foreground mt-1">
            LSTM 기반 주가 예측 모델 관리 및 훈련
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Controls */}
        <div className="mb-8 space-y-4">
          {/* Search and Add */}
          <div className="flex gap-2">
            <Input
              placeholder="티커 입력 (예: AAPL, TSLA, 005930.KS)"
              value={searchTicker}
              onChange={(e) => setSearchTicker(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchAndTrain()}
              className="flex-1"
            />
            <Button onClick={searchAndTrain}>
              주식 추가 및 훈련
            </Button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button onClick={trainAllModels} variant="default">
              전체 재훈련
            </Button>
            <Button onClick={deleteAllModels} variant="destructive">
              전체 삭제
            </Button>
            <Button onClick={loadModels} variant="outline">
              새로고침
            </Button>
          </div>
        </div>

        {/* Recent Training Activity */}
        {trainingStatus && trainingStatus.recently_trained.length > 0 && (
          <div className="mb-8 p-6 border rounded-lg bg-blue-50 dark:bg-blue-950">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  최근 훈련 활동 (24시간 이내)
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {trainingStatus.recently_trained.length}개 모델이 최근에 훈련되었습니다
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {trainingStatus.recently_trained.slice(0, 6).map((model) => (
                <div key={model.ticker} className="p-4 bg-white dark:bg-gray-900 rounded-lg border">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-mono font-semibold text-sm">{model.ticker}</p>
                      <p className="text-xs text-muted-foreground truncate">{model.name}</p>
                    </div>
                    <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded whitespace-nowrap ml-2">
                      {Math.abs(model.hours_ago) < 1
                        ? '방금 전'
                        : `${Math.abs(Math.round(model.hours_ago))}시간 전`}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>{model.file_size_mb} MB</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">
              훈련된 모델
            </h3>
            <p className="text-3xl font-bold mt-2 text-green-600">{allStocks.filter(s => s.trained).length}</p>
          </div>

          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">
              미국 주식
            </h3>
            <p className="text-3xl font-bold mt-2 text-blue-600">
              {usStocks.filter(s => s.trained).length}/{usStocks.length}
            </p>
          </div>

          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">
              한국 주식
            </h3>
            <p className="text-3xl font-bold mt-2 text-purple-600">
              {krStocks.filter(s => s.trained).length}/{krStocks.length}
            </p>
          </div>

          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">
              총 모델 크기
            </h3>
            <p className="text-2xl font-bold mt-2">
              {formatFileSize(models.reduce((sum, m) => sum + m.file_size, 0))}
            </p>
          </div>

          <div className="p-6 border rounded-lg bg-card">
            <h3 className="text-sm font-medium text-muted-foreground">
              자동 훈련 스케줄
            </h3>
            <div className="mt-2 text-xs space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-semibold">📊 포트폴리오:</span>
                <span className="text-muted-foreground">매일 오전 9시</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">🆕 미훈련 추천주:</span>
                <span className="text-muted-foreground">매일 오후 2시</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">📅 전체 추천주:</span>
                <span className="text-muted-foreground">매주 일요일 오전 6시</span>
              </div>
            </div>
          </div>
        </div>

        {/* US Stocks Table */}
        <div className="space-y-4 mb-12">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">🇺🇸 미국 주식</h2>
              <p className="text-sm text-muted-foreground mt-1">
                기술주 중심의 고거래량 종목 ({usStocks.filter(s => s.trained).length}개 훈련됨)
              </p>
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-blue-50 dark:bg-blue-950">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium">티커</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">회사명</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">설명</th>
                    <th className="px-4 py-3 text-center text-sm font-medium">상태</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">마지막 훈련</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">크기</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">작업</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {usStocks.map((stock) => (
                    <tr key={stock.ticker} className="hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3">
                        <span className="font-mono font-medium">{stock.ticker}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{stock.name}</span>
                          {stock.category === 'popular' && (
                            <span className="text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 px-2 py-0.5 rounded">
                              인기
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-muted-foreground">{stock.description}</span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        {stock.training ? (
                          <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                            <svg className="animate-spin -ml-1 mr-2 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            훈련 중
                          </span>
                        ) : stock.trained ? (
                          <span className="inline-flex px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                            ✓ 훈련됨
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                            미훈련
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {stock.last_trained ? (
                          formatDistanceToNow(new Date(stock.last_trained), {
                            addSuffix: true,
                            locale: ko,
                          })
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                        {stock.file_size > 0 ? formatFileSize(stock.file_size) : '-'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex gap-2 justify-end">
                          <Button
                            size="sm"
                            variant={stock.trained ? "outline" : "default"}
                            onClick={() => trainModel(stock.ticker)}
                            disabled={stock.training}
                          >
                            {stock.trained ? '재훈련' : '훈련'}
                          </Button>
                          {stock.trained && (
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => deleteModel(stock.ticker)}
                            >
                              삭제
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Korean Stocks Table */}
        <div className="space-y-4 mb-12">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">🇰🇷 한국 주식</h2>
              <p className="text-sm text-muted-foreground mt-1">
                코스피/코스닥 대표 종목 ({krStocks.filter(s => s.trained).length}개 훈련됨)
              </p>
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-purple-50 dark:bg-purple-950">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium">티커</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">회사명</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">설명</th>
                    <th className="px-4 py-3 text-center text-sm font-medium">상태</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">마지막 훈련</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">크기</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">작업</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {krStocks.map((stock) => (
                    <tr key={stock.ticker} className="hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3">
                        <span className="font-mono font-medium">{stock.ticker}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{stock.name}</span>
                          {stock.category === 'popular' && (
                            <span className="text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 px-2 py-0.5 rounded">
                              인기
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-muted-foreground">{stock.description}</span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        {stock.training ? (
                          <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                            <svg className="animate-spin -ml-1 mr-2 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            훈련 중
                          </span>
                        ) : stock.trained ? (
                          <span className="inline-flex px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                            ✓ 훈련됨
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                            미훈련
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {stock.last_trained ? (
                          formatDistanceToNow(new Date(stock.last_trained), {
                            addSuffix: true,
                            locale: ko,
                          })
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                        {stock.file_size > 0 ? formatFileSize(stock.file_size) : '-'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex gap-2 justify-end">
                          <Button
                            size="sm"
                            variant={stock.trained ? "outline" : "default"}
                            onClick={() => trainModel(stock.ticker)}
                            disabled={stock.training}
                          >
                            {stock.trained ? '재훈련' : '훈련'}
                          </Button>
                          {stock.trained && (
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => deleteModel(stock.ticker)}
                            >
                              삭제
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Other Stocks (if any) */}
        {otherStocks.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">기타 종목</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  사용자가 추가한 종목 ({otherStocks.filter(s => s.trained).length}개 훈련됨)
                </p>
              </div>
            </div>

            <div className="border rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium">티커</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">회사명</th>
                      <th className="px-4 py-3 text-center text-sm font-medium">상태</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">마지막 훈련</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">크기</th>
                      <th className="px-4 py-3 text-right text-sm font-medium">작업</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {otherStocks.map((stock) => (
                      <tr key={stock.ticker} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3">
                          <span className="font-mono font-medium">{stock.ticker}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm">{stock.name}</span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {stock.training ? (
                            <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                              <svg className="animate-spin -ml-1 mr-2 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              훈련 중
                            </span>
                          ) : stock.trained ? (
                            <span className="inline-flex px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                              ✓ 훈련됨
                            </span>
                          ) : (
                            <span className="inline-flex px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                              미훈련
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {stock.last_trained ? (
                            formatDistanceToNow(new Date(stock.last_trained), {
                              addSuffix: true,
                              locale: ko,
                            })
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                          {stock.file_size > 0 ? formatFileSize(stock.file_size) : '-'}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex gap-2 justify-end">
                            <Button
                              size="sm"
                              variant={stock.trained ? "outline" : "default"}
                              onClick={() => trainModel(stock.ticker)}
                              disabled={stock.training}
                            >
                              {stock.trained ? '재훈련' : '훈련'}
                            </Button>
                            {stock.trained && (
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => deleteModel(stock.ticker)}
                              >
                                삭제
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
