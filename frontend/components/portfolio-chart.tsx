'use client'

import { useMemo, useState, useEffect } from 'react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts'
import { type HoldingWithPrice } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'

interface PortfolioChartProps {
  holdings: HoldingWithPrice[]
  currency: 'USD' | 'KRW'
}

const COLORS = [
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#06b6d4', // cyan-500
  '#84cc16', // lime-500
]

export function PortfolioChart({ holdings, currency }: PortfolioChartProps) {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const chartData = useMemo(() => {
    return holdings
      .filter((h) => h.total_value && h.total_value > 0)
      .map((holding) => ({
        name: holding.ticker,
        value: holding.total_value || 0,
        profitLoss: holding.profit_loss || 0,
        profitLossPercent: holding.profit_loss_percent || 0,
      }))
      .sort((a, b) => b.value - a.value)
  }, [holdings])

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-muted-foreground">
        데이터가 없습니다
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="font-bold mb-1">{data.name}</p>
          <p className="text-sm">
            평가액: {formatCurrency(data.value, currency)}
          </p>
          <p
            className={`text-sm ${
              data.profitLoss >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            손익: {formatCurrency(data.profitLoss, currency)} (
            {data.profitLossPercent.toFixed(2)}%)
          </p>
        </div>
      )
    }
    return null
  }

  const chartHeight = isMobile ? 300 : 400
  const outerRadius = isMobile ? 80 : 120
  const fontSize = isMobile ? 11 : 14

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={isMobile ? false : ({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={outerRadius}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: `${fontSize}px` }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
