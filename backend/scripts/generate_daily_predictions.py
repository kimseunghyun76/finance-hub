"""Generate daily predictions for all stocks using trained models"""
import sys
import os
from datetime import datetime, timedelta
import numpy as np

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.sector import StockInfo
from app.models.prediction import Prediction, ActionType, ModelType
from app.models.daily_prediction import DailyPrediction
from app.models.stock_price import StockPrice
from app.ml.predictor import StockPredictor
from app.services.data_fetcher import StockDataFetcher
import pandas as pd

def generate_predictions():
    """Generate predictions for all stocks"""
    db = SessionLocal()
    
    try:
        print("🚀 Starting daily prediction generation...")
        
        # Get all tickers
        stocks = db.query(StockInfo).all()
        total_stocks = len(stocks)
        print(f"📋 Found {total_stocks} stocks in database")
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for i, stock in enumerate(stocks, 1):
            ticker = stock.ticker
            model_path = os.path.join("models", f"{ticker}_model.h5")
            
            if not os.path.exists(model_path):
                # print(f"  ⚠️ No model found for {ticker}, skipping...")
                skip_count += 1
                continue
                
            print(f"[{i}/{total_stocks}] Predicting {ticker}...", end=" ", flush=True)
            
            try:
                # Initialize predictor
                predictor = StockPredictor(model_path=model_path)
                
                # Fetch recent data (need at least 60 days)
                # Try fetching from DB first for speed, fallback to API
                # For now, let's just use DataFetcher to get latest
                df = StockDataFetcher.fetch_yahoo_finance(ticker, period="6mo")
                
                if df is None or df.empty or len(df) < 60:
                    print("❌ Insufficient data")
                    fail_count += 1
                    continue
                
                # Make prediction
                result = predictor.predict(df)
                
                # Determine action
                change_percent = result['change_percent']
                if change_percent >= 2.0:
                    action = ActionType.BUY
                elif change_percent <= -2.0:
                    action = ActionType.SELL
                else:
                    action = ActionType.HOLD
                
                # Create prediction record
                prediction = Prediction(
                    ticker=ticker,
                    prediction_date=datetime.now().date(),
                    target_date=datetime.now().date() + timedelta(days=result['forecast_days']),
                    predicted_price=result['predicted_price'],
                    confidence=result['confidence'],
                    action=action,
                    model_version="v1.0",
                    model_type=ModelType.LSTM,
                    features={"recent_close": float(result['current_price'])}
                )
                
                # Save to DB
                db.add(prediction)
                
                # Also save to DailyPrediction
                daily_prediction = DailyPrediction(
                    ticker=ticker,
                    prediction_date=datetime.now().date(),
                    target_date=datetime.now().date() + timedelta(days=result['forecast_days']),
                    predicted_price=result['predicted_price'],
                    current_price=result['current_price'],
                    predicted_change=result['change'],
                    predicted_change_percent=result['change_percent'],
                    confidence=result['confidence'],
                    action=action.value,
                    model_type=ModelType.LSTM.value
                )
                db.add(daily_prediction)
                
                db.commit()
                
                print(f"✅ {action.value} ({change_percent:+.2f}%)")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                fail_count += 1
                db.rollback()
        
        print(f"\n✨ Prediction generation completed!")
        print(f"✅ Generated: {success_count}")
        print(f"⚠️ Skipped: {skip_count}")
        print(f"❌ Failed: {fail_count}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_predictions()
