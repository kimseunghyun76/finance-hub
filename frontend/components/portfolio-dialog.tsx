'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { portfolioApi, type Portfolio } from '@/lib/api'

interface PortfolioDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  portfolio?: Portfolio | null
  onSuccess: () => void
}

export function PortfolioDialog({
  open,
  onOpenChange,
  portfolio,
  onSuccess,
}: PortfolioDialogProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isEdit = !!portfolio

  useEffect(() => {
    if (portfolio) {
      setName(portfolio.name)
      setDescription(portfolio.description || '')
    } else {
      setName('')
      setDescription('')
    }
    setError(null)
  }, [portfolio, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (isEdit && portfolio) {
        await portfolioApi.update(portfolio.id, { name, description })
      } else {
        await portfolioApi.create({ name, description })
      }
      onSuccess()
      onOpenChange(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || '오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {isEdit ? '포트폴리오 수정' : '새 포트폴리오'}
            </DialogTitle>
            <DialogDescription>
              {isEdit
                ? '포트폴리오 정보를 수정하세요.'
                : '새로운 포트폴리오를 만들어보세요.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">이름 *</Label>
              <Input
                id="name"
                placeholder="예: 미국 기술주 포트폴리오"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">설명</Label>
              <Input
                id="description"
                placeholder="예: FAANG 중심 장기 투자"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {error && (
              <div className="text-sm text-destructive">{error}</div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              취소
            </Button>
            <Button type="submit" disabled={loading || !name}>
              {loading ? '저장 중...' : isEdit ? '수정' : '생성'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
