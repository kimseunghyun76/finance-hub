'use client'

import { useState, useEffect } from 'react'
import { Star } from 'lucide-react'
import { watchlistManager } from '@/lib/watchlist'
import { Button } from './ui/button'

interface WatchlistToggleProps {
  ticker: string
  name?: string
  variant?: 'default' | 'icon'
  size?: 'sm' | 'default' | 'lg'
}

export function WatchlistToggle({ ticker, name, variant = 'default', size = 'default' }: WatchlistToggleProps) {
  const [isInWatchlist, setIsInWatchlist] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    setIsInWatchlist(watchlistManager.has(ticker))
  }, [ticker])

  useEffect(() => {
    if (!mounted) return

    const handleWatchlistUpdate = () => {
      setIsInWatchlist(watchlistManager.has(ticker))
    }

    window.addEventListener('watchlist-updated', handleWatchlistUpdate)

    return () => {
      window.removeEventListener('watchlist-updated', handleWatchlistUpdate)
    }
  }, [ticker, mounted])

  const handleToggle = () => {
    if (isInWatchlist) {
      watchlistManager.remove(ticker)
    } else {
      watchlistManager.add(ticker, name)
    }
    setIsInWatchlist(!isInWatchlist)
  }

  if (!mounted) {
    return null
  }

  if (variant === 'icon') {
    return (
      <button
        onClick={handleToggle}
        className={`transition-colors ${
          isInWatchlist
            ? 'text-yellow-500 hover:text-yellow-600'
            : 'text-gray-400 hover:text-yellow-500'
        }`}
        title={isInWatchlist ? '관심 종목에서 제거' : '관심 종목에 추가'}
      >
        <Star
          className={`w-6 h-6 ${isInWatchlist ? 'fill-current' : ''}`}
        />
      </button>
    )
  }

  return (
    <Button
      onClick={handleToggle}
      size={size}
      variant={isInWatchlist ? 'default' : 'outline'}
      className={`gap-2 ${isInWatchlist ? 'bg-yellow-500 hover:bg-yellow-600' : ''}`}
    >
      <Star className={`w-4 h-4 ${isInWatchlist ? 'fill-current' : ''}`} />
      {isInWatchlist ? '관심 종목에서 제거' : '관심 종목에 추가'}
    </Button>
  )
}
