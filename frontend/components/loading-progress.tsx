"use client"

import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'

interface LoadingProgressProps {
  message?: string
  estimatedSeconds?: number
}

export function LoadingProgress({
  message = "데이터를 불러오는 중...",
  estimatedSeconds = 10
}: LoadingProgressProps) {
  const [progress, setProgress] = useState(0)
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    // Progress animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        // Slow down as we approach 100%
        const increment = prev < 70 ? 2 : prev < 90 ? 1 : 0.5
        return Math.min(prev + increment, 95)
      })
    }, (estimatedSeconds * 1000) / 100)

    // Elapsed time counter
    const timeInterval = setInterval(() => {
      setElapsedTime((prev) => prev + 1)
    }, 1000)

    return () => {
      clearInterval(progressInterval)
      clearInterval(timeInterval)
    }
  }, [estimatedSeconds])

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds}초`
    }
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}분 ${secs}초`
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 space-y-4">
      <Loader2 className="w-12 h-12 text-primary animate-spin" />

      <div className="text-center space-y-2">
        <p className="text-lg font-medium">{message}</p>
        <p className="text-sm text-muted-foreground">
          경과 시간: {formatTime(elapsedTime)} / 예상 시간: {formatTime(estimatedSeconds)}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="w-full max-w-md space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>진행률</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2.5 overflow-hidden">
          <div
            className="bg-primary h-full transition-all duration-300 ease-out rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {elapsedTime > estimatedSeconds && (
        <p className="text-xs text-yellow-600 dark:text-yellow-500">
          예상보다 시간이 더 걸리고 있습니다. 잠시만 기다려 주세요...
        </p>
      )}
    </div>
  )
}
