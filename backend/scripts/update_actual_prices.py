#!/usr/bin/env python3
"""
Automatically update actual prices for daily predictions

This script:
1. Finds all predictions where target_date has passed but actual_price is null
2. Fetches the actual closing price for that date
3. Updates the prediction with actual values and calculates accuracy metrics
"""
import sys
import os
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.daily_prediction import DailyPrediction
from app.services.data_fetcher import StockDataFetcher


def update_actual_prices(days_back: int = 7):
    """
    Update actual prices for predictions whose target date has passed

    Args:
        days_back: How many days back to check for predictions (default: 7)
    """
    db = SessionLocal()
    fetcher = StockDataFetcher()

    try:
        # Get current date
        today = date.today()
        cutoff_date = today - timedelta(days=days_back)

        print(f"🔍 Checking predictions from {cutoff_date} to {today}")

        # Find predictions where:
        # 1. target_date has passed (target_date < today)
        # 2. actual_price is null (not yet updated)
        # 3. target_date is within the last 'days_back' days
        predictions = db.query(DailyPrediction).filter(
            DailyPrediction.target_date < today,
            DailyPrediction.target_date >= cutoff_date,
            DailyPrediction.actual_price.is_(None)
        ).all()

        if not predictions:
            print("✅ No predictions to update")
            return

        print(f"📊 Found {len(predictions)} predictions to update\n")

        updated_count = 0
        skipped_count = 0

        for pred in predictions:
            try:
                print(f"📈 {pred.ticker} - Target: {pred.target_date}")

                # Fetch actual price for target date
                # Get historical data for a range around target date
                start_date = pred.target_date - timedelta(days=5)
                end_date = pred.target_date + timedelta(days=5)

                hist_data = fetcher.get_historical_data(
                    pred.ticker,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )

                if hist_data is None or hist_data.empty:
                    print(f"  ⚠️  No data available for {pred.ticker}")
                    skipped_count += 1
                    continue

                # Find the actual closing price on target date
                # Convert target_date to datetime for comparison
                target_datetime = datetime.combine(pred.target_date, datetime.min.time())

                # Try to find exact date first
                matching_rows = hist_data[hist_data.index.date == pred.target_date]

                if matching_rows.empty:
                    # If exact date not found, try to find closest date after target
                    future_rows = hist_data[hist_data.index.date > pred.target_date]
                    if not future_rows.empty:
                        actual_price = float(future_rows.iloc[0]['Close'])
                        actual_date = future_rows.index[0].date()
                        print(f"  ℹ️  Using closest date: {actual_date}")
                    else:
                        print(f"  ⚠️  No price data after target date")
                        skipped_count += 1
                        continue
                else:
                    actual_price = float(matching_rows.iloc[0]['Close'])
                    actual_date = pred.target_date

                # Calculate actual change from current_price (prediction date price)
                actual_change = actual_price - pred.current_price
                actual_change_percent = (actual_change / pred.current_price) * 100

                # Update prediction with actuals
                pred.actual_price = actual_price
                pred.actual_change = actual_change
                pred.actual_change_percent = actual_change_percent

                # Calculate accuracy metrics
                pred.price_error = abs(pred.predicted_price - actual_price)
                pred.price_error_percent = abs(
                    (pred.predicted_price - actual_price) / actual_price * 100
                )

                # Check if direction was correct
                predicted_direction = "up" if pred.predicted_change > 0 else "down" if pred.predicted_change < 0 else "neutral"
                actual_direction = "up" if actual_change > 0 else "down" if actual_change < 0 else "neutral"
                pred.direction_correct = (predicted_direction == actual_direction)

                # Commit changes
                db.commit()

                print(f"  ✅ Updated: Predicted ${pred.predicted_price:.2f}, Actual ${actual_price:.2f}")
                print(f"     Error: ${pred.price_error:.2f} ({pred.price_error_percent:.2f}%)")
                print(f"     Direction: {'✓' if pred.direction_correct else '✗'}\n")

                updated_count += 1

            except Exception as e:
                print(f"  ❌ Error updating {pred.ticker}: {str(e)}\n")
                skipped_count += 1
                continue

        print(f"\n📊 Summary:")
        print(f"  ✅ Updated: {updated_count}")
        print(f"  ⚠️  Skipped: {skipped_count}")
        print(f"  📈 Total: {len(predictions)}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Update actual prices for daily predictions')
    parser.add_argument(
        '--days-back',
        type=int,
        default=7,
        help='How many days back to check for predictions (default: 7)'
    )

    args = parser.parse_args()

    print("🚀 Starting actual price update...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    update_actual_prices(days_back=args.days_back)

    print("\n✨ Done!")
