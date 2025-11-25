'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { portfolioApi, type RebalanceCheck, type RebalanceProposal, type RebalanceAction } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { formatCurrency, formatPercent } from '@/lib/utils'

interface Props {
  params: {
    id: string
  }
}

export default function RebalancePage({ params }: Props) {
  const router = useRouter()
  const portfolioId = parseInt(params.id)
  const [portfolioName, setPortfolioName] = useState('')
  const [rebalanceCheck, setRebalanceCheck] = useState<RebalanceCheck | null>(null)
  const [proposal, setProposal] = useState<RebalanceProposal | null>(null)
  const [loading, setLoading] = useState(true)
  const [proposing, setProposing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadRebalanceStatus()
  }, [portfolioId])

  const loadRebalanceStatus = async () => {
    try {
      setLoading(true)
      const response = await portfolioApi.checkRebalancing(portfolioId)
      setRebalanceCheck(response.data)
      setPortfolioName(response.data.portfolio_name || '')
      setError(null)
    } catch (err) {
      setError('리밸런싱 상태를 불러오는 중 오류가 발생했습니다.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const generateProposal = async () => {
    try {
      setProposing(true)
      const response = await portfolioApi.proposeRebalancing(portfolioId, 'AUTO')
      if (response.data.success && response.data.proposal) {
        setProposal(response.data.proposal)
        setError(null)
      } else {
        setError(response.data.message || '리밸런싱 제안을 생성할 수 없습니다.')
      }
    } catch (err) {
      setError('리밸런싱 제안을 생성하는 중 오류가 발생했습니다.')
      console.error(err)
    } finally {
      setProposing(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (error && !rebalanceCheck) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center text-red-600">{error}</div>
      </div>
    )
  }

  const parsedActions: RebalanceAction[] = proposal?.proposed_actions
    ? typeof proposal.proposed_actions === 'string'
      ? JSON.parse(proposal.proposed_actions)
      : proposal.proposed_actions
    : []

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return 'border-red-500 bg-red-50'
      case 'MEDIUM':
        return 'border-amber-500 bg-amber-50'
      case 'LOW':
        return 'border-blue-500 bg-blue-50'
      default:
        return 'border-gray-300 bg-gray-50'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return <AlertTriangle className="h-6 w-6 text-red-600" />
      case 'MEDIUM':
        return <AlertTriangle className="h-6 w-6 text-amber-600" />
      case 'LOW':
        return <CheckCircle2 className="h-6 w-6 text-blue-600" />
      default:
        return <CheckCircle2 className="h-6 w-6 text-gray-600" />
    }
  }

  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return '높음 - 즉시 리밸런싱 권장'
      case 'MEDIUM':
        return '보통 - 리밸런싱 검토 필요'
      case 'LOW':
        return '낮음 - 선택적 리밸런싱'
      default:
        return '없음 - 리밸런싱 불필요'
    }
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push(`/portfolios/${portfolioId}`)}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          포트폴리오로 돌아가기
        </Button>
      </div>

      <div>
        <h1 className="text-3xl font-bold">포트폴리오 리밸런싱</h1>
        <p className="text-muted-foreground mt-2">{portfolioName}</p>
      </div>

      {/* Rebalancing Status Card */}
      <Card className={`border-2 ${getSeverityColor(rebalanceCheck?.severity || 'NONE')}`}>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-2xl flex items-center gap-2">
                {getSeverityIcon(rebalanceCheck?.severity || 'NONE')}
                리밸런싱 상태
              </CardTitle>
              <CardDescription className="text-base">
                {getSeverityText(rebalanceCheck?.severity || 'NONE')}
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">
                {rebalanceCheck?.severity_score?.toFixed(0) || 0}
              </div>
              <div className="text-xs text-muted-foreground">심각도 점수</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {rebalanceCheck?.needs_rebalancing ? (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">🚨 감지된 문제</h3>
                <ul className="space-y-1">
                  {rebalanceCheck.triggers.map((trigger, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-4">
                      • {trigger}
                    </li>
                  ))}
                </ul>
              </div>

              {!proposal && (
                <Button
                  onClick={generateProposal}
                  disabled={proposing}
                  className="w-full mt-4"
                >
                  {proposing ? '제안 생성 중...' : '리밸런싱 제안 생성하기'}
                </Button>
              )}
            </div>
          ) : (
            <div className="text-center py-6">
              <CheckCircle2 className="h-12 w-12 text-green-600 mx-auto mb-2" />
              <p className="text-lg font-medium">포트폴리오가 균형 잡힌 상태입니다</p>
              <p className="text-sm text-muted-foreground mt-1">
                현재 리밸런싱이 필요하지 않습니다.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Rebalancing Proposal */}
      {proposal && (
        <>
          {/* Expected Impact */}
          <Card>
            <CardHeader>
              <CardTitle>📊 예상 효과</CardTitle>
              <CardDescription>리밸런싱 후 예상되는 포트폴리오 변화</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs text-muted-foreground">리스크 점수 변화</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-lg font-bold">
                      {proposal.current_risk_score.toFixed(1)} → {proposal.target_risk_score.toFixed(1)}
                    </span>
                    {proposal.expected_risk_change < 0 ? (
                      <TrendingDown className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingUp className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                  <div
                    className={`text-xs ${
                      proposal.expected_risk_change < 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {proposal.expected_risk_change > 0 ? '+' : ''}
                    {proposal.expected_risk_change.toFixed(1)}%
                  </div>
                </div>

                <div>
                  <div className="text-xs text-muted-foreground">다각화 점수 변화</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-lg font-bold">
                      {proposal.current_diversification.toFixed(1)} →{' '}
                      {proposal.target_diversification.toFixed(1)}
                    </span>
                    {proposal.target_diversification > proposal.current_diversification ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                  <div
                    className={`text-xs ${
                      proposal.target_diversification > proposal.current_diversification
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {proposal.target_diversification > proposal.current_diversification ? '+' : ''}
                    {(proposal.target_diversification - proposal.current_diversification).toFixed(1)}
                  </div>
                </div>

                <div>
                  <div className="text-xs text-muted-foreground">예상 수익률 변화</div>
                  <div className="text-lg font-bold mt-1">
                    {proposal.expected_return_change > 0 ? '+' : ''}
                    {proposal.expected_return_change.toFixed(2)}%
                  </div>
                  <div
                    className={`text-xs ${
                      proposal.expected_return_change > 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {proposal.expected_return_change > 0 ? '수익률 증가' : '수익률 감소'}
                  </div>
                </div>

                <div>
                  <div className="text-xs text-muted-foreground">제안 유형</div>
                  <div className="text-lg font-bold mt-1">{proposal.proposal_type}</div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(proposal.created_at).toLocaleDateString('ko-KR')}
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-muted rounded-lg">
                <div className="text-sm font-medium mb-1">트리거 원인</div>
                <div className="text-sm text-muted-foreground">{proposal.trigger_reason}</div>
              </div>
            </CardContent>
          </Card>

          {/* Proposed Actions */}
          <Card>
            <CardHeader>
              <CardTitle>🎯 제안된 조치사항</CardTitle>
              <CardDescription>
                포트폴리오 균형을 맞추기 위한 매수/매도 조치 ({parsedActions.length}개 종목)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {parsedActions.map((action, idx) => (
                  <div
                    key={idx}
                    className="border rounded-lg p-4 bg-card hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-bold text-lg">{action.ticker}</span>
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              action.action === 'INCREASE'
                                ? 'bg-green-100 text-green-700'
                                : action.action === 'REDUCE'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {action.action === 'INCREASE'
                              ? '매수'
                              : action.action === 'REDUCE'
                              ? '매도'
                              : '유지'}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          <div>
                            <div className="text-xs text-muted-foreground">현재 비중</div>
                            <div className="font-medium">
                              {formatPercent(action.current_weight)}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-muted-foreground">목표 비중</div>
                            <div className="font-medium">{formatPercent(action.target_weight)}</div>
                          </div>
                          <div>
                            <div className="text-xs text-muted-foreground">현재 수량</div>
                            <div className="font-medium">{action.current_shares}주</div>
                          </div>
                          <div>
                            <div className="text-xs text-muted-foreground">목표 수량</div>
                            <div className="font-medium">{action.target_shares}주</div>
                          </div>
                        </div>

                        <div className="mt-3 flex items-center gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">수량 변화: </span>
                            <span
                              className={`font-medium ${
                                action.shares_diff > 0
                                  ? 'text-green-600'
                                  : action.shares_diff < 0
                                  ? 'text-red-600'
                                  : 'text-gray-600'
                              }`}
                            >
                              {action.shares_diff > 0 ? '+' : ''}
                              {action.shares_diff}주
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">금액: </span>
                            <span
                              className={`font-medium ${
                                action.amount > 0
                                  ? 'text-green-600'
                                  : action.amount < 0
                                  ? 'text-red-600'
                                  : 'text-gray-600'
                              }`}
                            >
                              {formatCurrency(Math.abs(action.amount), 'USD')}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">현재가: </span>
                            <span className="font-medium">
                              {formatCurrency(action.current_price, 'USD')}
                            </span>
                          </div>
                        </div>

                        <div className="mt-2 text-xs text-muted-foreground">
                          사유: {action.reason}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 mt-6">
                <Button variant="outline" className="flex-1" onClick={() => setProposal(null)}>
                  취소
                </Button>
                <Button
                  variant="default"
                  className="flex-1"
                  onClick={() => alert('리밸런싱 실행 기능은 곧 추가됩니다.')}
                >
                  리밸런싱 실행
                </Button>
              </div>

              <p className="text-xs text-muted-foreground text-center mt-3">
                * 실제 매매는 수동으로 진행해야 하며, 이 제안은 참고용입니다.
              </p>
            </CardContent>
          </Card>
        </>
      )}

      {error && proposal && (
        <div className="text-center text-red-600 text-sm">{error}</div>
      )}
    </div>
  )
}
