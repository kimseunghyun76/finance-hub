'use client'

import { Button } from '@/components/ui/button'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

interface ModelTableRowProps {
  ticker: string
  name: string
  description?: string
  category?: string
  trained: boolean
  training: boolean
  lastTrained: string | null
  fileSize: number
  onTrain: () => void
  onDelete: () => void
}

export function ModelTableRow({
  ticker,
  name,
  description,
  category,
  trained,
  training,
  lastTrained,
  fileSize,
  onTrain,
  onDelete
}: ModelTableRowProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '-'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <tr className="hover:bg-muted/30 transition-colors">
      <td className="px-4 py-3">
        <span className="font-mono font-medium">{ticker}</span>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{name}</span>
          {category === 'popular' && (
            <span className="text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 px-2 py-0.5 rounded">
              인기
            </span>
          )}
        </div>
      </td>
      {description && (
        <td className="px-4 py-3">
          <span className="text-xs text-muted-foreground">{description}</span>
        </td>
      )}
      <td className="px-4 py-3 text-center">
        {training ? (
          <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
            <svg className="animate-spin -ml-1 mr-2 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            훈련 중
          </span>
        ) : trained ? (
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
        {lastTrained ? (
          formatDistanceToNow(new Date(lastTrained), {
            addSuffix: true,
            locale: ko,
          })
        ) : (
          '-'
        )}
      </td>
      <td className="px-4 py-3 text-right text-sm text-muted-foreground">
        {formatFileSize(fileSize)}
      </td>
      <td className="px-4 py-3 text-right">
        <div className="flex gap-2 justify-end">
          <Button
            size="sm"
            variant={trained ? "outline" : "default"}
            onClick={onTrain}
            disabled={training}
          >
            {trained ? '재훈련' : '훈련'}
          </Button>
          {trained && (
            <Button
              size="sm"
              variant="destructive"
              onClick={onDelete}
            >
              삭제
            </Button>
          )}
        </div>
      </td>
    </tr>
  )
}
