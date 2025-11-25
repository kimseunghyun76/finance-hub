/**
 * Stock name mapping utility
 * Centralized stock names for consistent display across the application
 */

export interface StockInfo {
  name: string
  market: string
}

export const STOCK_NAMES: Record<string, StockInfo> = {
  // US Stocks - Tech Giants
  'AAPL': { name: 'Apple Inc.', market: 'NASDAQ' },
  'GOOGL': { name: 'Alphabet (Google)', market: 'NASDAQ' },
  'MSFT': { name: 'Microsoft Corp.', market: 'NASDAQ' },
  'AMZN': { name: 'Amazon.com Inc.', market: 'NASDAQ' },
  'META': { name: 'Meta (Facebook)', market: 'NASDAQ' },
  'TSLA': { name: 'Tesla Inc.', market: 'NASDAQ' },
  'NVDA': { name: 'NVIDIA Corp.', market: 'NASDAQ' },

  // US Stocks - Other Tech
  'NFLX': { name: 'Netflix Inc.', market: 'NASDAQ' },
  'AVGO': { name: 'Broadcom Inc.', market: 'NASDAQ' },
  'ORCL': { name: 'Oracle Corp.', market: 'NYSE' },
  'AMD': { name: 'AMD', market: 'NASDAQ' },
  'INTC': { name: 'Intel Corp.', market: 'NASDAQ' },
  'QCOM': { name: 'Qualcomm Inc.', market: 'NASDAQ' },
  'CSCO': { name: 'Cisco Systems', market: 'NASDAQ' },
  'CRM': { name: 'Salesforce Inc.', market: 'NYSE' },
  'ADBE': { name: 'Adobe Inc.', market: 'NASDAQ' },
  'IBM': { name: 'IBM Corp.', market: 'NYSE' },

  // Korean Stocks - Popular
  '005930.KS': { name: '삼성전자', market: 'KRX' },
  '000660.KS': { name: 'SK하이닉스', market: 'KRX' },
  '035420.KS': { name: 'NAVER', market: 'KRX' },
  '035720.KS': { name: '카카오', market: 'KRX' },

  // Korean Stocks - Recommended
  '051910.KS': { name: 'LG화학', market: 'KRX' },
  '006400.KS': { name: '삼성SDI', market: 'KRX' },
  '207940.KS': { name: '삼성바이오로직스', market: 'KRX' },
  '068270.KS': { name: '셀트리온', market: 'KRX' },
  '105560.KS': { name: 'KB금융', market: 'KRX' },
  '055550.KS': { name: '신한지주', market: 'KRX' },

  // Korean Stocks - Additional
  '005380.KS': { name: '현대차', market: 'KRX' },
  '000270.KS': { name: '기아', market: 'KRX' },
  '086790.KS': { name: '하나금융지주', market: 'KRX' },
  '005490.KS': { name: 'POSCO홀딩스', market: 'KRX' },
  '326030.KS': { name: 'SK바이오팜', market: 'KRX' },
  '352820.KS': { name: '하이브', market: 'KRX' },
  '373220.KS': { name: 'LG에너지솔루션', market: 'KRX' },
}

/**
 * Get stock name from ticker
 * Returns the stock name if found, otherwise returns the ticker itself
 */
export function getStockName(ticker: string): string {
  return STOCK_NAMES[ticker]?.name || ticker
}

/**
 * Get full stock info from ticker
 * Returns stock info if found, otherwise returns default info
 */
export function getStockInfo(ticker: string): StockInfo {
  return STOCK_NAMES[ticker] || {
    name: ticker,
    market: ticker.includes('.KS') || ticker.includes('.KQ') ? 'KRX' : 'NASDAQ'
  }
}

/**
 * Format ticker display with name
 * Returns "Name (TICKER)" format
 */
export function formatTickerWithName(ticker: string): string {
  const name = getStockName(ticker)
  if (name === ticker) {
    return ticker
  }
  return `${name} (${ticker})`
}

/**
 * Check if ticker is Korean stock
 */
export function isKoreanStock(ticker: string): boolean {
  return ticker.includes('.KS') || ticker.includes('.KQ')
}
