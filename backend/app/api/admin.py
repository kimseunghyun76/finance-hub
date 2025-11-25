"""Admin API endpoints"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.scheduler import run_manual_collection
from app.services.data_fetcher import StockDataFetcher
from app.ml.predictor import StockPredictor
from app.services.cache import (
    stock_info_cache,
    stock_quote_cache,
    analyst_targets_cache,
    yfinance_circuit_breaker,
)
from app.models.prediction_cache import PredictionCache
from app.database import get_db
from datetime import datetime
import os
from typing import Optional

router = APIRouter()


@router.post("/collect-prices")
def trigger_price_collection(background_tasks: BackgroundTasks):
    """Manually trigger stock price collection"""
    background_tasks.add_task(run_manual_collection)
    return {
        "status": "started",
        "message": "Price collection started in background"
    }


@router.get("/scheduler/status")
def get_scheduler_status():
    """Get scheduler status"""
    from app.services.scheduler import scheduler

    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in scheduler.get_jobs()
        ],
    }


def train_model_task(ticker: str, save_dir: str = "models"):
    """Background task to train a model"""
    try:
        print(f"Starting training for {ticker}...")

        # Fetch historical data
        df = StockDataFetcher.fetch_yahoo_finance(ticker, period="5y")

        if df is None or df.empty:
            raise ValueError(f"No data found for {ticker}")

        # Initialize and train predictor
        predictor = StockPredictor(lookback_days=60, forecast_days=5)
        history = predictor.train(df, epochs=50, batch_size=32)

        # Save model
        os.makedirs(save_dir, exist_ok=True)
        model_path = os.path.join(save_dir, f"{ticker.replace('.', '_')}_model.h5")
        predictor.save_model(model_path)

        print(f"✅ Model trained and saved: {ticker}")
        return {
            "status": "success",
            "ticker": ticker,
            "model_path": model_path,
            "metrics": history
        }
    except Exception as e:
        print(f"❌ Training failed for {ticker}: {str(e)}")
        return {
            "status": "error",
            "ticker": ticker,
            "error": str(e)
        }


@router.post("/train-model/{ticker}")
def trigger_model_training(ticker: str, background_tasks: BackgroundTasks):
    """
    Trigger model training for a specific ticker

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, 005930.KS)

    Returns:
        Training status
    """
    # Check if ticker data is available
    try:
        df = StockDataFetcher.fetch_yahoo_finance(ticker, period="1mo")
        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for ticker {ticker}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch data for {ticker}: {str(e)}"
        )

    # Start training in background
    background_tasks.add_task(train_model_task, ticker)

    return {
        "status": "started",
        "message": f"Training started for {ticker}",
        "ticker": ticker,
        "estimated_time": "2-3 minutes"
    }


@router.get("/training-status")
def get_training_status():
    """Get status of all trained models"""
    model_dir = "models"

    if not os.path.exists(model_dir):
        return {"trained_models": [], "count": 0}

    trained_models = []
    for file in os.listdir(model_dir):
        if file.endswith("_model.h5"):
            ticker = file.replace("_model.h5", "").replace("_", ".")
            model_path = os.path.join(model_dir, file)
            scaler_path = model_path.replace(".h5", "_scaler.pkl")

            trained_models.append({
                "ticker": ticker,
                "model_file": file,
                "model_size": os.path.getsize(model_path),
                "has_scaler": os.path.exists(scaler_path),
                "modified_time": os.path.getmtime(model_path)
            })

    return {
        "trained_models": sorted(trained_models, key=lambda x: x['modified_time'], reverse=True),
        "count": len(trained_models)
    }


@router.get("/cache/status")
def get_cache_status(db: Session = Depends(get_db)):
    """Get cache statistics for all caches"""
    # Get in-memory cache stats
    stock_info_stats = stock_info_cache.get_stats()
    stock_quote_stats = stock_quote_cache.get_stats()
    analyst_targets_stats = analyst_targets_cache.get_stats()

    # Get database cache stats
    total_predictions = db.query(PredictionCache).count()
    active_predictions = (
        db.query(PredictionCache)
        .filter(PredictionCache.expires_at > datetime.utcnow())
        .count()
    )
    expired_predictions = total_predictions - active_predictions

    return {
        "in_memory_caches": {
            "stock_info": {
                **stock_info_stats,
                "ttl_seconds": 3600,
                "description": "Stock information (name, sector, etc.)"
            },
            "stock_quote": {
                **stock_quote_stats,
                "ttl_seconds": 300,
                "description": "Current stock prices"
            },
            "analyst_targets": {
                **analyst_targets_stats,
                "ttl_seconds": 3600,
                "description": "Analyst price targets and recommendations"
            },
        },
        "database_cache": {
            "predictions": {
                "total_entries": total_predictions,
                "active_entries": active_predictions,
                "expired_entries": expired_predictions,
                "ttl_seconds": 3600,
                "description": "ML prediction results"
            }
        },
        "summary": {
            "total_in_memory_entries": (
                stock_info_stats["total_entries"] +
                stock_quote_stats["total_entries"] +
                analyst_targets_stats["total_entries"]
            ),
            "total_database_entries": total_predictions,
        }
    }


@router.post("/cache/clear")
def clear_all_caches(db: Session = Depends(get_db)):
    """Clear all cache entries (in-memory and database)"""
    # Clear in-memory caches
    stock_info_cache.clear()
    stock_quote_cache.clear()
    analyst_targets_cache.clear()

    # Clear database cache
    db.query(PredictionCache).delete()
    db.commit()

    return {
        "status": "success",
        "message": "All caches cleared successfully"
    }


@router.post("/cache/cleanup")
def cleanup_expired_cache(db: Session = Depends(get_db)):
    """Remove expired cache entries"""
    # Cleanup in-memory caches
    stock_info_expired = stock_info_cache.cleanup_expired()
    stock_quote_expired = stock_quote_cache.cleanup_expired()
    analyst_targets_expired = analyst_targets_cache.cleanup_expired()

    # Cleanup database cache
    expired_count = (
        db.query(PredictionCache)
        .filter(PredictionCache.expires_at <= datetime.utcnow())
        .count()
    )
    db.query(PredictionCache).filter(
        PredictionCache.expires_at <= datetime.utcnow()
    ).delete()
    db.commit()

    return {
        "status": "success",
        "removed": {
            "in_memory": {
                "stock_info": stock_info_expired,
                "stock_quote": stock_quote_expired,
                "analyst_targets": analyst_targets_expired,
            },
            "database": {
                "predictions": expired_count
            }
        },
        "total_removed": (
            stock_info_expired + stock_quote_expired +
            analyst_targets_expired + expired_count
        )
    }


@router.get("/circuit-breaker/status")
def get_circuit_breaker_status():
    """Get Yahoo Finance API circuit breaker status"""
    return {
        "status": "success",
        "circuit_breaker": yfinance_circuit_breaker.get_status()
    }


@router.post("/circuit-breaker/reset")
def reset_circuit_breaker():
    """Manually reset the Yahoo Finance API circuit breaker"""
    yfinance_circuit_breaker.reset()
    return {
        "status": "success",
        "message": "Circuit breaker has been reset. API calls will resume immediately."
    }
