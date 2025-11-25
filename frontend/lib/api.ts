/**
 * API client for Finance-Hub backend
 */
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Portfolio {
  id: number
  user_id: number
  name: string
  description?: string
  created_at: string
  updated_at?: string
}

export interface PortfolioWithHoldings extends Portfolio {
  holdings: Holding[]
}

export interface Holding {
  id: number
  portfolio_id: number
  ticker: string
  company_name?: string
  market: 'KRX' | 'NYSE' | 'NASDAQ'
  quantity: number
  avg_price: number
  purchase_date: string
  created_at: string
  updated_at?: string
}

export interface HoldingWithPrice extends Holding {
  current_price?: number
  total_value?: number
  total_cost?: number
  profit_loss?: number
  profit_loss_percent?: number
}

export interface StockInfo {
  ticker: string
  name: string
  sector?: string
  industry?: string
  market_cap?: number
  currency: string
}

export interface StockQuote {
  ticker: string
  current_price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
}

export interface Prediction {
  predicted_price: number
  current_price: number
  change: number
  change_percent: number
  confidence: number
  forecast_days: number
}

export interface StockPrediction {
  ticker: string
  prediction: Prediction
  action: 'BUY' | 'SELL' | 'HOLD'
  timestamp: string
  created_at: string
  expires_at: string
}

export interface AnalystRecommendation {
  strong_buy: number
  buy: number
  hold: number
  sell: number
  strong_sell: number
  period: string
}

export interface AnalystPriceTarget {
  ticker: string
  current_price: number
  target_high?: number
  target_low?: number
  target_mean?: number
  target_median?: number
  recommendation_mean?: number  // 1=Strong Buy, 5=Strong Sell
  recommendation_key?: string   // buy, hold, sell
  number_of_analysts?: number
  recommendations?: AnalystRecommendation[]
}

export interface StockFundamentals {
  ticker: string
  // Valuation metrics
  trailing_pe?: number
  forward_pe?: number
  price_to_book?: number
  price_to_sales?: number
  peg_ratio?: number
  // Profitability metrics
  return_on_equity?: number
  return_on_assets?: number
  profit_margins?: number
  operating_margins?: number
  // Growth metrics
  earnings_growth?: number
  revenue_growth?: number
  // Financial health
  debt_to_equity?: number
  current_ratio?: number
  quick_ratio?: number
  // Dividend metrics
  dividend_yield?: number
  payout_ratio?: number
  // Risk metrics
  beta?: number
  // Price range
  fifty_two_week_high?: number
  fifty_two_week_low?: number
  current_price?: number
}

// Portfolio 2.0 Analytics Types
export interface PortfolioPerformance {
  total_value: number
  total_cost: number
  total_return: number
  total_gain: number
  daily_return: number
  annualized_return: number
}

export interface PortfolioRisk {
  volatility: number
  sharpe_ratio: number
  max_drawdown: number
  beta: number
  alpha: number
  var_95: number
}

export interface PortfolioDiversification {
  sector_diversity_score: number
  geographic_diversity_score: number
  concentration_risk: number
  sector_distribution: Record<string, number>
  country_distribution: Record<string, number>
  num_holdings: number
}

export interface HoldingAnalysis {
  ticker: string
  name: string
  sector: string
  shares: number
  purchase_price: number
  current_price: number
  total_value: number
  gain: number
  gain_percent: number
  weight: number
  is_etf: number
}

export interface PortfolioAnalytics {
  performance: PortfolioPerformance
  risk: PortfolioRisk
  diversification: PortfolioDiversification
  holdings: HoldingAnalysis[]
  snapshot_date: string
}

export interface StockRecommendation {
  ticker: string
  name: string
  action: 'BUY' | 'SELL' | 'HOLD' | 'ADD' | 'REDUCE'
  confidence_score: number
  target_weight: number
  reason_category: string
  reason_detail: string
  ai_prediction_score: number
  technical_score: number
  momentum_score: number
  diversification_score: number
  current_price: number
  sector?: string
  is_etf: number
  created_at: string
  expires_at: string
}

export interface RebalanceCheck {
  needs_rebalancing: boolean
  triggers: string[]
  severity: 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH'
  severity_score: number
}

export interface RebalanceAction {
  ticker: string
  action: 'HOLD' | 'REDUCE' | 'INCREASE'
  current_weight: number
  target_weight: number
  current_shares: number
  target_shares: number
  shares_diff: number
  current_price: number
  amount: number
  reason: string
}

export interface RebalanceProposal {
  id?: number
  portfolio_id: number
  proposal_type: string
  trigger_reason: string
  current_risk_score: number
  target_risk_score: number
  current_diversification: number
  target_diversification: number
  proposed_actions: string | RebalanceAction[]
  expected_return_change: number
  expected_risk_change: number
  status: string
  created_at: string
  executed_at?: string
}

export interface PortfolioInsights {
  portfolio_id: number
  portfolio_name: string
  overall_score: number
  summary: {
    strengths: string[]
    warnings: string[]
    suggestions: string[]
  }
  analysis: PortfolioAnalytics
  top_recommendations: StockRecommendation[]
  rebalancing: RebalanceCheck
}

// Portfolio API
export const portfolioApi = {
  getAll: () => api.get<Portfolio[]>('/api/v1/portfolios'),

  getById: (id: number) => api.get<PortfolioWithHoldings>(`/api/v1/portfolios/${id}`),

  create: (data: { name: string; description?: string }) =>
    api.post<Portfolio>('/api/v1/portfolios', data),

  update: (id: number, data: { name?: string; description?: string }) =>
    api.put<Portfolio>(`/api/v1/portfolios/${id}`, data),

  delete: (id: number) => api.delete(`/api/v1/portfolios/${id}`),

  // Portfolio 2.0 Analytics
  getAnalytics: (id: number) =>
    api.get<{ success: boolean; portfolio_id: number; portfolio_name: string; analysis: PortfolioAnalytics }>(
      `/api/v1/portfolios/${id}/analytics`
    ),

  saveAnalyticsSnapshot: (id: number) =>
    api.post(`/api/v1/portfolios/${id}/analytics/snapshot`),

  getInsights: (id: number) =>
    api.get<PortfolioInsights>(`/api/v1/portfolios/${id}/insights`),

  checkRebalancing: (id: number) =>
    api.get<RebalanceCheck & { portfolio_id: number; portfolio_name: string }>(
      `/api/v1/portfolios/${id}/rebalance/check`
    ),

  proposeRebalancing: (id: number, proposalType: string = 'AUTO') =>
    api.post<{ success: boolean; message: string; proposal: RebalanceProposal | null }>(
      `/api/v1/portfolios/${id}/rebalance/propose`,
      null,
      { params: { proposal_type: proposalType } }
    ),
}

// Recommendation API
export const recommendationApi = {
  getRecommendations: (portfolioId?: number, focusSectors?: string[], maxResults: number = 10) =>
    api.get<{ success: boolean; count: number; recommendations: StockRecommendation[] }>(
      '/api/v1/recommendations',
      {
        params: {
          portfolio_id: portfolioId,
          focus_sectors: focusSectors?.join(','),
          max_results: maxResults,
        },
      }
    ),

  saveRecommendations: (portfolioId?: number, focusSectors?: string[], maxResults: number = 10) =>
    api.post('/api/v1/recommendations/save', null, {
      params: {
        portfolio_id: portfolioId,
        focus_sectors: focusSectors?.join(','),
        max_results: maxResults,
      },
    }),
}

// Holding API
export const holdingApi = {
  getByPortfolio: (portfolioId: number) =>
    api.get<Holding[]>(`/api/v1/holdings/portfolio/${portfolioId}`),

  getById: (id: number) => api.get<Holding>(`/api/v1/holdings/${id}`),

  getWithPrice: (id: number) =>
    api.get<HoldingWithPrice>(`/api/v1/holdings/${id}/with-price`),

  create: (data: {
    portfolio_id: number
    ticker: string
    company_name?: string
    market: 'KRX' | 'NYSE' | 'NASDAQ'
    quantity: number
    avg_price: number
    purchase_date: string
  }) => api.post<Holding>('/api/v1/holdings', data),

  update: (
    id: number,
    data: {
      quantity?: number
      avg_price?: number
      purchase_date?: string
    }
  ) => api.put<Holding>(`/api/v1/holdings/${id}`, data),

  delete: (id: number) => api.delete(`/api/v1/holdings/${id}`),
}

// Prediction API
export const predictionApi = {
  getTrainedModels: () => api.get<{ trained_models: string[]; count: number }>('/api/v1/predictions/'),

  getPrediction: (ticker: string) => api.get<StockPrediction>(`/api/v1/predictions/${ticker}`),

  getTrainStatus: (ticker: string) => api.get<{ ticker: string; trained: boolean; model_path: string | null }>(`/api/v1/predictions/${ticker}/train-status`),

  getModelsDetails: () => api.get<{ models: Array<{ ticker: string; trained: boolean; last_trained: string | null; file_size: number }> }>('/api/v1/predictions/models/details'),

  trainModel: (ticker: string) => api.post(`/api/v1/predictions/train/${ticker}`),

  getSummary: () => api.get('/api/v1/predictions/summary'),
}

export interface StockSearchResult {
  ticker: string
  name: string
  country: string
  sector?: string
  is_etf: boolean
  market: string
}

// Stock API
export const stockApi = {
  getInfo: (ticker: string) => api.get<StockInfo>(`/api/v1/stocks/${ticker}/info`),

  getQuote: (ticker: string) => api.get<StockQuote>(`/api/v1/stocks/${ticker}/quote`),

  getHistory: (ticker: string, period: string = '1mo') =>
    api.get(`/api/v1/stocks/${ticker}/history`, { params: { period } }),

  getPrediction: (ticker: string) => predictionApi.getPrediction(ticker),

  getAnalystTargets: (ticker: string) => api.get<AnalystPriceTarget>(`/api/v1/stocks/${ticker}/analyst-targets`),

  getFundamentals: (ticker: string) => api.get<StockFundamentals>(`/api/v1/stocks/${ticker}/fundamentals`),

  search: (query: string, limit: number = 10) =>
    api.get<{ success: boolean; query: string; count: number; results: StockSearchResult[] }>(
      '/api/v1/stocks/search',
      { params: { query, limit } }
    ),
}

// Scheduler Log Types
export interface SchedulerLog {
  id: number
  job_id: string
  job_name: string
  status: 'started' | 'completed' | 'failed'
  message: string | null
  success_count: number
  failed_count: number
  started_at: string
  completed_at: string | null
  duration_seconds: number | null
}

export interface SchedulerJob {
  id: string
  name: string
  description: string
  schedule: string
  cron: string
  next_run: string | null
  active: boolean
}

export interface SchedulerStatus {
  running: boolean
  jobs: Array<{
    id: string
    name: string
    next_run: string | null
    trigger: string
  }>
  job_count: number
}

export interface SchedulerSummary {
  period_days: number
  total_runs: number
  successful: number
  failed: number
  success_rate: number
  by_job: Array<{
    job_id: string
    job_name: string
    total_runs: number
    successful: number
    failed: number
    last_run: string | null
    avg_duration: number
  }>
}

// Scheduler API
export const schedulerApi = {
  getLogs: (params?: { job_id?: string; status?: string; days?: number; limit?: number }) =>
    api.get<{ logs: SchedulerLog[]; total: number; filters: any }>('/api/v1/scheduler/logs', { params }),

  getStatus: () => api.get<SchedulerStatus>('/api/v1/scheduler/status'),

  getJobs: () => api.get<{ scheduler_running: boolean; jobs: SchedulerJob[] }>('/api/v1/scheduler/jobs'),

  getSummary: (days: number = 7) =>
    api.get<SchedulerSummary>('/api/v1/scheduler/summary', { params: { days } }),
}

// Education types
export interface EducationArticle {
  id: number
  title: string
  category: string
  level: string
  content: string
  views: number
  created_at: string
}

export interface ChatMessage {
  role: 'student' | 'teacher'
  content: string
  emoji: string
}

// Education API
export const educationApi = {
  getArticles: (params?: { level?: string; category?: string }) =>
    api.get<EducationArticle[]>('/api/v1/education/articles', { params }),

  getArticle: (id: number) =>
    api.get<EducationArticle>(`/api/v1/education/articles/${id}`),

  generateArticle: (data: { topic: string; level: string; category?: string }) =>
    api.post<{ success: boolean; article: EducationArticle }>('/api/v1/education/articles/generate', data),

  deleteArticle: (id: number) =>
    api.delete<{ success: boolean }>(`/api/v1/education/articles/${id}`),

  markAsViewed: (articleId: number, userId?: number) =>
    api.post<{ success: boolean }>(`/api/v1/education/progress/${articleId}`, { user_id: userId }),
}

// Notification types
export interface Notification {
  id: number
  user_id: number | null
  ticker: string | null
  type: 'price_alert' | 'prediction_update' | 'rebalance_needed' | 'news' | 'portfolio_goal'
  title: string
  message: string
  severity: 'info' | 'warning' | 'success' | 'error'
  is_read: boolean
  data: string | null
  created_at: string
  read_at: string | null
}

export interface NotificationSettings {
  id: number
  user_id: number | null
  price_alert_enabled: boolean
  prediction_update_enabled: boolean
  rebalance_alert_enabled: boolean
  news_alert_enabled: boolean
  portfolio_goal_enabled: boolean
  price_change_threshold: number
  rebalance_threshold: number
}

// Notification API
export const notificationApi = {
  getAll: (params?: { user_id?: number; is_read?: boolean; type?: string; limit?: number; offset?: number }) =>
    api.get<Notification[]>('/api/v1/notifications', { params }),

  getUnreadCount: (userId?: number) =>
    api.get<{ unread_count: number }>('/api/v1/notifications/unread-count', { params: { user_id: userId } }),

  markAsRead: (id: number) =>
    api.patch<{ success: boolean; message: string }>(`/api/v1/notifications/${id}/read`),

  markAllAsRead: (userId?: number) =>
    api.patch<{ success: boolean; message: string }>('/api/v1/notifications/mark-all-read', null, { params: { user_id: userId } }),

  delete: (id: number) =>
    api.delete<{ success: boolean; message: string }>(`/api/v1/notifications/${id}`),

  getSettings: (userId?: number) =>
    api.get<NotificationSettings>('/api/v1/notifications/settings', { params: { user_id: userId } }),

  updateSettings: (data: Partial<NotificationSettings>, userId?: number) =>
    api.patch<NotificationSettings>('/api/v1/notifications/settings', data, { params: { user_id: userId } }),
}

// Investment Insight types
export interface InvestmentInsight {
  ticker: string
  buffett_analysis: string
  lynch_analysis: string
  graham_analysis: string
  overall_rating: 'BUY' | 'HOLD' | 'SELL'
  confidence_score: number
  current_price: number | null
  pe_ratio: number | null
  generated_at: string | null
  expires_at: string | null
}

// Accuracy types
export interface AccuracyMetrics {
  total_predictions: number
  correct_direction: number
  direction_accuracy: number
  avg_price_error_percent: number
  overall_score: number
}

export interface TickerAccuracy {
  ticker: string
  total_predictions: number
  direction_accuracy: number
  avg_price_error_percent: number
  overall_score: number
  last_updated: string
}

export interface TimeSeriesAccuracy {
  date: string
  predictions_count: number
  direction_accuracy: number
  avg_error_percent: number
}

export interface AccuracyDashboard {
  overall_metrics: AccuracyMetrics
  by_ticker: TickerAccuracy[]
  time_series: TimeSeriesAccuracy[]
  top_performers: TickerAccuracy[]
  worst_performers: TickerAccuracy[]
}

// Investment Insight API
export const insightApi = {
  getInsight: (ticker: string, refresh: boolean = false) =>
    api.get<InvestmentInsight>(`/api/v1/insights/${ticker}`, { params: { refresh } }),
}

// Accuracy API
export const accuracyApi = {
  getMetrics: (days: number = 30) =>
    api.get<AccuracyMetrics>('/api/v1/accuracy/metrics', { params: { days } }),

  getByTicker: (days: number = 30, minPredictions: number = 5) =>
    api.get<TickerAccuracy[]>('/api/v1/accuracy/by-ticker', { params: { days, min_predictions: minPredictions } }),

  getTimeSeries: (days: number = 30, ticker?: string) =>
    api.get<TimeSeriesAccuracy[]>('/api/v1/accuracy/time-series', { params: { days, ticker } }),

  getDashboard: (days: number = 30) =>
    api.get<AccuracyDashboard>('/api/v1/accuracy/dashboard', { params: { days } }),

  getTickerAccuracy: (ticker: string, days: number = 30) =>
    api.get<TickerAccuracy>(`/api/v1/accuracy/ticker/${ticker}`, { params: { days } }),
}

// Error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)
