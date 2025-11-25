"""Train stock prediction model with multiple model types"""
import sys
sys.path.append('.')

from app.services.data_fetcher import StockDataFetcher
from app.ml.predictor import StockPredictor
from app.ml.gru_predictor import GRUPredictor
import os

def train_model_for_ticker(ticker: str, save_dir: str = "models", model_type: str = "LSTM"):
    """Train model for a specific ticker with specified model type

    Args:
        ticker: Stock ticker symbol
        save_dir: Directory to save models
        model_type: Model type (LSTM or GRU)
    """
    print(f"\n{'='*50}")
    print(f"Training {model_type} model for {ticker}")
    print(f"{'='*50}\n")

    # Fetch historical data (5 years)
    print("Fetching historical data...")
    df = StockDataFetcher.fetch_yahoo_finance(ticker, period="5y")

    if df is None or df.empty:
        print(f"❌ No data found for {ticker}")
        return

    print(f"✅ Fetched {len(df)} days of data")

    # Initialize predictor based on model type
    if model_type.upper() == "GRU":
        predictor = GRUPredictor(
            lookback_days=60,
            forecast_days=5
        )
    else:  # Default to LSTM
        predictor = StockPredictor(
            lookback_days=60,
            forecast_days=5
        )

    # Train model
    print(f"\n🤖 Training {model_type} model...")
    history = predictor.train(df, epochs=50, batch_size=32)

    print("\n📊 Training Results:")
    print(f"  Train Loss: {history['train_loss']:.4f}")
    print(f"  Val Loss: {history['val_loss']:.4f}")
    print(f"  Test Loss: {history['test_loss']:.4f}")
    print(f"  Test MAE: {history['test_mae']:.4f}")

    # Save model (without model type in filename for compatibility)
    os.makedirs(save_dir, exist_ok=True)
    model_filename = f"{ticker.replace('.', '_')}_model.h5"
    model_path = os.path.join(save_dir, model_filename)
    predictor.save_model(model_path)

    print(f"\n✅ {model_type} Model saved to {model_path}")

    # Test prediction
    print("\n🔮 Testing prediction...")
    prediction = predictor.predict(df.tail(60))

    print(f"  Current Price: ${prediction['current_price']:.2f}")
    print(f"  Predicted Price (5 days): ${prediction['predicted_price']:.2f}")
    print(f"  Change: ${prediction['change']:.2f} ({prediction['change_percent']:.2f}%)")
    print(f"  Confidence: {prediction['confidence']:.2%}")

    return predictor


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train stock prediction model")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL, 005930.KS)")
    parser.add_argument("--save-dir", default="models", help="Directory to save model")
    parser.add_argument("--model-type", default="LSTM", choices=["LSTM", "GRU"],
                        help="Model type to train (default: LSTM)")

    args = parser.parse_args()

    train_model_for_ticker(args.ticker, args.save_dir, args.model_type)
