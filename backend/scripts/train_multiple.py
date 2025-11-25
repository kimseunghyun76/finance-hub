"""Train multiple stock prediction models"""
import sys
sys.path.append('.')

from scripts.train_model import train_model_for_ticker
import argparse

# Popular stocks to train
DEFAULT_TICKERS = [
    # US Stocks
    'AAPL',    # Apple
    'GOOGL',   # Alphabet
    'MSFT',    # Microsoft
    'TSLA',    # Tesla
    'NVDA',    # NVIDIA
    'AMZN',    # Amazon
    'META',    # Meta
    # Korean Stocks
    '005930.KS',  # Samsung Electronics
    '000660.KS',  # SK Hynix
    '035420.KS',  # NAVER
    '035720.KS',  # Kakao
]


def train_multiple_models(tickers: list[str], save_dir: str = "models", model_type: str = "LSTM"):
    """Train models for multiple tickers with specified model type"""
    print(f"\n🚀 Starting {model_type} training for {len(tickers)} stocks")
    print(f"Tickers: {', '.join(tickers)}\n")

    results = {
        'success': [],
        'failed': []
    }

    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        try:
            train_model_for_ticker(ticker, save_dir, model_type)
            results['success'].append(ticker)
        except Exception as e:
            print(f"\n❌ Failed to train {ticker}: {str(e)}")
            results['failed'].append((ticker, str(e)))

    # Summary
    print(f"\n{'='*50}")
    print("📊 TRAINING SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Success: {len(results['success'])} models")
    for ticker in results['success']:
        print(f"  - {ticker}")

    if results['failed']:
        print(f"\n❌ Failed: {len(results['failed'])} models")
        for ticker, error in results['failed']:
            print(f"  - {ticker}: {error}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train multiple stock prediction models")
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="List of ticker symbols (e.g., AAPL GOOGL MSFT)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Train all default popular stocks"
    )
    parser.add_argument(
        "--save-dir",
        default="models",
        help="Directory to save models"
    )
    parser.add_argument(
        "--model-type",
        default="LSTM",
        choices=["LSTM", "GRU"],
        help="Model type to train (default: LSTM)"
    )

    args = parser.parse_args()

    if args.all:
        tickers = DEFAULT_TICKERS
    elif args.tickers:
        tickers = args.tickers
    else:
        print("Error: Please specify --tickers or --all")
        print("\nExamples:")
        print("  python scripts/train_multiple.py --all")
        print("  python scripts/train_multiple.py --tickers AAPL GOOGL MSFT")
        print("  python scripts/train_multiple.py --tickers AAPL --model-type GRU")
        sys.exit(1)

    train_multiple_models(tickers, args.save_dir, args.model_type)
