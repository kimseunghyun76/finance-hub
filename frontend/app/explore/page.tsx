'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { predictionApi } from '@/lib/api'
import StockTreemap from '@/components/stock-treemap'
import { StockDiscovery } from '@/components/stock-discovery'
import { LayoutGrid, Map, Search } from 'lucide-react'

// Stock name mapping
const STOCK_NAMES: Record<string, { name: string; market: string }> = {
  // US Stocks
  'AAPL': { name: 'Apple Inc.', market: 'NASDAQ' },
  'GOOGL': { name: 'Alphabet (Google)', market: 'NASDAQ' },
  'MSFT': { name: 'Microsoft Corp.', market: 'NASDAQ' },
  'TSLA': { name: 'Tesla Inc.', market: 'NASDAQ' },
  'NVDA': { name: 'NVIDIA Corp.', market: 'NASDAQ' },
  'AMZN': { name: 'Amazon.com Inc.', market: 'NASDAQ' },
  'META': { name: 'Meta (Facebook)', market: 'NASDAQ' },
  'AVGO': { name: 'Broadcom Inc.', market: 'NASDAQ' },
  'ORCL': { name: 'Oracle Corp.', market: 'NYSE' },
  'NFLX': { name: 'Netflix Inc.', market: 'NASDAQ' },
  'AMD': { name: 'AMD', market: 'NASDAQ' },
  'INTC': { name: 'Intel Corp.', market: 'NASDAQ' },
  'QCOM': { name: 'Qualcomm Inc.', market: 'NASDAQ' },
  'CSCO': { name: 'Cisco Systems', market: 'NASDAQ' },
  // Korean Stocks
  '005930.KS': { name: '삼성전자', market: 'KRX' },
  '000660.KS': { name: 'SK하이닉스', market: 'KRX' },
  '035420.KS': { name: 'NAVER', market: 'KRX' },
  '035720.KS': { name: '카카오', market: 'KRX' },
}

interface ModelDetail {
  ticker: string
  name: string
  market: string
  trained: boolean
}

export default function ExplorePage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [language, setLanguage] = useState<'ko' | 'en'>('ko')
  const [models, setModels] = useState<ModelDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'treemap' | 'discovery'>('grid')
  const [actionFilter, setActionFilter] = useState<'ALL' | 'BUY' | 'SELL' | 'HOLD'>('ALL')

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const response = await predictionApi.getTrainedModels()
      const trainedTickers = response.data.trained_models

      // Create list combining trained models and popular stocks
      const allTickers = new Set([
        ...trainedTickers,
        ...Object.keys(STOCK_NAMES)
      ])

      const modelList: ModelDetail[] = Array.from(allTickers).map(ticker => {
        const stockInfo = STOCK_NAMES[ticker] || {
          name: ticker,
          market: ticker.includes('.KS') || ticker.includes('.KQ') ? 'KRX' : 'NASDAQ'
        }

        return {
          ticker,
          name: stockInfo.name,
          market: stockInfo.market,
          trained: trainedTickers.includes(ticker)
        }
      })

      // Sort: trained first, then alphabetically
      modelList.sort((a, b) => {
        if (a.trained !== b.trained) return a.trained ? -1 : 1
        return a.ticker.localeCompare(b.ticker)
      })

      setModels(modelList)
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/stocks/${searchQuery.trim().toUpperCase()}`)
    }
  }

  const handleStockClick = (ticker: string) => {
    router.push(`/stocks/${ticker}`)
  }

  const t = {
    ko: {
      title: '주식 탐색',
      subtitle: '주식을 검색하고 AI 예측을 확인하세요',
      searchPlaceholder: '종목 코드 입력 (예: AAPL, 005930.KS)',
      searchButton: '검색',
      popularTitle: '인기 종목',
      popularSubtitle: '자주 조회되는 종목을 빠르게 확인하세요',
      usStocks: '미국 주식',
      krStocks: '한국 주식',
      viewDetails: '상세보기',
      howToSearch: '검색 방법',
      searchTip1: '미국 주식: 종목 코드만 입력 (예: AAPL, GOOGL)',
      searchTip2: '한국 주식: 종목 코드.KS 형식 (예: 005930.KS, 035420.KS)',
      viewMode: '보기 모드',
      gridView: '그리드',
      treemapView: '트리맵',
      discoveryView: '신규 종목 발굴',
      predictionMap: 'AI 예측 맵',
      predictionMapSubtitle: '한눈에 보는 AI 매매 의견',
      stockDiscovery: '신규 종목 발굴',
      stockDiscoverySubtitle: '투자 기회를 찾아보세요',
      filterAll: '전체',
      filterBuy: '매수',
      filterSell: '매도',
      filterHold: '보유',
    },
    en: {
      title: 'Explore Stocks',
      subtitle: 'Search stocks and check AI predictions',
      searchPlaceholder: 'Enter ticker symbol (e.g., AAPL, 005930.KS)',
      searchButton: 'Search',
      popularTitle: 'Popular Stocks',
      popularSubtitle: 'Quick access to frequently viewed stocks',
      usStocks: 'US Stocks',
      krStocks: 'Korean Stocks',
      viewDetails: 'View Details',
      howToSearch: 'How to Search',
      searchTip1: 'US Stocks: Enter ticker symbol only (e.g., AAPL, GOOGL)',
      searchTip2: 'Korean Stocks: Use ticker.KS format (e.g., 005930.KS, 035420.KS)',
      viewMode: 'View Mode',
      gridView: 'Grid',
      treemapView: 'Treemap',
      discoveryView: 'Stock Discovery',
      predictionMap: 'AI Prediction Map',
      predictionMapSubtitle: 'Visual overview of AI trading recommendations',
      stockDiscovery: 'Stock Discovery',
      stockDiscoverySubtitle: 'Find new investment opportunities',
      filterAll: 'All',
      filterBuy: 'Buy',
      filterSell: 'Sell',
      filterHold: 'Hold',
    },
  }

  const text = t[language]

  // Filter stocks by market
  const usStocks = models.filter((s) => s.market !== 'KRX')
  const krStocks = models.filter((s) => s.market === 'KRX')

  // Count trained models
  const trainedCount = models.filter(m => m.trained).length

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">{text.title}</h1>
              <p className="text-muted-foreground mt-1">{text.subtitle}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setLanguage('ko')}
                className={`px-3 py-1 rounded-md text-sm ${
                  language === 'ko'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
              >
                한국어
              </button>
              <button
                onClick={() => setLanguage('en')}
                className={`px-3 py-1 rounded-md text-sm ${
                  language === 'en'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
              >
                English
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="max-w-2xl mx-auto mb-12">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={text.searchPlaceholder}
              className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <Button type="submit" className="px-6">
              {text.searchButton}
            </Button>
          </form>

          {/* Search Tips */}
          <div className="mt-4 p-4 bg-muted/50 rounded-lg">
            <h3 className="text-sm font-semibold mb-2">{text.howToSearch}</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• {text.searchTip1}</li>
              <li>• {text.searchTip2}</li>
            </ul>
          </div>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">로딩 중...</p>
          </div>
        ) : (
          <>
            {/* Stats */}
            <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 rounded-lg border">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold mb-1">
                    {language === 'ko' ? 'AI 학습 완료 종목' : 'AI Trained Stocks'}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {language === 'ko'
                      ? `총 ${trainedCount}개 종목에서 AI 예측이 가능합니다`
                      : `AI predictions available for ${trainedCount} stocks`}
                  </p>
                </div>
                <div className="text-4xl font-bold text-primary">
                  {trainedCount}
                </div>
              </div>
            </div>

            {/* View Toggle */}
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold">
                {viewMode === 'treemap' ? text.predictionMap : viewMode === 'discovery' ? text.stockDiscovery : text.popularTitle}
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  <LayoutGrid className="w-4 h-4" />
                  {text.gridView}
                </button>
                <button
                  onClick={() => setViewMode('treemap')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    viewMode === 'treemap'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  <Map className="w-4 h-4" />
                  {text.treemapView}
                </button>
                <button
                  onClick={() => setViewMode('discovery')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    viewMode === 'discovery'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  <Search className="w-4 h-4" />
                  {text.discoveryView}
                </button>
              </div>
            </div>

            {/* Treemap View */}
            {viewMode === 'treemap' && (
              <div className="mb-8">
                <p className="text-muted-foreground mb-4">{text.predictionMapSubtitle}</p>

                {/* Action Filter Tabs */}
                <div className="flex gap-2 mb-6">
                  {(['ALL', 'BUY', 'SELL', 'HOLD'] as const).map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setActionFilter(filter)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
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
                      {filter === 'ALL' && text.filterAll}
                      {filter === 'BUY' && text.filterBuy}
                      {filter === 'SELL' && text.filterSell}
                      {filter === 'HOLD' && text.filterHold}
                    </button>
                  ))}
                </div>

                {/* Treemap Component */}
                <StockTreemap filter={actionFilter} language={language} />
              </div>
            )}

            {/* Discovery View */}
            {viewMode === 'discovery' && (
              <div className="mb-8">
                <p className="text-muted-foreground mb-4">{text.stockDiscoverySubtitle}</p>
                <StockDiscovery />
              </div>
            )}

            {/* Grid View - Popular Stocks */}
            {viewMode === 'grid' && (
            <div className="mb-8">

              {/* US Stocks */}
              {usStocks.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold mb-4">
                    {text.usStocks} ({usStocks.filter(s => s.trained).length}/{usStocks.length} {language === 'ko' ? '학습됨' : 'Trained'})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {usStocks.map((stock) => (
                      <button
                        key={stock.ticker}
                        onClick={() => handleStockClick(stock.ticker)}
                        className="p-4 border rounded-lg hover:border-primary hover:bg-accent transition-colors text-left relative"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-bold text-lg">{stock.ticker}</p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {stock.name}
                            </p>
                          </div>
                          <span className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded">
                            {stock.market}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {stock.trained ? (
                            <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded flex items-center gap-1">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              {language === 'ko' ? 'AI 예측 가능' : 'AI Ready'}
                            </span>
                          ) : (
                            <span className="text-xs bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 px-2 py-1 rounded">
                              {language === 'ko' ? '학습 필요' : 'Training Required'}
                            </span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Korean Stocks */}
              {krStocks.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    {text.krStocks} ({krStocks.filter(s => s.trained).length}/{krStocks.length} {language === 'ko' ? '학습됨' : 'Trained'})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {krStocks.map((stock) => (
                      <button
                        key={stock.ticker}
                        onClick={() => handleStockClick(stock.ticker)}
                        className="p-4 border rounded-lg hover:border-primary hover:bg-accent transition-colors text-left relative"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-bold text-lg">{stock.ticker}</p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {stock.name}
                            </p>
                          </div>
                          <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded">
                            {stock.market}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {stock.trained ? (
                            <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded flex items-center gap-1">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              {language === 'ko' ? 'AI 예측 가능' : 'AI Ready'}
                            </span>
                          ) : (
                            <span className="text-xs bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 px-2 py-1 rounded">
                              {language === 'ko' ? '학습 필요' : 'Training Required'}
                            </span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
