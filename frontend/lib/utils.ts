import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format number as currency
 */
export function formatCurrency(value: number, currency: string = 'USD'): string {
  if (currency === 'KRW') {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(value)
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value)
}

/**
 * Format percentage
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`
}

/**
 * Format date
 */
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * Format large numbers (K, M, B)
 */
export function formatLargeNumber(value: number): string {
  if (value >= 1e9) {
    return `${(value / 1e9).toFixed(2)}B`
  }
  if (value >= 1e6) {
    return `${(value / 1e6).toFixed(2)}M`
  }
  if (value >= 1e3) {
    return `${(value / 1e3).toFixed(2)}K`
  }
  return value.toFixed(2)
}

/**
 * Check if ticker is Korean stock
 */
export function isKoreanStock(ticker: string): boolean {
  if (!ticker) return false
  return ticker.includes('.KS') || ticker.includes('.KQ')
}

/**
 * Format price based on market (KRX: KRW without decimals, US: USD with 2 decimals)
 */
export function formatPrice(value: number, ticker?: string): string {
  if (value === undefined || value === null) return '-'

  const isKRW = ticker ? isKoreanStock(ticker) : false

  if (isKRW) {
    return `₩${Math.round(value).toLocaleString()}`
  } else {
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }
}

/**
 * Format elapsed time from ISO date
 */
export function formatElapsedTime(isoDate: string | null): string {
  if (!isoDate) return '-'

  const trained = new Date(isoDate)
  const now = new Date()
  const diffMs = now.getTime() - trained.getTime()

  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 60) {
    return `${diffMinutes}분 전`
  } else if (diffHours < 24) {
    return `${diffHours}시간 전`
  } else if (diffDays < 30) {
    return `${diffDays}일 전`
  } else {
    const diffMonths = Math.floor(diffDays / 30)
    return `${diffMonths}개월 전`
  }
}

/**
 * Format datetime in Korean format
 */
export function formatDateTime(isoDate: string): string {
  if (!isoDate) return '-'

  const date = new Date(isoDate)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(date)
}

/**
 * Format time remaining until expiration
 */
export function formatTimeRemaining(expiresAt: string): string {
  if (!expiresAt) return '-'

  const expires = new Date(expiresAt)
  const now = new Date()
  const diffMs = expires.getTime() - now.getTime()

  if (diffMs < 0) return '만료됨'

  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

  if (diffMinutes < 60) {
    return `${diffMinutes}분 후 만료`
  } else {
    return `${diffHours}시간 후 만료`
  }
}
