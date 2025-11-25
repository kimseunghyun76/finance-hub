"""Backtesting API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

from app.database import get_db
from app.models.backtest import BacktestStrategy, BacktestRun
from app.services.backtest_engine import BacktestEngine

router = APIRouter()


# Request models
class CreateStrategyRequest(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str  # BUY_AND_HOLD, MOVING_AVERAGE, PREDICTION_BASED
    parameters: Optional[dict] = None
    initial_capital: float = 100000.0
    position_size_pct: float = 10.0
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None


class RunBacktestRequest(BaseModel):
    strategy_id: int
    ticker: str
    start_date: datetime
    end_date: datetime


# Response models
class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy_type: str
    parameters: Optional[dict]
    initial_capital: float
    position_size_pct: float
    stop_loss_pct: Optional[float]
    take_profit_pct: Optional[float]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, strategy: BacktestStrategy):
        data = {
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'strategy_type': strategy.strategy_type,
            'parameters': json.loads(strategy.parameters) if strategy.parameters else None,
            'initial_capital': strategy.initial_capital,
            'position_size_pct': strategy.position_size_pct,
            'stop_loss_pct': strategy.stop_loss_pct,
            'take_profit_pct': strategy.take_profit_pct,
            'is_active': strategy.is_active,
            'created_at': strategy.created_at
        }
        return cls(**data)


class BacktestResultResponse(BaseModel):
    id: int
    strategy_id: int
    ticker: str
    start_date: datetime
    end_date: datetime
    duration_days: Optional[int]
    initial_capital: float
    final_capital: float
    total_return: Optional[float]
    annualized_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    win_rate: Optional[float]
    profit_factor: Optional[float]
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: Optional[float]
    avg_loss: Optional[float]
    benchmark_return: Optional[float]
    alpha: Optional[float]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class BacktestDetailResponse(BaseModel):
    id: int
    strategy_id: int
    ticker: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: Optional[float]
    annualized_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    win_rate: Optional[float]
    profit_factor: Optional[float]
    total_trades: int
    winning_trades: int
    losing_trades: int
    benchmark_return: Optional[float]
    alpha: Optional[float]
    trades: List[dict]
    equity_curve: List[dict]
    status: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, run: BacktestRun):
        data = {
            'id': run.id,
            'strategy_id': run.strategy_id,
            'ticker': run.ticker,
            'start_date': run.start_date,
            'end_date': run.end_date,
            'initial_capital': run.initial_capital,
            'final_capital': run.final_capital,
            'total_return': run.total_return,
            'annualized_return': run.annualized_return,
            'sharpe_ratio': run.sharpe_ratio,
            'max_drawdown': run.max_drawdown,
            'win_rate': run.win_rate,
            'profit_factor': run.profit_factor,
            'total_trades': run.total_trades,
            'winning_trades': run.winning_trades,
            'losing_trades': run.losing_trades,
            'benchmark_return': run.benchmark_return,
            'alpha': run.alpha,
            'trades': json.loads(run.trades) if run.trades else [],
            'equity_curve': json.loads(run.equity_curve) if run.equity_curve else [],
            'status': run.status
        }
        return cls(**data)


# Strategy endpoints
@router.post("/backtest/strategies", response_model=StrategyResponse)
def create_strategy(
    request: CreateStrategyRequest,
    db: Session = Depends(get_db)
):
    """Create a new backtesting strategy"""

    strategy = BacktestStrategy(
        name=request.name,
        description=request.description,
        strategy_type=request.strategy_type,
        parameters=json.dumps(request.parameters) if request.parameters else None,
        initial_capital=request.initial_capital,
        position_size_pct=request.position_size_pct,
        stop_loss_pct=request.stop_loss_pct,
        take_profit_pct=request.take_profit_pct
    )

    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    return StrategyResponse.from_orm(strategy)


@router.get("/backtest/strategies", response_model=List[StrategyResponse])
def list_strategies(
    active_only: bool = Query(True, description="Show only active strategies"),
    db: Session = Depends(get_db)
):
    """List all backtesting strategies"""

    query = db.query(BacktestStrategy)

    if active_only:
        query = query.filter(BacktestStrategy.is_active == True)

    strategies = query.order_by(BacktestStrategy.created_at.desc()).all()

    return [StrategyResponse.from_orm(s) for s in strategies]


@router.get("/backtest/strategies/{strategy_id}", response_model=StrategyResponse)
def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific strategy"""

    strategy = db.query(BacktestStrategy).filter(
        BacktestStrategy.id == strategy_id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    return StrategyResponse.from_orm(strategy)


@router.put("/backtest/strategies/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: int,
    request: CreateStrategyRequest,
    db: Session = Depends(get_db)
):
    """Update a strategy"""

    strategy = db.query(BacktestStrategy).filter(
        BacktestStrategy.id == strategy_id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.name = request.name
    strategy.description = request.description
    strategy.strategy_type = request.strategy_type
    strategy.parameters = json.dumps(request.parameters) if request.parameters else None
    strategy.initial_capital = request.initial_capital
    strategy.position_size_pct = request.position_size_pct
    strategy.stop_loss_pct = request.stop_loss_pct
    strategy.take_profit_pct = request.take_profit_pct

    db.commit()
    db.refresh(strategy)

    return StrategyResponse.from_orm(strategy)


@router.delete("/backtest/strategies/{strategy_id}")
def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Delete (deactivate) a strategy"""

    strategy = db.query(BacktestStrategy).filter(
        BacktestStrategy.id == strategy_id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.is_active = False
    db.commit()

    return {"success": True, "message": f"Strategy {strategy_id} deactivated"}


# Backtest execution endpoints
@router.post("/backtest/run", response_model=BacktestResultResponse)
def run_backtest(
    request: RunBacktestRequest,
    db: Session = Depends(get_db)
):
    """Execute a backtest"""

    # Validate strategy exists
    strategy = db.query(BacktestStrategy).filter(
        BacktestStrategy.id == request.strategy_id
    ).first()

    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # Validate date range
    if request.start_date >= request.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    if request.end_date > datetime.utcnow():
        raise HTTPException(status_code=400, detail="End date cannot be in the future")

    # Run backtest
    engine = BacktestEngine(db)
    result = engine.run_backtest(
        strategy_id=request.strategy_id,
        ticker=request.ticker,
        start_date=request.start_date,
        end_date=request.end_date
    )

    if not result:
        raise HTTPException(
            status_code=500,
            detail="Backtest execution failed. Check if historical data is available for this ticker."
        )

    return BacktestResultResponse.from_attributes(result)


@router.get("/backtest/results", response_model=List[BacktestResultResponse])
def list_backtest_results(
    strategy_id: Optional[int] = Query(None, description="Filter by strategy"),
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db)
):
    """List backtest results"""

    query = db.query(BacktestRun)

    if strategy_id:
        query = query.filter(BacktestRun.strategy_id == strategy_id)

    if ticker:
        query = query.filter(BacktestRun.ticker == ticker)

    results = query.order_by(BacktestRun.created_at.desc()).limit(limit).all()

    return [BacktestResultResponse.from_attributes(r) for r in results]


@router.get("/backtest/results/{run_id}", response_model=BacktestDetailResponse)
def get_backtest_result(
    run_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed backtest result with trades and equity curve"""

    result = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Backtest result not found")

    return BacktestDetailResponse.from_orm(result)


@router.get("/backtest/compare")
def compare_strategies(
    ticker: str,
    strategy_ids: str = Query(..., description="Comma-separated strategy IDs"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """Compare multiple strategies on the same ticker and time period"""

    # Parse strategy IDs
    try:
        ids = [int(id.strip()) for id in strategy_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid strategy IDs format")

    # Run backtests for all strategies
    engine = BacktestEngine(db)
    results = []

    for strategy_id in ids:
        # Check if result already exists
        existing = db.query(BacktestRun).filter(
            BacktestRun.strategy_id == strategy_id,
            BacktestRun.ticker == ticker,
            BacktestRun.start_date == start_date,
            BacktestRun.end_date == end_date,
            BacktestRun.status == 'completed'
        ).first()

        if existing:
            results.append(BacktestResultResponse.from_attributes(existing))
        else:
            # Run new backtest
            result = engine.run_backtest(
                strategy_id=strategy_id,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
            if result:
                results.append(BacktestResultResponse.from_attributes(result))

    if not results:
        raise HTTPException(
            status_code=500,
            detail="Failed to run backtests. Check if historical data is available."
        )

    return {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "strategies": len(results),
        "results": results
    }


@router.get("/backtest/strategy/{strategy_id}/performance")
def get_strategy_performance(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get aggregated performance metrics for a strategy across all runs"""

    runs = db.query(BacktestRun).filter(
        BacktestRun.strategy_id == strategy_id,
        BacktestRun.status == 'completed'
    ).all()

    if not runs:
        raise HTTPException(
            status_code=404,
            detail=f"No completed backtest runs found for strategy {strategy_id}"
        )

    # Aggregate metrics
    total_runs = len(runs)
    avg_return = sum([r.total_return for r in runs if r.total_return]) / total_runs
    avg_sharpe = sum([r.sharpe_ratio for r in runs if r.sharpe_ratio]) / total_runs
    avg_max_drawdown = sum([r.max_drawdown for r in runs if r.max_drawdown]) / total_runs
    avg_win_rate = sum([r.win_rate for r in runs if r.win_rate]) / total_runs

    profitable_runs = len([r for r in runs if r.total_return and r.total_return > 0])
    win_ratio = (profitable_runs / total_runs) * 100

    return {
        "strategy_id": strategy_id,
        "total_runs": total_runs,
        "profitable_runs": profitable_runs,
        "win_ratio": win_ratio,
        "avg_total_return": avg_return,
        "avg_sharpe_ratio": avg_sharpe,
        "avg_max_drawdown": avg_max_drawdown,
        "avg_win_rate": avg_win_rate,
        "recent_runs": [BacktestResultResponse.from_attributes(r) for r in runs[:5]]
    }
