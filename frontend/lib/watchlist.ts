/**
 * Watchlist management utilities using local storage
 */

export interface WatchlistItem {
  ticker: string
  addedAt: string
  name?: string
}

const WATCHLIST_KEY = 'finance-hub-watchlist'

export const watchlistManager = {
  /**
   * Get all watchlist items
   */
  getAll: (): WatchlistItem[] => {
    if (typeof window === 'undefined') return []

    try {
      const data = localStorage.getItem(WATCHLIST_KEY)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to load watchlist:', error)
      return []
    }
  },

  /**
   * Add a ticker to watchlist
   */
  add: (ticker: string, name?: string): boolean => {
    if (typeof window === 'undefined') return false

    try {
      const watchlist = watchlistManager.getAll()

      // Check if already exists
      if (watchlist.some(item => item.ticker === ticker)) {
        return false
      }

      const newItem: WatchlistItem = {
        ticker,
        addedAt: new Date().toISOString(),
        name
      }

      watchlist.push(newItem)
      localStorage.setItem(WATCHLIST_KEY, JSON.stringify(watchlist))

      // Dispatch custom event for other components to listen
      window.dispatchEvent(new CustomEvent('watchlist-updated'))

      return true
    } catch (error) {
      console.error('Failed to add to watchlist:', error)
      return false
    }
  },

  /**
   * Remove a ticker from watchlist
   */
  remove: (ticker: string): boolean => {
    if (typeof window === 'undefined') return false

    try {
      const watchlist = watchlistManager.getAll()
      const filtered = watchlist.filter(item => item.ticker !== ticker)

      if (filtered.length === watchlist.length) {
        return false // Not found
      }

      localStorage.setItem(WATCHLIST_KEY, JSON.stringify(filtered))

      // Dispatch custom event
      window.dispatchEvent(new CustomEvent('watchlist-updated'))

      return true
    } catch (error) {
      console.error('Failed to remove from watchlist:', error)
      return false
    }
  },

  /**
   * Check if ticker is in watchlist
   */
  has: (ticker: string): boolean => {
    if (typeof window === 'undefined') return false

    const watchlist = watchlistManager.getAll()
    return watchlist.some(item => item.ticker === ticker)
  },

  /**
   * Clear entire watchlist
   */
  clear: (): void => {
    if (typeof window === 'undefined') return

    try {
      localStorage.removeItem(WATCHLIST_KEY)
      window.dispatchEvent(new CustomEvent('watchlist-updated'))
    } catch (error) {
      console.error('Failed to clear watchlist:', error)
    }
  },

  /**
   * Get count of watchlist items
   */
  count: (): number => {
    return watchlistManager.getAll().length
  }
}
