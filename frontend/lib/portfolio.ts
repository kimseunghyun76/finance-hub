/**
 * Portfolio simulation manager using local storage
 */

export interface PortfolioPosition {
  ticker: string
  name: string
  shares: number
  avgPrice: number
  currentPrice: number
  totalCost: number
  currentValue: number
  profit: number
  profitPercent: number
  purchaseDate: string
}

export interface Transaction {
  id: string
  ticker: string
  type: 'BUY' | 'SELL'
  shares: number
  price: number
  total: number
  date: string
  aiRecommendation?: boolean
}

export interface PortfolioState {
  cash: number
  initialCash: number
  positions: PortfolioPosition[]
  transactions: Transaction[]
  totalValue: number
  totalProfit: number
  totalProfitPercent: number
}

const PORTFOLIO_KEY = 'finance-hub-portfolio'
const INITIAL_CASH = 100000 // $100,000 starting capital

export const portfolioManager = {
  /**
   * Get current portfolio state
   */
  getPortfolio: (): PortfolioState => {
    if (typeof window === 'undefined') {
      return {
        cash: INITIAL_CASH,
        initialCash: INITIAL_CASH,
        positions: [],
        transactions: [],
        totalValue: INITIAL_CASH,
        totalProfit: 0,
        totalProfitPercent: 0
      }
    }

    try {
      const data = localStorage.getItem(PORTFOLIO_KEY)
      if (!data) {
        return portfolioManager.initializePortfolio()
      }

      const portfolio: PortfolioState = JSON.parse(data)
      return portfolio
    } catch (error) {
      console.error('Failed to load portfolio:', error)
      return portfolioManager.initializePortfolio()
    }
  },

  /**
   * Initialize new portfolio
   */
  initializePortfolio: (): PortfolioState => {
    const portfolio: PortfolioState = {
      cash: INITIAL_CASH,
      initialCash: INITIAL_CASH,
      positions: [],
      transactions: [],
      totalValue: INITIAL_CASH,
      totalProfit: 0,
      totalProfitPercent: 0
    }

    portfolioManager.savePortfolio(portfolio)
    return portfolio
  },

  /**
   * Save portfolio to local storage
   */
  savePortfolio: (portfolio: PortfolioState): void => {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem(PORTFOLIO_KEY, JSON.stringify(portfolio))
      window.dispatchEvent(new CustomEvent('portfolio-updated'))
    } catch (error) {
      console.error('Failed to save portfolio:', error)
    }
  },

  /**
   * Buy stock
   */
  buyStock: (
    ticker: string,
    name: string,
    shares: number,
    price: number,
    aiRecommendation: boolean = false
  ): { success: boolean; error?: string } => {
    const portfolio = portfolioManager.getPortfolio()
    const total = shares * price

    if (total > portfolio.cash) {
      return { success: false, error: '현금이 부족합니다' }
    }

    // Create transaction
    const transaction: Transaction = {
      id: Date.now().toString(),
      ticker,
      type: 'BUY',
      shares,
      price,
      total,
      date: new Date().toISOString(),
      aiRecommendation
    }

    // Update or create position
    const existingPosition = portfolio.positions.find(p => p.ticker === ticker)

    if (existingPosition) {
      // Update existing position (average price)
      const newTotalShares = existingPosition.shares + shares
      const newAvgPrice = (existingPosition.totalCost + total) / newTotalShares

      existingPosition.shares = newTotalShares
      existingPosition.avgPrice = newAvgPrice
      existingPosition.totalCost += total
      existingPosition.currentPrice = price
      existingPosition.currentValue = newTotalShares * price
      existingPosition.profit = existingPosition.currentValue - existingPosition.totalCost
      existingPosition.profitPercent = (existingPosition.profit / existingPosition.totalCost) * 100
    } else {
      // Create new position
      portfolio.positions.push({
        ticker,
        name,
        shares,
        avgPrice: price,
        currentPrice: price,
        totalCost: total,
        currentValue: total,
        profit: 0,
        profitPercent: 0,
        purchaseDate: new Date().toISOString()
      })
    }

    // Update cash
    portfolio.cash -= total

    // Add transaction
    portfolio.transactions.unshift(transaction)

    // Recalculate totals
    portfolioManager.recalculateTotals(portfolio)

    portfolioManager.savePortfolio(portfolio)

    return { success: true }
  },

  /**
   * Sell stock
   */
  sellStock: (
    ticker: string,
    shares: number,
    price: number,
    aiRecommendation: boolean = false
  ): { success: boolean; error?: string } => {
    const portfolio = portfolioManager.getPortfolio()
    const position = portfolio.positions.find(p => p.ticker === ticker)

    if (!position) {
      return { success: false, error: '보유하고 있지 않은 종목입니다' }
    }

    if (shares > position.shares) {
      return { success: false, error: '보유 수량이 부족합니다' }
    }

    const total = shares * price

    // Create transaction
    const transaction: Transaction = {
      id: Date.now().toString(),
      ticker,
      type: 'SELL',
      shares,
      price,
      total,
      date: new Date().toISOString(),
      aiRecommendation
    }

    // Update position
    position.shares -= shares
    position.totalCost -= (position.avgPrice * shares)
    position.currentValue = position.shares * price
    position.profit = position.currentValue - position.totalCost
    position.profitPercent = position.totalCost > 0
      ? (position.profit / position.totalCost) * 100
      : 0

    // Remove position if fully sold
    if (position.shares === 0) {
      portfolio.positions = portfolio.positions.filter(p => p.ticker !== ticker)
    }

    // Update cash
    portfolio.cash += total

    // Add transaction
    portfolio.transactions.unshift(transaction)

    // Recalculate totals
    portfolioManager.recalculateTotals(portfolio)

    portfolioManager.savePortfolio(portfolio)

    return { success: true }
  },

  /**
   * Update current prices for all positions
   */
  updatePrices: async (positions: PortfolioPosition[]): Promise<PortfolioPosition[]> => {
    const updatedPositions = await Promise.all(
      positions.map(async (position) => {
        try {
          const response = await fetch(`http://localhost:8001/api/v1/stocks/${position.ticker}/quote`)
          const data = await response.json()

          const currentPrice = data.data?.current_price || position.currentPrice
          const currentValue = position.shares * currentPrice
          const profit = currentValue - position.totalCost
          const profitPercent = (profit / position.totalCost) * 100

          return {
            ...position,
            currentPrice,
            currentValue,
            profit,
            profitPercent
          }
        } catch (error) {
          console.error(`Failed to update price for ${position.ticker}:`, error)
          return position
        }
      })
    )

    return updatedPositions
  },

  /**
   * Recalculate portfolio totals
   */
  recalculateTotals: (portfolio: PortfolioState): void => {
    const positionsValue = portfolio.positions.reduce(
      (sum, pos) => sum + pos.currentValue,
      0
    )

    portfolio.totalValue = portfolio.cash + positionsValue
    portfolio.totalProfit = portfolio.totalValue - portfolio.initialCash
    portfolio.totalProfitPercent = (portfolio.totalProfit / portfolio.initialCash) * 100
  },

  /**
   * Reset portfolio
   */
  resetPortfolio: (): PortfolioState => {
    return portfolioManager.initializePortfolio()
  },

  /**
   * Get transaction history
   */
  getTransactions: (limit?: number): Transaction[] => {
    const portfolio = portfolioManager.getPortfolio()
    return limit ? portfolio.transactions.slice(0, limit) : portfolio.transactions
  },

  /**
   * Get AI-recommended transaction stats
   */
  getAIStats: (): {
    totalAITrades: number
    aiWins: number
    aiLosses: number
    aiWinRate: number
  } => {
    const portfolio = portfolioManager.getPortfolio()
    const aiTrades = portfolio.transactions.filter(t => t.aiRecommendation)

    let aiWins = 0
    let aiLosses = 0

    // Match buy/sell pairs to determine wins/losses
    const buyTrades = aiTrades.filter(t => t.type === 'BUY')
    const sellTrades = aiTrades.filter(t => t.type === 'SELL')

    for (const sell of sellTrades) {
      const correspondingBuy = buyTrades
        .filter(b => b.ticker === sell.ticker && new Date(b.date) < new Date(sell.date))
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0]

      if (correspondingBuy) {
        if (sell.price > correspondingBuy.price) {
          aiWins++
        } else {
          aiLosses++
        }
      }
    }

    const totalAITrades = aiWins + aiLosses
    const aiWinRate = totalAITrades > 0 ? (aiWins / totalAITrades) * 100 : 0

    return {
      totalAITrades,
      aiWins,
      aiLosses,
      aiWinRate
    }
  }
}
