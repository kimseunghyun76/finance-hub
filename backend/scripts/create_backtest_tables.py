"""Create backtesting tables"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models.backtest import BacktestStrategy, BacktestRun, Trade

if __name__ == "__main__":
    print("Creating backtesting tables...")

    # Create tables
    Base.metadata.create_all(bind=engine, tables=[
        BacktestStrategy.__table__,
        BacktestRun.__table__,
        Trade.__table__
    ])

    print("✅ Backtesting tables created successfully!")
