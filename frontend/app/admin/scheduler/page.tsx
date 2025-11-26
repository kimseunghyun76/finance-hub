'use client'

import { useState, useEffect } from 'react'
import { schedulerApi, SchedulerLog, SchedulerJob, SchedulerSummary } from '@/lib/api'
import { RefreshCw, Clock, CheckCircle, XCircle, PlayCircle, AlertCircle, Calendar, Timer, Activity } from 'lucide-react'

export default function SchedulerPage() {
  const [logs, setLogs] = useState<SchedulerLog[]>([])
  const [jobs, setJobs] = useState<SchedulerJob[]>([])
  const [summary, setSummary] = useState<SchedulerSummary | null>(null)
  const [schedulerRunning, setSchedulerRunning] = useState(false)
  const [loading, setLoading] = useState(true)
  const [selectedJobId, setSelectedJobId] = useState<string>('')
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  useEffect(() => {
    loadData()
  }, [selectedJobId, selectedStatus])

  const loadData = async () => {
    setLoading(true)
    try {
      const [logsRes, jobsRes, summaryRes] = await Promise.all([
        schedulerApi.getLogs({
          job_id: selectedJobId || undefined,
          status: selectedStatus || undefined,
          days: 7,
          limit: 100,
        }),
        schedulerApi.getJobs(),
        schedulerApi.getSummary(7),
      ])

      setLogs(logsRes.data.logs)
      setJobs(jobsRes.data.jobs)
      setSchedulerRunning(jobsRes.data.scheduler_running)
      setSummary(summaryRes.data)
    } catch (error) {
      console.error('Failed to load scheduler data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-'
    if (seconds < 60) return `${seconds}초`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}분 ${seconds % 60}초`
    return `${Math.floor(seconds / 3600)}시간 ${Math.floor((seconds % 3600) / 60)}분`
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
            <CheckCircle className="w-3 h-3" />
            완료
          </span>
        )
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
            <XCircle className="w-3 h-3" />
            실패
          </span>
        )
      case 'started':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            <PlayCircle className="w-3 h-3" />
            실행중
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400">
            {status}
          </span>
        )
    }
  }

  // Get next scheduled job
  const getNextJob = () => {
    const now = new Date()
    const upcomingJobs = jobs
      .filter(j => j.next_run && j.active)
      .map(j => ({ ...j, nextRunDate: new Date(j.next_run!) }))
      .sort((a, b) => a.nextRunDate.getTime() - b.nextRunDate.getTime())
    return upcomingJobs[0] || null
  }

  const nextJob = getNextJob()

  // Get time until next job
  const getTimeUntilNext = () => {
    if (!nextJob?.next_run) return null
    const now = new Date()
    const next = new Date(nextJob.next_run)
    const diffMs = next.getTime() - now.getTime()
    if (diffMs < 0) return '곧 실행'
    const hours = Math.floor(diffMs / (1000 * 60 * 60))
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
    if (hours > 0) return `${hours}시간 ${minutes}분 후`
    return `${minutes}분 후`
  }

  // Get daily stats from summary
  const getDailyStats = () => {
    if (!summary?.by_job) return []
    return summary.by_job
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">스케줄러 관리</h1>
          <p className="text-muted-foreground mt-1">
            자동 작업 스케줄 및 실행 로그
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
            schedulerRunning
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${schedulerRunning ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            {schedulerRunning ? '실행중' : '중지됨'}
          </div>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 rounded-lg border hover:bg-accent transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Schedule Timeline - NEW TOP SECTION */}
      <div className="mb-6 p-6 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Timer className="w-5 h-5" />
          스케줄 타임라인
        </h2>

        {/* Next Job Highlight */}
        {nextJob && (
          <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">다음 예정 작업</p>
                <p className="text-xl font-bold mt-1">{nextJob.name}</p>
                <p className="text-sm text-muted-foreground mt-1">{nextJob.description}</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{getTimeUntilNext()}</p>
                <p className="text-sm text-muted-foreground mt-1">{formatDate(nextJob.next_run!)}</p>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {jobs.filter(j => j.active).map((job) => (
            <div key={job.id} className="p-3 bg-white dark:bg-gray-800 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-sm truncate" title={job.name}>{job.name}</h4>
                <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 rounded">
                  {job.schedule}
                </span>
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                {job.next_run ? formatDate(job.next_run) : '대기 중'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 border rounded-lg bg-card">
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <Calendar className="w-4 h-4" />
              최근 7일 실행
            </div>
            <p className="text-2xl font-bold mt-2">{summary.total_runs}회</p>
          </div>
          <div className="p-4 border rounded-lg bg-card">
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <CheckCircle className="w-4 h-4 text-green-500" />
              성공
            </div>
            <p className="text-2xl font-bold mt-2 text-green-600">{summary.successful}회</p>
          </div>
          <div className="p-4 border rounded-lg bg-card">
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <XCircle className="w-4 h-4 text-red-500" />
              실패
            </div>
            <p className="text-2xl font-bold mt-2 text-red-600">{summary.failed}회</p>
          </div>
          <div className="p-4 border rounded-lg bg-card">
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <AlertCircle className="w-4 h-4" />
              성공률
            </div>
            <p className="text-2xl font-bold mt-2">{summary.success_rate}%</p>
          </div>
        </div>
      )}

      {/* Job Performance Table - Daily Results */}
      {summary && summary.by_job && summary.by_job.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            작업별 실행 현황 (최근 7일)
          </h2>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">작업명</th>
                  <th className="px-4 py-3 text-center text-sm font-medium">총 실행</th>
                  <th className="px-4 py-3 text-center text-sm font-medium">성공</th>
                  <th className="px-4 py-3 text-center text-sm font-medium">실패</th>
                  <th className="px-4 py-3 text-center text-sm font-medium">성공률</th>
                  <th className="px-4 py-3 text-center text-sm font-medium">평균 소요시간</th>
                  <th className="px-4 py-3 text-center text-sm font-medium">최근 실행</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {summary.by_job.map((job) => {
                  const successRate = job.total_runs > 0
                    ? ((job.successful / job.total_runs) * 100).toFixed(1)
                    : '0'
                  return (
                    <tr key={job.job_id} className="hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <span className="font-medium">{job.job_name}</span>
                      </td>
                      <td className="px-4 py-3 text-center">{job.total_runs}회</td>
                      <td className="px-4 py-3 text-center text-green-600 font-medium">{job.successful}회</td>
                      <td className="px-4 py-3 text-center text-red-600 font-medium">{job.failed}회</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          parseFloat(successRate) >= 90 ? 'bg-green-100 text-green-700' :
                          parseFloat(successRate) >= 70 ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {successRate}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-muted-foreground">
                        {formatDuration(job.avg_duration)}
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-muted-foreground">
                        {job.last_run ? formatDate(job.last_run) : '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Scheduled Jobs - Now below timeline */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-3">예약된 작업 상세</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <div key={job.id} className="p-4 border rounded-lg bg-card">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium">{job.name}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{job.description}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  job.active
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-gray-100 text-gray-500 dark:bg-gray-800'
                }`}>
                  {job.active ? '활성' : '비활성'}
                </span>
              </div>
              <div className="mt-3 pt-3 border-t space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">스케줄:</span>
                  <span>{job.schedule}</span>
                </div>
                {job.next_run && (
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">다음 실행:</span>
                    <span>{formatDate(job.next_run)}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-4">
        <select
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
          className="px-3 py-2 border rounded-lg bg-background text-sm"
        >
          <option value="">모든 작업</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.name}
            </option>
          ))}
        </select>
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="px-3 py-2 border rounded-lg bg-background text-sm"
        >
          <option value="">모든 상태</option>
          <option value="completed">완료</option>
          <option value="failed">실패</option>
          <option value="started">실행중</option>
        </select>
      </div>

      {/* Logs Table */}
      <div className="border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">작업</th>
                <th className="px-4 py-3 text-left text-sm font-medium">상태</th>
                <th className="px-4 py-3 text-left text-sm font-medium">시작 시간</th>
                <th className="px-4 py-3 text-left text-sm font-medium">소요 시간</th>
                <th className="px-4 py-3 text-left text-sm font-medium">성공/실패</th>
                <th className="px-4 py-3 text-left text-sm font-medium">메시지</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
                    로딩 중...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    실행 로그가 없습니다.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-muted/30">
                    <td className="px-4 py-3">
                      <div>
                        <span className="font-medium">{log.job_name}</span>
                        <span className="text-xs text-muted-foreground ml-2">({log.job_id})</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(log.status)}</td>
                    <td className="px-4 py-3 text-sm">{formatDate(log.started_at)}</td>
                    <td className="px-4 py-3 text-sm">{formatDuration(log.duration_seconds)}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="text-green-600">{log.success_count}</span>
                      {' / '}
                      <span className="text-red-600">{log.failed_count}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground max-w-xs truncate">
                      {log.message || '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
