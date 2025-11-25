"""Test backtesting functionality"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.backtest import BacktestStrategy
from app.services.backtest_engine import BacktestEngine
import json


def test_backtesting():
    """Test backtesting system"""
    db = SessionLocal()

    try:
        print("🧪 Testing Backtesting System\n")

        # 1. Create test strategies
        print("1️⃣ Creating test strategies...")

        # Buy and Hold strategy
        buy_hold_strategy = BacktestStrategy(
            name="Buy and Hold",
            description="Simple buy and hold strategy for baseline comparison",
            strategy_type="BUY_AND_HOLD",
            initial_capital=100000.0,
            position_size_pct=100.0
        )

        # Moving Average strategy
        ma_params = {
            "short_window": 20,
            "long_window": 50
        }
        ma_strategy = BacktestStrategy(
            name="MA Crossover (20/50)",
            description="Moving average crossover strategy",
            strategy_type="MOVING_AVERAGE",
            parameters=json.dumps(ma_params),
            initial_capital=100000.0,
            position_size_pct=95.0
        )

        # Prediction-based strategy
        pred_params = {
            "confidence_threshold": 0.7
        }
        pred_strategy = BacktestStrategy(
            name="AI Prediction Strategy",
            description="Strategy based on ML predictions with confidence threshold",
            strategy_type="PREDICTION_BASED",
            parameters=json.dumps(pred_params),
            initial_capital=100000.0,
            position_size_pct=80.0
        )

        db.add(buy_hold_strategy)
        db.add(ma_strategy)
        db.add(pred_strategy)
        db.commit()

        print(f"✅ Created 3 strategies:")
        print(f"   - {buy_hold_strategy.name} (ID: {buy_hold_strategy.id})")
        print(f"   - {ma_strategy.name} (ID: {ma_strategy.id})")
        print(f"   - {pred_strategy.name} (ID: {pred_strategy.id})\n")

        # 2. Run backtests
        print("2️⃣ Running backtests for AAPL...")

        engine = BacktestEngine(db)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)  # 6 months

        print(f"   Period: {start_date.date()} to {end_date.date()}\n")

        # Test Buy and Hold
        print(f"   Testing {buy_hold_strategy.name}...")
        buy_hold_result = engine.run_backtest(
            strategy_id=buy_hold_strategy.id,
            ticker="AAPL",
            start_date=start_date,
            end_date=end_date
        )

        if buy_hold_result:
            print(f"   ✅ Return: {buy_hold_result.total_return:.2f}%")
            print(f"      Sharpe: {buy_hold_result.sharpe_ratio:.2f}")
            print(f"      Max Drawdown: {buy_hold_result.max_drawdown:.2f}%")
            print(f"      Trades: {buy_hold_result.total_trades}\n")

        # Test Moving Average
        print(f"   Testing {ma_strategy.name}...")
        ma_result = engine.run_backtest(
            strategy_id=ma_strategy.id,
            ticker="AAPL",
            start_date=start_date,
            end_date=end_date
        )

        if ma_result:
            print(f"   ✅ Return: {ma_result.total_return:.2f}%")
            print(f"      Sharpe: {ma_result.sharpe_ratio:.2f}")
            print(f"      Max Drawdown: {ma_result.max_drawdown:.2f}%")
            print(f"      Trades: {ma_result.total_trades}")
            print(f"      Win Rate: {ma_result.win_rate:.2f}%")
            print(f"      Alpha vs Benchmark: {ma_result.alpha:.2f}%\n")

        # Test Prediction-based
        print(f"   Testing {pred_strategy.name}...")
        pred_result = engine.run_backtest(
            strategy_id=pred_strategy.id,
            ticker="AAPL",
            start_date=start_date,
            end_date=end_date
        )

        if pred_result:
            print(f"   ✅ Return: {pred_result.total_return:.2f}%")
            print(f"      Sharpe: {pred_result.sharpe_ratio:.2f}")
            print(f"      Max Drawdown: {pred_result.max_drawdown:.2f}%")
            print(f"      Trades: {pred_result.total_trades}")
            print(f"      Win Rate: {pred_result.win_rate:.2f}%")
            print(f"      Alpha vs Benchmark: {pred_result.alpha:.2f}%\n")

        # 3. Compare results
        print("3️⃣ Strategy Comparison:")
        print("=" * 80)
        print(f"{'Strategy':<30} {'Return':<12} {'Sharpe':<10} {'Drawdown':<12} {'Trades':<8}")
        print("-" * 80)

        if buy_hold_result:
            print(f"{buy_hold_strategy.name:<30} "
                  f"{buy_hold_result.total_return:>10.2f}%  "
                  f"{buy_hold_result.sharpe_ratio:>8.2f}  "
                  f"{buy_hold_result.max_drawdown:>10.2f}%  "
                  f"{buy_hold_result.total_trades:>6}")

        if ma_result:
            print(f"{ma_strategy.name:<30} "
                  f"{ma_result.total_return:>10.2f}%  "
                  f"{ma_result.sharpe_ratio:>8.2f}  "
                  f"{ma_result.max_drawdown:>10.2f}%  "
                  f"{ma_result.total_trades:>6}")

        if pred_result:
            print(f"{pred_strategy.name:<30} "
                  f"{pred_result.total_return:>10.2f}%  "
                  f"{pred_result.sharpe_ratio:>8.2f}  "
                  f"{pred_result.max_drawdown:>10.2f}%  "
                  f"{pred_result.total_trades:>6}")

        print("=" * 80)
        print("\n✅ Backtesting system test completed successfully!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_backtesting()
