"""Backtesting engine for trading strategies"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import logging
import numpy as np
from collections import defaultdict

from app.models.backtest import BacktestStrategy, BacktestRun, Trade
from app.models.daily_prediction import DailyPrediction
import yfinance as yf

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtesting engine for various trading strategies"""

    def __init__(self, db: Session):
        self.db = db

    def run_backtest(
        self,
        strategy_id: int,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[BacktestRun]:
        """Execute a backtest for a given strategy and ticker"""

        # Get strategy
        strategy = self.db.query(BacktestStrategy).filter(
            BacktestStrategy.id == strategy_id
        ).first()

        if not strategy:
            logger.error(f"Strategy {strategy_id} not found")
            return None

        try:
            # Get historical data
            historical_data = self._get_historical_data(ticker, start_date, end_date)
            if not historical_data or len(historical_data) < 2:
                logger.error(f"Insufficient historical data for {ticker}")
                return None

            # Execute strategy
            trades, equity_curve = self._execute_strategy(
                strategy, ticker, historical_data, start_date, end_date
            )

            # Calculate performance metrics
            metrics = self._calculate_metrics(
                trades, equity_curve, strategy.initial_capital, historical_data
            )

            # Create backtest run record
            duration_days = (end_date - start_date).days

            backtest_run = BacktestRun(
                strategy_id=strategy_id,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                duration_days=duration_days,
                initial_capital=strategy.initial_capital,
                final_capital=metrics['final_capital'],
                total_return=metrics['total_return'],
                annualized_return=metrics['annualized_return'],
                sharpe_ratio=metrics['sharpe_ratio'],
                max_drawdown=metrics['max_drawdown'],
                win_rate=metrics['win_rate'],
                profit_factor=metrics['profit_factor'],
                total_trades=len(trades),
                winning_trades=metrics['winning_trades'],
                losing_trades=metrics['losing_trades'],
                avg_win=metrics['avg_win'],
                avg_loss=metrics['avg_loss'],
                benchmark_return=metrics['benchmark_return'],
                alpha=metrics['alpha'],
                trades=json.dumps([self._trade_to_dict(t) for t in trades]),
                equity_curve=json.dumps(equity_curve),
                status='completed',
                completed_at=datetime.utcnow()
            )

            self.db.add(backtest_run)
            self.db.commit()
            self.db.refresh(backtest_run)

            logger.info(f"✅ Backtest completed for {ticker}: {metrics['total_return']:.2f}% return")
            return backtest_run

        except Exception as e:
            logger.error(f"❌ Backtest failed for {ticker}: {e}")
            self.db.rollback()

            # Create failed run record
            backtest_run = BacktestRun(
                strategy_id=strategy_id,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                initial_capital=strategy.initial_capital,
                final_capital=strategy.initial_capital,
                status='failed',
                error_message=str(e)
            )
            self.db.add(backtest_run)
            self.db.commit()
            return None

    def _get_historical_data(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Get historical price data from yfinance and prediction data"""
        try:
            # Get historical price data from yfinance
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                logger.warning(f"No historical data found for {ticker}")
                return []

            # Get prediction data for the same period
            predictions = self.db.query(DailyPrediction).filter(
                DailyPrediction.ticker == ticker,
                DailyPrediction.prediction_date >= start_date,
                DailyPrediction.prediction_date <= end_date
            ).order_by(DailyPrediction.prediction_date).all()

            # Create prediction lookup dict
            pred_dict = {}
            for pred in predictions:
                # Handle both datetime and date objects
                if hasattr(pred.prediction_date, 'date'):
                    pred_date = pred.prediction_date.date()
                else:
                    pred_date = pred.prediction_date

                # Map action (BUY/SELL/HOLD) to direction (UP/DOWN/NEUTRAL)
                direction = 'NEUTRAL'
                if pred.action == 'BUY':
                    direction = 'UP'
                elif pred.action == 'SELL':
                    direction = 'DOWN'

                pred_dict[pred_date] = {
                    'predicted_direction': direction,
                    'confidence': pred.confidence
                }

            # Combine price and prediction data
            historical_data = []
            for date_idx, row in hist.iterrows():
                date = date_idx.to_pydatetime()
                date_key = date.date()

                # Get prediction data if available
                pred_data = pred_dict.get(date_key, {
                    'predicted_direction': 'NEUTRAL',
                    'confidence': 0.5
                })

                historical_data.append({
                    'date': date,
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'volume': row['Volume'],
                    'predicted_direction': pred_data['predicted_direction'],
                    'confidence': pred_data['confidence']
                })

            return historical_data

        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []

    def _execute_strategy(
        self,
        strategy: BacktestStrategy,
        ticker: str,
        historical_data: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[List[Dict], List[Dict]]:
        """Execute trading strategy and return trades and equity curve"""

        strategy_type = strategy.strategy_type
        params = json.loads(strategy.parameters) if strategy.parameters else {}

        if strategy_type == "BUY_AND_HOLD":
            return self._buy_and_hold_strategy(strategy, ticker, historical_data)
        elif strategy_type == "MOVING_AVERAGE":
            return self._moving_average_strategy(strategy, ticker, historical_data, params)
        elif strategy_type == "PREDICTION_BASED":
            return self._prediction_based_strategy(strategy, ticker, historical_data, params)
        else:
            logger.warning(f"Unknown strategy type: {strategy_type}, using buy-and-hold")
            return self._buy_and_hold_strategy(strategy, ticker, historical_data)

    def _buy_and_hold_strategy(
        self, strategy: BacktestStrategy, ticker: str, data: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Simple buy-and-hold strategy"""
        trades = []
        equity_curve = []

        if not data:
            return trades, equity_curve

        # Buy at start
        entry_price = data[0]['close']
        shares = strategy.initial_capital / entry_price

        trade = {
            'ticker': ticker,
            'entry_date': data[0]['date'],
            'entry_price': entry_price,
            'shares': shares,
            'direction': 'LONG'
        }

        # Track equity
        for i, day in enumerate(data):
            portfolio_value = shares * day['close']
            equity_curve.append({
                'date': day['date'].isoformat(),
                'value': portfolio_value
            })

        # Sell at end
        exit_price = data[-1]['close']
        trade['exit_date'] = data[-1]['date']
        trade['exit_price'] = exit_price
        trade['profit_loss'] = (exit_price - entry_price) * shares
        trade['profit_loss_pct'] = ((exit_price - entry_price) / entry_price) * 100
        trade['holding_days'] = (trade['exit_date'] - trade['entry_date']).days
        trade['exit_reason'] = 'END_OF_PERIOD'

        trades.append(trade)
        return trades, equity_curve

    def _moving_average_strategy(
        self, strategy: BacktestStrategy, ticker: str, data: List[Dict], params: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        """Moving average crossover strategy"""
        short_window = params.get('short_window', 20)
        long_window = params.get('long_window', 50)

        trades = []
        equity_curve = []
        cash = strategy.initial_capital
        position = None

        # Calculate moving averages
        closes = [d['close'] for d in data]
        short_ma = self._moving_average(closes, short_window)
        long_ma = self._moving_average(closes, long_window)

        for i, day in enumerate(data):
            if i < long_window:
                equity_curve.append({
                    'date': day['date'].isoformat(),
                    'value': cash
                })
                continue

            # Trading signals
            if short_ma[i] > long_ma[i] and (i == 0 or short_ma[i-1] <= long_ma[i-1]):
                # Buy signal
                if position is None and cash > 0:
                    position_size = cash * (strategy.position_size_pct / 100)
                    shares = position_size / day['close']

                    position = {
                        'ticker': ticker,
                        'entry_date': day['date'],
                        'entry_price': day['close'],
                        'shares': shares,
                        'direction': 'LONG'
                    }
                    cash -= position_size

            elif short_ma[i] < long_ma[i] and (i == 0 or short_ma[i-1] >= long_ma[i-1]):
                # Sell signal
                if position is not None:
                    exit_price = day['close']
                    position['exit_date'] = day['date']
                    position['exit_price'] = exit_price
                    position['profit_loss'] = (exit_price - position['entry_price']) * position['shares']
                    position['profit_loss_pct'] = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                    position['holding_days'] = (position['exit_date'] - position['entry_date']).days
                    position['exit_reason'] = 'SIGNAL'

                    trades.append(position)
                    cash += position['shares'] * exit_price
                    position = None

            # Calculate portfolio value
            portfolio_value = cash
            if position:
                portfolio_value += position['shares'] * day['close']

            equity_curve.append({
                'date': day['date'].isoformat(),
                'value': portfolio_value
            })

        # Close any open position at end
        if position:
            exit_price = data[-1]['close']
            position['exit_date'] = data[-1]['date']
            position['exit_price'] = exit_price
            position['profit_loss'] = (exit_price - position['entry_price']) * position['shares']
            position['profit_loss_pct'] = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            position['holding_days'] = (position['exit_date'] - position['entry_date']).days
            position['exit_reason'] = 'END_OF_PERIOD'
            trades.append(position)

        return trades, equity_curve

    def _prediction_based_strategy(
        self, strategy: BacktestStrategy, ticker: str, data: List[Dict], params: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        """Strategy based on ML predictions"""
        confidence_threshold = params.get('confidence_threshold', 0.7)

        trades = []
        equity_curve = []
        cash = strategy.initial_capital
        position = None

        for i, day in enumerate(data):
            predicted_direction = day.get('predicted_direction', 'NEUTRAL')
            confidence = day.get('confidence', 0.5)

            # Buy signal: UP prediction with high confidence
            if predicted_direction == 'UP' and confidence >= confidence_threshold:
                if position is None and cash > 0:
                    position_size = cash * (strategy.position_size_pct / 100)
                    shares = position_size / day['close']

                    position = {
                        'ticker': ticker,
                        'entry_date': day['date'],
                        'entry_price': day['close'],
                        'shares': shares,
                        'direction': 'LONG'
                    }
                    cash -= position_size

            # Sell signal: DOWN prediction or low confidence
            elif (predicted_direction == 'DOWN' or confidence < confidence_threshold * 0.8):
                if position is not None:
                    exit_price = day['close']
                    position['exit_date'] = day['date']
                    position['exit_price'] = exit_price
                    position['profit_loss'] = (exit_price - position['entry_price']) * position['shares']
                    position['profit_loss_pct'] = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                    position['holding_days'] = (position['exit_date'] - position['entry_date']).days
                    position['exit_reason'] = 'SIGNAL'

                    trades.append(position)
                    cash += position['shares'] * exit_price
                    position = None

            # Calculate portfolio value
            portfolio_value = cash
            if position:
                portfolio_value += position['shares'] * day['close']

            equity_curve.append({
                'date': day['date'].isoformat(),
                'value': portfolio_value
            })

        # Close any open position at end
        if position:
            exit_price = data[-1]['close']
            position['exit_date'] = data[-1]['date']
            position['exit_price'] = exit_price
            position['profit_loss'] = (exit_price - position['entry_price']) * position['shares']
            position['profit_loss_pct'] = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            position['holding_days'] = (position['exit_date'] - position['entry_date']).days
            position['exit_reason'] = 'END_OF_PERIOD'
            trades.append(position)

        return trades, equity_curve

    def _moving_average(self, data: List[float], window: int) -> List[float]:
        """Calculate moving average"""
        ma = []
        for i in range(len(data)):
            if i < window - 1:
                ma.append(data[i])
            else:
                ma.append(sum(data[i-window+1:i+1]) / window)
        return ma

    def _calculate_metrics(
        self, trades: List[Dict], equity_curve: List[Dict], initial_capital: float, data: List[Dict]
    ) -> Dict:
        """Calculate performance metrics"""

        if not equity_curve:
            return {
                'final_capital': initial_capital,
                'total_return': 0.0,
                'annualized_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'benchmark_return': 0.0,
                'alpha': 0.0
            }

        final_capital = equity_curve[-1]['value']
        total_return = ((final_capital - initial_capital) / initial_capital) * 100

        # Annualized return
        years = len(equity_curve) / 252  # Trading days per year
        if years > 0:
            annualized_return = (((final_capital / initial_capital) ** (1 / years)) - 1) * 100
        else:
            annualized_return = total_return

        # Sharpe ratio
        returns = []
        for i in range(1, len(equity_curve)):
            daily_return = (equity_curve[i]['value'] - equity_curve[i-1]['value']) / equity_curve[i-1]['value']
            returns.append(daily_return)

        if returns and len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0

        # Maximum drawdown
        peak = equity_curve[0]['value']
        max_drawdown = 0.0
        for point in equity_curve:
            if point['value'] > peak:
                peak = point['value']
            drawdown = ((peak - point['value']) / peak) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Trade statistics
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) <= 0]

        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0.0
        avg_win = np.mean([t['profit_loss'] for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([abs(t['profit_loss']) for t in losing_trades]) if losing_trades else 0.0

        total_wins = sum([t['profit_loss'] for t in winning_trades])
        total_losses = abs(sum([t['profit_loss'] for t in losing_trades]))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0

        # Benchmark (buy-and-hold)
        if data and len(data) >= 2:
            benchmark_return = ((data[-1]['close'] - data[0]['close']) / data[0]['close']) * 100
        else:
            benchmark_return = 0.0

        alpha = total_return - benchmark_return

        return {
            'final_capital': final_capital,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'benchmark_return': benchmark_return,
            'alpha': alpha
        }

    def _trade_to_dict(self, trade: Dict) -> Dict:
        """Convert trade to JSON-serializable dict"""
        return {
            'ticker': trade.get('ticker'),
            'entry_date': trade.get('entry_date').isoformat() if trade.get('entry_date') else None,
            'entry_price': trade.get('entry_price'),
            'exit_date': trade.get('exit_date').isoformat() if trade.get('exit_date') else None,
            'exit_price': trade.get('exit_price'),
            'shares': trade.get('shares'),
            'direction': trade.get('direction'),
            'profit_loss': trade.get('profit_loss'),
            'profit_loss_pct': trade.get('profit_loss_pct'),
            'holding_days': trade.get('holding_days'),
            'exit_reason': trade.get('exit_reason')
        }
