'use client'

import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { stockApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'

interface StockChartProps {
  ticker: string
  period?: '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '5y'
  currency?: 'USD' | 'KRW'
}

export function StockChart({
  ticker,
  period = '1mo',
  currency = 'USD',
}: StockChartProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [ticker, period])

  const loadData = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await stockApi.getHistory(ticker, period)
      const historyData = response.data.data

      // Format data for Recharts
      const formattedData = historyData.map((item: any) => ({
        date: new Date(item.date).toLocaleDateString('ko-KR', {
          month: 'short',
          day: 'numeric',
        }),
        price: item.close,
        high: item.high,
        low: item.low,
        volume: item.volume,
      }))

      setData(formattedData)
    } catch (err) {
      setError('차트 데이터를 불러올 수 없습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Calculate min/max for better chart scaling
  const getPriceRange = () => {
    if (data.length === 0) return [0, 100]
    const prices = data.map(d => d.price)
    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const padding = (maxPrice - minPrice) * 0.1 // 10% padding
    return [
      Math.max(0, minPrice - padding),
      maxPrice + padding
    ]
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">로딩 중...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-center">
          <p className="text-destructive">{error}</p>
          <button
            onClick={loadData}
            className="mt-2 text-sm text-primary hover:underline"
          >
            다시 시도
          </button>
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <p className="text-muted-foreground">데이터가 없습니다.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Price Chart */}
      <div className="w-full h-[250px] md:h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 5, right: 10, left: 5, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={getPriceRange()}
              tick={{ fontSize: 10 }}
              tickFormatter={(value) =>
                currency === 'KRW'
                  ? `₩${(value / 1000).toFixed(0)}K`
                  : `$${value.toFixed(0)}`
              }
              tickLine={false}
              width={60}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              formatter={(value: any) => [
                formatCurrency(value, currency),
                '종가',
              ]}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Line
              type="monotone"
              dataKey="price"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              name="종가"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Chart */}
      <div className="w-full">
        <h3 className="text-sm font-medium text-muted-foreground mb-3">거래량</h3>
        <div className="h-[120px] md:h-[160px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 5, right: 10, left: 5, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => {
                  if (value >= 1000000000) return `${(value / 1000000000).toFixed(1)}B`
                  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
                  if (value >= 1000) return `${(value / 1000).toFixed(0)}K`
                  return value.toString()
                }}
                tickLine={false}
                width={60}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                formatter={(value: any) => [
                  value.toLocaleString(),
                  '거래량',
                ]}
              />
              <Line
                type="monotone"
                dataKey="volume"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name="거래량"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
