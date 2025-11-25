'use client'

import { useState, useEffect } from 'react'
import { portfolioApi, type Portfolio } from '@/lib/api'
import { Button } from './ui/button'

interface PortfolioEditDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  portfolio: Portfolio | null
  onSuccess: () => void
}

export function PortfolioEditDialog({
  open,
  onOpenChange,
  portfolio,
  onSuccess,
}: PortfolioEditDialogProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (portfolio) {
      setName(portfolio.name)
      setDescription(portfolio.description || '')
    }
  }, [portfolio])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!portfolio) return

    if (!name.trim()) {
      setError('포트폴리오 이름을 입력해주세요')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await portfolioApi.update(portfolio.id, {
        name: name.trim(),
        description: description.trim() || undefined,
      })

      setName('')
      setDescription('')
      onSuccess()
      onOpenChange(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || '포트폴리오 수정에 실패했습니다')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!portfolio) return

    setLoading(true)
    setError(null)

    try {
      await portfolioApi.delete(portfolio.id)
      setShowDeleteConfirm(false)
      onSuccess()
      onOpenChange(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || '포트폴리오 삭제에 실패했습니다')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (!open || !portfolio) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-background rounded-lg p-6 w-full max-w-md border shadow-lg">
        {showDeleteConfirm ? (
          <>
            <h2 className="text-xl font-bold mb-4 text-destructive">
              포트폴리오 삭제
            </h2>
            <p className="text-muted-foreground mb-6">
              정말로 &quot;{portfolio.name}&quot; 포트폴리오를 삭제하시겠습니까?
              <br />
              <strong className="text-destructive">
                포트폴리오와 모든 보유 종목이 삭제됩니다.
              </strong>
            </p>

            {error && (
              <div className="mb-4 p-3 bg-destructive/10 border border-destructive rounded-md">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={loading}
                className="flex-1"
              >
                취소
              </Button>
              <Button
                type="button"
                onClick={handleDelete}
                disabled={loading}
                className="flex-1 bg-destructive hover:bg-destructive/90"
              >
                {loading ? '삭제 중...' : '삭제'}
              </Button>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-xl font-bold mb-4">포트폴리오 수정</h2>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    포트폴리오 이름 *
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="예: 내 주식 포트폴리오"
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    설명 (선택)
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="포트폴리오에 대한 설명을 입력하세요"
                    rows={3}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    disabled={loading}
                  />
                </div>

                {error && (
                  <div className="p-3 bg-destructive/10 border border-destructive rounded-md">
                    <p className="text-sm text-destructive">{error}</p>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => onOpenChange(false)}
                    disabled={loading}
                    className="flex-1"
                  >
                    취소
                  </Button>
                  <Button type="submit" disabled={loading} className="flex-1">
                    {loading ? '저장 중...' : '저장'}
                  </Button>
                </div>

                <div className="pt-4 border-t">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(true)}
                    disabled={loading}
                    className="w-full text-destructive hover:bg-destructive/10"
                  >
                    포트폴리오 삭제
                  </Button>
                </div>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
