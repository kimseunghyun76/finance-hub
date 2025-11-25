"""Backtesting models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class BacktestStrategy(Base):
    """Backtest strategy configuration"""
    __tablename__ = "backtest_strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # NULL for system strategies
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Strategy type and parameters
    strategy_type = Column(String(50), nullable=False)  # BUY_AND_HOLD, MOVING_AVERAGE, PREDICTION_BASED, etc.
    parameters = Column(Text)  # JSON parameters

    # Risk management
    initial_capital = Column(Float, default=100000.0)
    position_size_pct = Column(Float, default=10.0)  # % of portfolio per position
    stop_loss_pct = Column(Float, nullable=True)  # % stop loss
    take_profit_pct = Column(Float, nullable=True)  # % take profit

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    runs = relationship("BacktestRun", back_populates="strategy", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BacktestStrategy {self.name} ({self.strategy_type})>"


class BacktestRun(Base):
    """Individual backtest run results"""
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("backtest_strategies.id"), nullable=False)
    ticker = Column(String(20), index=True, nullable=False)

    # Time period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_days = Column(Integer)

    # Results
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float)  # %
    annualized_return = Column(Float)  # %

    # Performance metrics
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)  # %
    win_rate = Column(Float)  # %
    profit_factor = Column(Float)

    # Trading statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    avg_win = Column(Float)
    avg_loss = Column(Float)

    # Comparison to buy-and-hold
    benchmark_return = Column(Float)  # Buy-and-hold return
    alpha = Column(Float)  # Excess return over benchmark

    # Detailed results
    trades = Column(Text)  # JSON array of trades
    equity_curve = Column(Text)  # JSON array of daily portfolio values

    # Status
    status = Column(String(20), default="completed")  # running, completed, failed
    error_message = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    strategy = relationship("BacktestStrategy", back_populates="runs")

    def __repr__(self):
        return f"<BacktestRun {self.ticker} ({self.start_date.date()} - {self.end_date.date()}): {self.total_return:.2f}%>"


class Trade(Base):
    """Individual trade record (for detailed analysis)"""
    __tablename__ = "backtest_trades"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False)
    ticker = Column(String(20), index=True, nullable=False)

    # Trade details
    entry_date = Column(DateTime, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_date = Column(DateTime)
    exit_price = Column(Float)

    # Position
    shares = Column(Float, nullable=False)
    direction = Column(String(10), default="LONG")  # LONG or SHORT

    # Results
    profit_loss = Column(Float)
    profit_loss_pct = Column(Float)
    holding_days = Column(Integer)

    # Reason for exit
    exit_reason = Column(String(50))  # STOP_LOSS, TAKE_PROFIT, SIGNAL, END_OF_PERIOD

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Trade {self.ticker} @ {self.entry_price} -> {self.exit_price}: {self.profit_loss_pct:.2f}%>"
