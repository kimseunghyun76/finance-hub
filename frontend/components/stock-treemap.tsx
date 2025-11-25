"use client"

import { useEffect, useState } from 'react'
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'

interface StockPrediction {
  ticker: string
  name: string
  action: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  change_percent: number
  predicted_price: number
  current_price: number
  sector: string
  market_cap: number
  market: 'KRX' | 'US'
}

interface TreemapData {
  name: string
  size: number
  ticker: string
  action: 'BUY' | 'SELL' | 'HOLD'
  change_percent: number
  confidence: number
  current_price: number
  predicted_price: number
}

interface CustomContentProps {
  x?: number
  y?: number
  width?: number
  height?: number
  name?: string
  ticker?: string
  action?: 'BUY' | 'SELL' | 'HOLD'
  change_percent?: number
}

const CustomContent: React.FC<CustomContentProps> = ({
  x = 0,
  y = 0,
  width = 0,
  height = 0,
  name = '',
  ticker = '',
  action = 'HOLD',
  change_percent = 0
}) => {
  // Don't render if too small
  if (width < 40 || height < 30) return null

  // Color based on action
  const getColor = () => {
    switch (action) {
      case 'BUY':
        return { bg: '#22c55e', text: '#ffffff' }
      case 'SELL':
        return { bg: '#ef4444', text: '#ffffff' }
      case 'HOLD':
        return { bg: '#94a3b8', text: '#ffffff' }
      default:
        return { bg: '#94a3b8', text: '#ffffff' }
    }
  }

  const colors = getColor()
  const fontSize = Math.min(width / 8, height / 4, 14)
  const showDetails = width > 80 && height > 50

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: colors.bg,
          stroke: '#fff',
          strokeWidth: 2,
          strokeOpacity: 1,
        }}
      />
      <text
        x={x + width / 2}
        y={y + height / 2 - (showDetails ? 10 : 0)}
        textAnchor="middle"
        fill={colors.text}
        fontSize={fontSize}
        fontWeight="bold"
      >
        {name}
      </text>
      {showDetails && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2 + 8}
            textAnchor="middle"
            fill={colors.text}
            fontSize={fontSize * 0.7}
          >
            {change_percent > 0 ? '+' : ''}{change_percent.toFixed(1)}%
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2 + 20}
            textAnchor="middle"
            fill={colors.text}
            fontSize={fontSize * 0.6}
            opacity={0.9}
          >
            {action}
          </text>
        </>
      )}
    </g>
  )
}

const CustomTooltip = ({ active, payload, language = 'en' }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
        <p className="font-bold text-sm">{data.name}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400 font-mono">{data.ticker}</p>
        <div className="mt-2 space-y-1">
          <p className="text-xs">
            <span className="font-semibold">
              {language === 'ko' ? '의견' : 'Action'}:
            </span>{' '}
            <span className={`font-bold ${
              data.action === 'BUY' ? 'text-green-600' :
              data.action === 'SELL' ? 'text-red-600' :
              'text-gray-600'
            }`}>
              {data.action}
            </span>
          </p>
          <p className="text-xs">
            <span className="font-semibold">
              {language === 'ko' ? '예상 변화율' : 'Change'}:
            </span>{' '}
            <span className={data.change_percent > 0 ? 'text-green-600' : 'text-red-600'}>
              {data.change_percent > 0 ? '+' : ''}{data.change_percent.toFixed(2)}%
            </span>
          </p>
          <p className="text-xs">
            <span className="font-semibold">
              {language === 'ko' ? '현재가' : 'Current'}:
            </span>{' '}
            ${data.current_price.toFixed(2)}
          </p>
          <p className="text-xs">
            <span className="font-semibold">
              {language === 'ko' ? '예상가' : 'Predicted'}:
            </span>{' '}
            ${data.predicted_price.toFixed(2)}
          </p>
          <p className="text-xs">
            <span className="font-semibold">
              {language === 'ko' ? '신뢰도' : 'Confidence'}:
            </span>{' '}
            {(data.confidence * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    )
  }
  return null
}

interface StockTreemapProps {
  filter?: 'ALL' | 'BUY' | 'SELL' | 'HOLD'
  language?: 'ko' | 'en'
}

export default function StockTreemap({ filter = 'ALL', language = 'en' }: StockTreemapProps) {
  const [data, setData] = useState<TreemapData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://localhost:8001/api/v1/predictions/summary')
        if (!response.ok) throw new Error('Failed to fetch predictions')

        const result = await response.json()

        // Filter predictions based on filter prop
        let predictions: StockPrediction[] = result.predictions || []
        if (filter !== 'ALL') {
          predictions = predictions.filter((p: StockPrediction) => p.action === filter)
        }

        // Transform to treemap format
        const treemapData: TreemapData[] = predictions.map((p: StockPrediction) => ({
          name: p.name,
          // Use absolute change_percent for size to ensure positive values
          size: Math.abs(p.change_percent) || 1, // Minimum size of 1 to ensure visibility
          ticker: p.ticker,
          action: p.action,
          change_percent: p.change_percent,
          confidence: p.confidence,
          current_price: p.current_price,
          predicted_price: p.predicted_price,
        }))

        setData(treemapData)
        setError(null)
      } catch (err) {
        console.error('Error fetching predictions:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
  }, [filter])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">
            {language === 'ko' ? '예측 데이터 로딩 중...' : 'Loading predictions...'}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center text-red-500">
          <p className="font-semibold">{language === 'ko' ? '오류 발생' : 'Error'}</p>
          <p className="text-sm mt-2">{error}</p>
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <p className="font-semibold">
            {language === 'ko' ? '데이터가 없습니다' : 'No data available'}
          </p>
          <p className="text-sm mt-2">
            {language === 'ko'
              ? '학습된 모델이 없거나 예측 데이터가 없습니다.'
              : 'No trained models or prediction data available.'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-[600px]">
      <ResponsiveContainer width="100%" height="100%">
        <Treemap
          data={data}
          dataKey="size"
          stroke="#fff"
          fill="#8884d8"
          content={<CustomContent />}
        >
          <Tooltip content={<CustomTooltip language={language} />} />
        </Treemap>
      </ResponsiveContainer>
    </div>
  )
}
