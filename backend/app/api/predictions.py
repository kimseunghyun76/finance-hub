"""Prediction API endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.ml.predictor import StockPredictor
from app.services.data_fetcher import StockDataFetcher
from app.services.prediction_validator import PredictionValidator
from app.services.cache import stock_info_cache, STOCK_INFO_TTL
from app.models.prediction_cache import PredictionCache
from app.models.daily_prediction import DailyPrediction
from app.models.validation_history import ValidationHistory
from app.database import get_db
from datetime import datetime, date, timedelta
from typing import List, Optional
import os
import sys

router = APIRouter()

# Model directory
MODEL_DIR = "models"

# Add scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


# Pydantic models for daily predictions
class DailyPredictionCreate(BaseModel):
    ticker: str
    prediction_date: date
    target_date: date
    predicted_price: float
    current_price: float
    predicted_change: float
    predicted_change_percent: float
    confidence: float
    action: str
    model_type: Optional[str] = None


class DailyPredictionUpdate(BaseModel):
    actual_price: float
    actual_change: float
    actual_change_percent: float


@router.get("/summary")
def get_predictions_summary(db: Session = Depends(get_db)):
    """
    Get prediction summary for all trained models (for Treemap visualization)

    Returns predictions grouped by action (BUY/SELL/HOLD) with company info
    """
    from app.api.stocks import get_stock_info

    if not os.path.exists(MODEL_DIR):
        return {"predictions": [], "count": 0}

    predictions = []

    # Get all trained models
    for file in os.listdir(MODEL_DIR):
        if file.endswith("_model.h5"):
            # Extract base ticker (remove model type suffix like .LSTM, .GRU)
            ticker_with_model = file.replace("_model.h5", "").replace("_", ".")

            # Remove model type suffix to get clean ticker
            ticker = ticker_with_model
            for model_type in ['.LSTM', '.GRU', '.TRANSFORMER', '.CNN.LSTM', '.ENSEMBLE', '.PROPHET', '.XGBOOST']:
                if ticker.endswith(model_type):
                    ticker = ticker[:-len(model_type)]
                    break

            # Skip if we already have this ticker
            if any(p['ticker'] == ticker for p in predictions):
                continue

            try:
                # Get cached prediction
                cached_prediction = (
                    db.query(PredictionCache)
                    .filter(PredictionCache.ticker == ticker)
                    .filter(PredictionCache.expires_at > datetime.utcnow())
                    .first()
                )

                if not cached_prediction:
                    # Try to get fresh prediction
                    try:
                        pred_data = predict_stock_price(ticker, db)
                        if pred_data:
                            cached_prediction = (
                                db.query(PredictionCache)
                                .filter(PredictionCache.ticker == ticker)
                                .filter(PredictionCache.expires_at > datetime.utcnow())
                                .first()
                            )
                    except:
                        continue

                if cached_prediction:
                    # Get stock info
                    try:
                        stock_info = get_stock_info(ticker, db)
                        company_name = stock_info.get('name', ticker)
                        sector = stock_info.get('sector', 'Unknown')
                        market_cap = stock_info.get('market_cap', 0)
                    except:
                        company_name = ticker
                        sector = 'Unknown'
                        market_cap = 0

                    predictions.append({
                        'ticker': ticker,
                        'name': company_name,
                        'action': cached_prediction.action,
                        'confidence': float(cached_prediction.confidence),
                        'change_percent': float(cached_prediction.change_percent),
                        'predicted_price': float(cached_prediction.predicted_price),
                        'current_price': float(cached_prediction.current_price),
                        'sector': sector,
                        'market_cap': market_cap,
                        'market': 'KRX' if (ticker.endswith('.KS') or ticker.endswith('.KQ')) else 'US'
                    })
            except Exception as e:
                print(f"Error getting prediction for {ticker}: {e}")
                continue

    # Group by action for easier filtering
    grouped = {
        'BUY': [p for p in predictions if p['action'] == 'BUY'],
        'SELL': [p for p in predictions if p['action'] == 'SELL'],
        'HOLD': [p for p in predictions if p['action'] == 'HOLD']
    }

    return {
        'predictions': predictions,
        'grouped': grouped,
        'count': len(predictions),
        'summary': {
            'buy_count': len(grouped['BUY']),
            'sell_count': len(grouped['SELL']),
            'hold_count': len(grouped['HOLD'])
        }
    }


@router.post("/daily/save")
def save_daily_prediction(
    prediction: DailyPredictionCreate,
    db: Session = Depends(get_db)
):
    """Save or update a daily prediction"""
    try:
        # Check if prediction already exists
        existing = db.query(DailyPrediction).filter(
            DailyPrediction.ticker == prediction.ticker,
            DailyPrediction.prediction_date == prediction.prediction_date,
            DailyPrediction.target_date == prediction.target_date
        ).first()

        if existing:
            # Update existing prediction
            for key, value in prediction.dict().items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return {
                "status": "updated",
                "prediction": {
                    "id": existing.id,
                    "ticker": existing.ticker,
                    "prediction_date": existing.prediction_date.isoformat(),
                    "target_date": existing.target_date.isoformat(),
                    "predicted_price": existing.predicted_price,
                    "confidence": existing.confidence,
                    "action": existing.action
                }
            }
        else:
            # Create new prediction
            new_prediction = DailyPrediction(**prediction.dict())
            db.add(new_prediction)
            db.commit()
            db.refresh(new_prediction)
            return {
                "status": "created",
                "prediction": {
                    "id": new_prediction.id,
                    "ticker": new_prediction.ticker,
                    "prediction_date": new_prediction.prediction_date.isoformat(),
                    "target_date": new_prediction.target_date.isoformat(),
                    "predicted_price": new_prediction.predicted_price,
                    "confidence": new_prediction.confidence,
                    "action": new_prediction.action
                }
            }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save prediction: {str(e)}"
        )


@router.post("/daily/save-batch")
def save_daily_predictions_batch(
    predictions: List[DailyPredictionCreate],
    db: Session = Depends(get_db)
):
    """Save multiple daily predictions at once"""
    try:
        results = {"created": 0, "updated": 0, "failed": 0}

        for prediction in predictions:
            try:
                # Check if prediction already exists
                existing = db.query(DailyPrediction).filter(
                    DailyPrediction.ticker == prediction.ticker,
                    DailyPrediction.prediction_date == prediction.prediction_date,
                    DailyPrediction.target_date == prediction.target_date
                ).first()

                if existing:
                    # Update existing prediction
                    for key, value in prediction.dict().items():
                        setattr(existing, key, value)
                    results["updated"] += 1
                else:
                    # Create new prediction
                    new_prediction = DailyPrediction(**prediction.dict())
                    db.add(new_prediction)
                    results["created"] += 1
            except Exception as e:
                results["failed"] += 1
                print(f"Failed to save prediction for {prediction.ticker}: {str(e)}")

        db.commit()
        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save predictions: {str(e)}"
        )


@router.get("/daily")
def get_daily_predictions(
    ticker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    has_actuals: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get daily predictions with optional filters"""
    try:
        query = db.query(DailyPrediction)

        # Apply filters
        if ticker:
            query = query.filter(DailyPrediction.ticker == ticker)

        if start_date:
            query = query.filter(DailyPrediction.prediction_date >= start_date)

        if end_date:
            query = query.filter(DailyPrediction.prediction_date <= end_date)

        if has_actuals is not None:
            if has_actuals:
                query = query.filter(DailyPrediction.actual_price.isnot(None))
            else:
                query = query.filter(DailyPrediction.actual_price.is_(None))

        # Order by date descending
        predictions = query.order_by(DailyPrediction.prediction_date.desc()).all()

        return {
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "ticker": p.ticker,
                    "prediction_date": p.prediction_date.isoformat(),
                    "target_date": p.target_date.isoformat(),
                    "predicted_price": p.predicted_price,
                    "current_price": p.current_price,
                    "predicted_change": p.predicted_change,
                    "predicted_change_percent": p.predicted_change_percent,
                    "confidence": p.confidence,
                    "action": p.action,
                    "actual_price": p.actual_price,
                    "actual_change": p.actual_change,
                    "actual_change_percent": p.actual_change_percent,
                    "price_error": p.price_error,
                    "price_error_percent": p.price_error_percent,
                    "direction_correct": p.direction_correct,
                    "model_type": p.model_type,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in predictions
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get predictions: {str(e)}"
        )


@router.post("/daily/{prediction_id}/update-actuals")
def update_prediction_actuals(
    prediction_id: int,
    actuals: DailyPredictionUpdate,
    db: Session = Depends(get_db)
):
    """Update a prediction with actual results and calculate accuracy metrics"""
    try:
        prediction = db.query(DailyPrediction).filter(
            DailyPrediction.id == prediction_id
        ).first()

        if not prediction:
            raise HTTPException(
                status_code=404,
                detail=f"Prediction {prediction_id} not found"
            )

        # Update actual values
        prediction.actual_price = actuals.actual_price
        prediction.actual_change = actuals.actual_change
        prediction.actual_change_percent = actuals.actual_change_percent

        # Calculate accuracy metrics
        prediction.price_error = abs(prediction.predicted_price - actuals.actual_price)
        prediction.price_error_percent = abs(
            (prediction.predicted_price - actuals.actual_price) / actuals.actual_price * 100
        )

        # Check if direction was correct
        predicted_direction = "up" if prediction.predicted_change > 0 else "down" if prediction.predicted_change < 0 else "neutral"
        actual_direction = "up" if actuals.actual_change > 0 else "down" if actuals.actual_change < 0 else "neutral"
        prediction.direction_correct = (predicted_direction == actual_direction)

        db.commit()
        db.refresh(prediction)

        return {
            "status": "updated",
            "prediction": {
                "id": prediction.id,
                "ticker": prediction.ticker,
                "predicted_price": prediction.predicted_price,
                "actual_price": prediction.actual_price,
                "price_error": prediction.price_error,
                "price_error_percent": prediction.price_error_percent,
                "direction_correct": prediction.direction_correct
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update actuals: {str(e)}"
        )


@router.post("/daily/update-actuals-batch")
def update_actuals_batch(
    target_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Update actual results for predictions whose target date has passed
    Fetches current prices from yfinance for all pending predictions
    """
    try:
        # If no target_date provided, use yesterday
        if not target_date:
            target_date = date.today() - timedelta(days=1)

        # Get predictions that need actual data
        predictions = db.query(DailyPrediction).filter(
            DailyPrediction.target_date == target_date,
            DailyPrediction.actual_price.is_(None)
        ).all()

        if not predictions:
            return {
                "status": "no_predictions_to_update",
                "target_date": target_date.isoformat(),
                "count": 0
            }

        # Fetch actual prices
        fetcher = StockDataFetcher()
        updated_count = 0
        failed_count = 0

        for prediction in predictions:
            try:
                # Get stock data for target date
                data = fetcher.fetch_stock_data(prediction.ticker, period="5d")

                if data is not None and not data.empty:
                    # Find the closest date to target_date
                    target_data = data[data.index.date == target_date]

                    if not target_data.empty:
                        actual_price = float(target_data['Close'].iloc[0])
                        actual_change = actual_price - prediction.current_price
                        actual_change_percent = (actual_change / prediction.current_price) * 100

                        # Update prediction
                        prediction.actual_price = actual_price
                        prediction.actual_change = actual_change
                        prediction.actual_change_percent = actual_change_percent

                        # Calculate accuracy metrics
                        prediction.price_error = abs(prediction.predicted_price - actual_price)
                        prediction.price_error_percent = abs(
                            (prediction.predicted_price - actual_price) / actual_price * 100
                        )

                        # Check direction
                        predicted_direction = "up" if prediction.predicted_change > 0 else "down" if prediction.predicted_change < 0 else "neutral"
                        actual_direction = "up" if actual_change > 0 else "down" if actual_change < 0 else "neutral"
                        prediction.direction_correct = (predicted_direction == actual_direction)

                        updated_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Failed to update {prediction.ticker}: {str(e)}")
                failed_count += 1

        db.commit()

        return {
            "status": "completed",
            "target_date": target_date.isoformat(),
            "total": len(predictions),
            "updated": updated_count,
            "failed": failed_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update actuals: {str(e)}"
        )


@router.get("/daily/accuracy")
def get_prediction_accuracy(
    ticker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get accuracy statistics for all AI model predictions"""
    try:
        # Get count of trained models
        trained_models_count = 0
        if os.path.exists(MODEL_DIR):
            trained_models_count = len([f for f in os.listdir(MODEL_DIR) if f.endswith("_model.h5")])

        # Query predictions with actual results
        query = db.query(DailyPrediction).filter(
            DailyPrediction.actual_price.isnot(None)
        )

        if ticker:
            query = query.filter(DailyPrediction.ticker == ticker)

        if start_date:
            query = query.filter(DailyPrediction.prediction_date >= start_date)

        if end_date:
            query = query.filter(DailyPrediction.prediction_date <= end_date)

        predictions = query.all()

        # Count unique tickers in predictions
        unique_tickers = len(set(p.ticker for p in predictions)) if predictions else 0

        if not predictions:
            return {
                "status": "no_data",
                "count": 0,
                "trained_models": trained_models_count,
                "tested_models": 0,
                "accuracy": None
            }

        # Calculate statistics
        total = len(predictions)
        direction_correct = sum(1 for p in predictions if p.direction_correct)
        direction_accuracy = (direction_correct / total) * 100

        avg_price_error = sum(p.price_error for p in predictions) / total
        avg_price_error_percent = sum(p.price_error_percent for p in predictions) / total

        # Group by action
        by_action = {}
        for action in ["BUY", "SELL", "HOLD"]:
            action_preds = [p for p in predictions if p.action == action]
            if action_preds:
                action_correct = sum(1 for p in action_preds if p.direction_correct)
                by_action[action] = {
                    "count": len(action_preds),
                    "direction_accuracy": (action_correct / len(action_preds)) * 100,
                    "avg_price_error": sum(p.price_error for p in action_preds) / len(action_preds),
                    "avg_price_error_percent": sum(p.price_error_percent for p in action_preds) / len(action_preds)
                }

        # Recent predictions (last 10)
        recent = sorted(predictions, key=lambda p: p.prediction_date, reverse=True)[:10]

        return {
            "count": total,
            "trained_models": trained_models_count,
            "tested_models": unique_tickers,
            "overall": {
                "direction_accuracy": round(direction_accuracy, 2),
                "direction_correct": direction_correct,
                "direction_incorrect": total - direction_correct,
                "avg_price_error": round(avg_price_error, 2),
                "avg_price_error_percent": round(avg_price_error_percent, 2)
            },
            "by_action": by_action,
            "recent_predictions": [
                {
                    "ticker": p.ticker,
                    "prediction_date": p.prediction_date.isoformat(),
                    "target_date": p.target_date.isoformat(),
                    "action": p.action,
                    "predicted_price": p.predicted_price,
                    "actual_price": p.actual_price,
                    "price_error": p.price_error,
                    "price_error_percent": p.price_error_percent,
                    "direction_correct": p.direction_correct
                }
                for p in recent
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get accuracy: {str(e)}"
        )


@router.post("/daily/refresh-validation")
def refresh_validation(
    db: Session = Depends(get_db)
):
    """
    Re-validate all predictions whose target date has passed.
    Fetches current prices and updates validation metrics.
    Logs the validation run to validation_history table.
    """
    try:
        today = date.today()

        # Get all predictions that need validation (target_date <= today and no actual_price)
        pending_predictions = db.query(DailyPrediction).filter(
            DailyPrediction.target_date <= today,
            DailyPrediction.actual_price.is_(None)
        ).all()

        if not pending_predictions:
            # Still log the validation attempt
            history_entry = ValidationHistory(
                validation_date=datetime.utcnow(),
                predictions_validated=0,
                predictions_skipped=0,
                direction_correct=0,
                direction_incorrect=0,
                success_rate=0.0,
                avg_price_error=None,
                avg_price_error_percent=None
            )
            db.add(history_entry)
            db.commit()

            return {
                "status": "no_pending_predictions",
                "message": "검증 대기 중인 예측이 없습니다",
                "validated": 0,
                "skipped": 0,
                "success_rate": None
            }

        # Fetch actual prices and validate
        fetcher = StockDataFetcher()
        validated_count = 0
        skipped_count = 0
        direction_correct_count = 0
        direction_incorrect_count = 0
        total_price_error = 0.0
        total_price_error_percent = 0.0

        for prediction in pending_predictions:
            try:
                # Get stock data for target date
                data = fetcher.fetch_stock_data(prediction.ticker, period="1mo")

                if data is not None and not data.empty:
                    # Find the closest date to target_date
                    target_data = data[data.index.date == prediction.target_date]

                    if target_data.empty:
                        # Try to get the nearest available date
                        data = data[data.index.date <= prediction.target_date]
                        if not data.empty:
                            target_data = data.iloc[[-1]]
                        else:
                            skipped_count += 1
                            continue

                    actual_price = float(target_data['Close'].iloc[0])
                    actual_change = actual_price - prediction.current_price
                    actual_change_percent = (actual_change / prediction.current_price) * 100

                    # Update prediction
                    prediction.actual_price = actual_price
                    prediction.actual_change = actual_change
                    prediction.actual_change_percent = actual_change_percent

                    # Calculate accuracy metrics
                    price_error = abs(prediction.predicted_price - actual_price)
                    price_error_percent = abs(
                        (prediction.predicted_price - actual_price) / actual_price * 100
                    )
                    prediction.price_error = price_error
                    prediction.price_error_percent = price_error_percent

                    # Check direction
                    predicted_direction = "up" if prediction.predicted_change > 0 else "down" if prediction.predicted_change < 0 else "neutral"
                    actual_direction = "up" if actual_change > 0 else "down" if actual_change < 0 else "neutral"
                    direction_correct = (predicted_direction == actual_direction)
                    prediction.direction_correct = direction_correct

                    validated_count += 1
                    total_price_error += price_error
                    total_price_error_percent += price_error_percent

                    if direction_correct:
                        direction_correct_count += 1
                    else:
                        direction_incorrect_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                print(f"Failed to validate {prediction.ticker}: {str(e)}")
                skipped_count += 1

        # Calculate success rate
        total_validated = direction_correct_count + direction_incorrect_count
        success_rate = (direction_correct_count / total_validated * 100) if total_validated > 0 else 0.0
        avg_price_error = total_price_error / validated_count if validated_count > 0 else None
        avg_price_error_percent = total_price_error_percent / validated_count if validated_count > 0 else None

        # Log validation history
        history_entry = ValidationHistory(
            validation_date=datetime.utcnow(),
            predictions_validated=validated_count,
            predictions_skipped=skipped_count,
            direction_correct=direction_correct_count,
            direction_incorrect=direction_incorrect_count,
            success_rate=success_rate,
            avg_price_error=avg_price_error,
            avg_price_error_percent=avg_price_error_percent
        )
        db.add(history_entry)
        db.commit()

        return {
            "status": "completed",
            "message": f"{validated_count}개 예측 검증 완료",
            "validated": validated_count,
            "skipped": skipped_count,
            "direction_correct": direction_correct_count,
            "direction_incorrect": direction_incorrect_count,
            "success_rate": round(success_rate, 2),
            "avg_price_error": round(avg_price_error, 2) if avg_price_error else None,
            "avg_price_error_percent": round(avg_price_error_percent, 2) if avg_price_error_percent else None,
            "validation_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"검증 실패: {str(e)}"
        )


@router.get("/daily/validation-history")
def get_validation_history_list(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get validation history log.
    Returns list of past validation runs with their metrics.
    """
    try:
        history = db.query(ValidationHistory).order_by(
            ValidationHistory.validation_date.desc()
        ).limit(limit).all()

        return {
            "count": len(history),
            "history": [
                {
                    "id": h.id,
                    "validation_date": h.validation_date.isoformat() if h.validation_date else None,
                    "predictions_validated": h.predictions_validated,
                    "predictions_skipped": h.predictions_skipped,
                    "direction_correct": h.direction_correct,
                    "direction_incorrect": h.direction_incorrect,
                    "success_rate": h.success_rate,
                    "avg_price_error": h.avg_price_error,
                    "avg_price_error_percent": h.avg_price_error_percent,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation history: {str(e)}"
        )


@router.get("/daily/model-info")
def get_model_info(db: Session = Depends(get_db)):
    """
    Get information about all trained models including training dates.
    """
    try:
        if not os.path.exists(MODEL_DIR):
            return {
                "models": [],
                "count": 0,
                "last_trained": None,
                "last_validation": None
            }

        models = []
        latest_trained = None

        for file in os.listdir(MODEL_DIR):
            if file.endswith("_model.h5"):
                ticker = file.replace("_model.h5", "").replace("_", ".")
                model_path = os.path.join(MODEL_DIR, file)

                try:
                    mtime = os.path.getmtime(model_path)
                    last_trained = datetime.fromtimestamp(mtime)
                    file_size = os.path.getsize(model_path)

                    if latest_trained is None or last_trained > latest_trained:
                        latest_trained = last_trained

                    models.append({
                        "ticker": ticker,
                        "last_trained": last_trained.isoformat(),
                        "file_size_mb": round(file_size / (1024 * 1024), 2)
                    })
                except Exception as e:
                    print(f"Error getting model info for {ticker}: {e}")
                    continue

        # Get last validation date
        last_validation_record = db.query(ValidationHistory).order_by(
            ValidationHistory.validation_date.desc()
        ).first()

        # Get total validation count
        total_validations = db.query(ValidationHistory).count()

        return {
            "models": sorted(models, key=lambda x: x.get("last_trained", ""), reverse=True),
            "count": len(models),
            "last_trained": latest_trained.isoformat() if latest_trained else None,
            "last_validation": last_validation_record.validation_date.isoformat() if last_validation_record and last_validation_record.validation_date else None,
            "total_validations": total_validations
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.get("/{ticker}")
def predict_stock_price(ticker: str, db: Session = Depends(get_db)):
    """
    Predict stock price using LSTM model with database caching

    Args:
        ticker: Stock ticker symbol
        db: Database session

    Returns:
        Prediction results (from cache if available and not expired)
    """
    # Check cache first
    cached_prediction = (
        db.query(PredictionCache)
        .filter(PredictionCache.ticker == ticker)
        .filter(PredictionCache.expires_at > datetime.utcnow())
        .first()
    )

    if cached_prediction:
        print(f"✅ Returning cached prediction for {ticker}")
        return cached_prediction.to_dict()

    # Check if model exists
    model_path = os.path.join(MODEL_DIR, f"{ticker.replace('.', '_')}_model.h5")

    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No trained model found for {ticker}. Please train the model first."
        )

    try:
        # Load model
        predictor = StockPredictor(model_path=model_path)

        # Fetch recent data
        df = StockDataFetcher.fetch_yahoo_finance(ticker, period="3mo")

        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for {ticker}"
            )

        # Make prediction
        prediction = predictor.predict(df)

        # Determine action
        if prediction['change_percent'] > 2:
            action = "BUY"
        elif prediction['change_percent'] < -2:
            action = "SELL"
        else:
            action = "HOLD"

        # Save to cache
        cache_entry = PredictionCache(
            ticker=ticker,
            predicted_price=prediction['predicted_price'],
            current_price=prediction['current_price'],
            change=prediction['change'],
            change_percent=prediction['change_percent'],
            confidence=prediction['confidence'],
            action=action,
            forecast_days=prediction.get('forecast_days', 5),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + PredictionCache.get_cache_duration()
        )
        db.add(cache_entry)
        db.commit()
        db.refresh(cache_entry)
        print(f"💾 Cached prediction for {ticker} (expires in 1 hour)")

        return {
            "ticker": ticker,
            "prediction": prediction,
            "action": action,
            "timestamp": df['date'].iloc[-1].isoformat() if hasattr(df['date'].iloc[-1], 'isoformat') else str(df['date'].iloc[-1]),
            "created_at": cache_entry.created_at.isoformat(),
            "expires_at": cache_entry.expires_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.get("/")
def list_trained_models():
    """
    List all trained models

    Returns:
        List of trained ticker symbols
    """
    if not os.path.exists(MODEL_DIR):
        return {"trained_models": []}

    trained_models = []
    for file in os.listdir(MODEL_DIR):
        if file.endswith("_model.h5"):
            # Extract ticker from filename (e.g., "AAPL_model.h5" -> "AAPL")
            ticker = file.replace("_model.h5", "").replace("_", ".")
            trained_models.append(ticker)

    return {
        "trained_models": sorted(trained_models),
        "count": len(trained_models)
    }


@router.get("/{ticker}/train-status")
def get_train_status(ticker: str):
    """Check if model is trained for a ticker"""
    model_path = os.path.join(MODEL_DIR, f"{ticker.replace('.', '_')}_model.h5")
    trained = os.path.exists(model_path)

    # Get last modified time if model exists
    last_trained = None
    if trained:
        try:
            last_trained = datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat()
        except:
            pass

    return {
        "ticker": ticker,
        "trained": trained,
        "model_path": model_path if trained else None,
        "last_trained": last_trained,
    }


@router.post("/train/{ticker}")
async def train_model(ticker: str, background_tasks: BackgroundTasks):
    """Trigger training for a specific ticker"""
    from scripts.train_model import train_model_for_ticker

    def train_task(ticker: str):
        try:
            train_model_for_ticker(ticker, save_dir=MODEL_DIR)
        except Exception as e:
            print(f"Training failed for {ticker}: {str(e)}")

    background_tasks.add_task(train_task, ticker)

    return {
        "message": f"Training started for {ticker}",
        "ticker": ticker,
        "status": "training"
    }


@router.post("/train-all")
async def train_all(background_tasks: BackgroundTasks):
    """Trigger training for all models"""
    from app.services.scheduler import train_all_models

    background_tasks.add_task(train_all_models)

    return {
        "message": "Training started for all models",
        "status": "training"
    }


@router.delete("/{ticker}/model")
def delete_model(ticker: str):
    """Delete a trained model"""
    model_path = os.path.join(MODEL_DIR, f"{ticker.replace('.', '_')}_model.h5")
    scaler_path = model_path.replace('.h5', '_scaler.pkl')

    deleted = False

    if os.path.exists(model_path):
        os.remove(model_path)
        deleted = True

    if os.path.exists(scaler_path):
        os.remove(scaler_path)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No model found for {ticker}"
        )

    return {
        "message": f"Model deleted for {ticker}",
        "ticker": ticker
    }


@router.delete("/models/all")
def delete_all_models():
    """Delete all trained models"""
    if not os.path.exists(MODEL_DIR):
        return {
            "message": "No models directory found",
            "deleted_count": 0
        }

    deleted_count = 0
    deleted_tickers = []

    # Delete all model files
    for file in os.listdir(MODEL_DIR):
        if file.endswith("_model.h5") or file.endswith("_scaler.pkl"):
            file_path = os.path.join(MODEL_DIR, file)
            try:
                os.remove(file_path)
                if file.endswith("_model.h5"):
                    ticker = file.replace("_model.h5", "").replace("_", ".")
                    deleted_tickers.append(ticker)
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file}: {e}")

    return {
        "message": f"Deleted {deleted_count} models",
        "deleted_count": deleted_count,
        "tickers": deleted_tickers
    }


@router.get("/models/details")
def get_all_models_details(db: Session = Depends(get_db)):
    """Get detailed information about all trained models"""
    from app.api.stocks import get_stock_info

    if not os.path.exists(MODEL_DIR):
        return {"models": []}

    models = []
    for file in os.listdir(MODEL_DIR):
        if file.endswith("_model.h5"):
            ticker = file.replace("_model.h5", "").replace("_", ".")
            model_path = os.path.join(MODEL_DIR, file)

            try:
                last_trained = datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat()
                file_size = os.path.getsize(model_path)
            except:
                last_trained = None
                file_size = 0

            # Get company name
            company_name = ticker
            try:
                stock_info = get_stock_info(ticker, db)
                if stock_info and 'name' in stock_info:
                    company_name = stock_info['name']
            except Exception as e:
                print(f"Could not fetch name for {ticker}: {e}")

            models.append({
                "ticker": ticker,
                "company_name": company_name,
                "trained": True,
                "last_trained": last_trained,
                "file_size": file_size,
                "model_path": model_path
            })

    return {
        "models": sorted(models, key=lambda x: x.get("last_trained", "") or "", reverse=True),
        "count": len(models)
    }


@router.get("/training/status")
def get_training_status(db: Session = Depends(get_db)):
    """
    Get training status for all models

    Returns recent training activity and model information
    """
    from app.api.stocks import get_stock_info

    if not os.path.exists(MODEL_DIR):
        return {
            "models": [],
            "total_models": 0,
            "recently_trained": [],
            "last_update": None
        }

    models = []
    now = datetime.utcnow()

    for file in os.listdir(MODEL_DIR):
        if file.endswith("_model.h5"):
            ticker = file.replace("_model.h5", "").replace("_", ".")
            model_path = os.path.join(MODEL_DIR, file)

            try:
                # Get file modification time
                mtime = os.path.getmtime(model_path)
                last_trained = datetime.fromtimestamp(mtime)
                file_size = os.path.getsize(model_path)

                # Calculate hours since last training
                hours_ago = (now - last_trained).total_seconds() / 3600

                # Get stock info
                try:
                    stock_info = get_stock_info(ticker, db)
                    company_name = stock_info.get('name', ticker)
                except:
                    company_name = ticker

                model_info = {
                    "ticker": ticker,
                    "name": company_name,
                    "last_trained": last_trained.isoformat(),
                    "hours_ago": round(hours_ago, 1),
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "model_path": model_path
                }

                models.append(model_info)

            except Exception as e:
                print(f"Error getting training status for {ticker}: {e}")
                continue

    # Sort by most recently trained
    models.sort(key=lambda x: x.get("last_trained", ""), reverse=True)

    # Get recently trained models (within last 24 hours)
    recently_trained = [m for m in models if m.get("hours_ago", float('inf')) < 24]

    return {
        "models": models,
        "total_models": len(models),
        "recently_trained": recently_trained,
        "recently_trained_count": len(recently_trained),
        "last_update": models[0]["last_trained"] if models else None
    }


# ============================================
# Sector Analysis & Recommendations
# ============================================

@router.get("/sectors/analysis")
def get_sector_analysis(db: Session = Depends(get_db)):
    """
    Analyze sector performance based on AI predictions

    Returns sector-level metrics including:
    - Average predicted change by sector
    - Stock count and distribution
    - BUY/SELL/HOLD recommendations per sector
    - Market breakdown (US vs KR)
    """
    from app.api.stocks import get_stock_info

    if not os.path.exists(MODEL_DIR):
        return {
            "sectors": [],
            "total_sectors": 0,
            "us_sectors": [],
            "kr_sectors": []
        }

    # Collect all predictions with sector info
    sector_data = {}

    for file in os.listdir(MODEL_DIR):
        if file.endswith("_model.h5"):
            ticker = file.replace("_model.h5", "").replace("_", ".")

            try:
                # Get cached prediction
                cached_prediction = (
                    db.query(PredictionCache)
                    .filter(PredictionCache.ticker == ticker)
                    .filter(PredictionCache.expires_at > datetime.utcnow())
                    .first()
                )

                if not cached_prediction:
                    continue

                # Get stock info for sector
                try:
                    stock_info = get_stock_info(ticker, db)
                    sector = stock_info.get('sector', 'Unknown')
                    market = 'KRX' if (ticker.endswith('.KS') or ticker.endswith('.KQ')) else 'US'
                except:
                    sector = 'Unknown'
                    market = 'US'

                # Initialize sector data
                if sector not in sector_data:
                    sector_data[sector] = {
                        'sector': sector,
                        'stocks': [],
                        'avg_change_percent': 0,
                        'total_stocks': 0,
                        'buy_count': 0,
                        'sell_count': 0,
                        'hold_count': 0,
                        'us_count': 0,
                        'kr_count': 0,
                        'momentum_score': 0  # Calculated later
                    }

                # Add stock data
                sector_data[sector]['stocks'].append({
                    'ticker': ticker,
                    'action': cached_prediction.action,
                    'change_percent': float(cached_prediction.change_percent),
                    'confidence': float(cached_prediction.confidence),
                    'market': market
                })

                sector_data[sector]['total_stocks'] += 1

                # Count actions
                if cached_prediction.action == 'BUY':
                    sector_data[sector]['buy_count'] += 1
                elif cached_prediction.action == 'SELL':
                    sector_data[sector]['sell_count'] += 1
                else:
                    sector_data[sector]['hold_count'] += 1

                # Count markets
                if market == 'US':
                    sector_data[sector]['us_count'] += 1
                else:
                    sector_data[sector]['kr_count'] += 1

            except Exception as e:
                print(f"Error analyzing sector for {ticker}: {e}")
                continue

    # Calculate sector metrics
    sectors = []
    for sector, data in sector_data.items():
        # Average change percent
        avg_change = sum(s['change_percent'] for s in data['stocks']) / len(data['stocks']) if data['stocks'] else 0
        data['avg_change_percent'] = round(avg_change, 2)

        # Momentum score: combination of avg change and buy ratio
        buy_ratio = data['buy_count'] / data['total_stocks'] if data['total_stocks'] > 0 else 0
        sell_ratio = data['sell_count'] / data['total_stocks'] if data['total_stocks'] > 0 else 0

        # Score: positive change + high buy ratio - sell ratio
        momentum = (avg_change * 0.6) + (buy_ratio * 30) - (sell_ratio * 20)
        data['momentum_score'] = round(momentum, 2)

        # Recommendation
        if momentum > 5 and buy_ratio > 0.4:
            data['recommendation'] = 'STRONG_BUY'
        elif momentum > 2 and buy_ratio > 0.3:
            data['recommendation'] = 'BUY'
        elif momentum < -5 or sell_ratio > 0.5:
            data['recommendation'] = 'AVOID'
        else:
            data['recommendation'] = 'NEUTRAL'

        # Remove detailed stocks from response (too much data)
        data['top_picks'] = sorted(
            [s for s in data['stocks'] if s['action'] == 'BUY'],
            key=lambda x: x['change_percent'],
            reverse=True
        )[:3]  # Top 3 buy recommendations

        del data['stocks']  # Remove full stock list

        sectors.append(data)

    # Sort by momentum score
    sectors.sort(key=lambda x: x['momentum_score'], reverse=True)

    # Separate US and KR sectors
    us_sectors = [s for s in sectors if s['us_count'] > 0]
    kr_sectors = [s for s in sectors if s['kr_count'] > 0]

    return {
        'sectors': sectors,
        'total_sectors': len(sectors),
        'us_sectors': us_sectors,
        'kr_sectors': kr_sectors,
        'top_momentum_sectors': sectors[:3] if len(sectors) >= 3 else sectors,
        'generated_at': datetime.utcnow().isoformat()
    }


# ============================================
# Stock Discovery & Training Candidates
# ============================================

# Cache for discovery results (30 minutes TTL)
_discovery_cache = {}
_discovery_cache_time = {}

@router.get("/discover/candidates")
def discover_training_candidates(
    market: str = Query('ALL', description="Market filter: US, KR, or ALL"),
    check_signals: bool = Query(True, description="Check for volume/price signals"),
    force_refresh: bool = Query(False, description="Force cache refresh"),
    db: Session = Depends(get_db)
):
    """
    Discover new stocks based on batch predictions (No real-time Yahoo Finance API calls)

    Returns:
    - Stocks with existing predictions from batch processing
    - Action-based recommendations (BUY/SELL signals)
    - Sorted by prediction confidence and change percentage
    """
    from datetime import datetime, timedelta
    from app.api.stocks import get_stock_info

    # Check cache
    cache_key = f"{market}_{check_signals}"
    cache_ttl = timedelta(minutes=30)
    now = datetime.utcnow()

    if not force_refresh and cache_key in _discovery_cache:
        cache_time = _discovery_cache_time.get(cache_key)
        if cache_time and (now - cache_time) < cache_ttl:
            print(f"✅ Returning cached discovery results for {cache_key}")
            return _discovery_cache[cache_key]

    print(f"🔄 Refreshing discovery cache from batch predictions for {cache_key}")

    # Get currently trained models
    trained_tickers = []
    if os.path.exists(MODEL_DIR):
        for file in os.listdir(MODEL_DIR):
            if file.endswith("_model.h5"):
                ticker = file.replace("_model.h5", "").replace("_", ".")
                trained_tickers.append(ticker)

    # Get predictions from PredictionCache (batch predictions)
    cached_predictions = (
        db.query(PredictionCache)
        .filter(PredictionCache.expires_at > datetime.utcnow())
        .all()
    )

    # Get excluded tickers
    from app.models.excluded_ticker import ExcludedTicker
    excluded_tickers = [e.ticker for e in db.query(ExcludedTicker).all()]

    # Build recommendations from batch predictions (deduplicated by ticker)
    recommendations = []
    buy_signals = 0
    sell_signals = 0
    seen_tickers = set()

    for pred in cached_predictions:
        # Skip duplicates
        if pred.ticker in seen_tickers:
            continue

        if pred.ticker in excluded_tickers:
            continue

        # Apply market filter
        if market != 'ALL':
            if market == 'US' and (pred.ticker.endswith('.KS') or pred.ticker.endswith('.KQ')):
                continue
            if market == 'KR' and not (pred.ticker.endswith('.KS') or pred.ticker.endswith('.KQ')):
                continue

        # Get stock info (from cache if available)
        try:
            stock_info = get_stock_info(pred.ticker, db)
        except:
            continue

        # Determine priority based on action and confidence
        priority = 'LOW'
        reason = f"예측: {pred.action}"

        if pred.action == 'BUY' and pred.confidence >= 0.7:
            priority = 'HIGH'
            reason = f"매수 신호 (신뢰도 {pred.confidence*100:.1f}%)"
            buy_signals += 1
        elif pred.action == 'BUY' and pred.confidence >= 0.5:
            priority = 'MEDIUM'
            reason = f"약한 매수 신호 (신뢰도 {pred.confidence*100:.1f}%)"
            buy_signals += 1
        elif pred.action == 'SELL' and pred.confidence >= 0.7:
            priority = 'HIGH'
            reason = f"매도 신호 (신뢰도 {pred.confidence*100:.1f}%)"
            sell_signals += 1
        elif pred.action == 'SELL' and pred.confidence >= 0.5:
            priority = 'MEDIUM'
            reason = f"약한 매도 신호 (신뢰도 {pred.confidence*100:.1f}%)"
            sell_signals += 1

        # Only show meaningful signals if check_signals is True
        if check_signals and priority == 'LOW':
            continue

        # Add to seen tickers
        seen_tickers.add(pred.ticker)

        recommendations.append({
            'ticker': pred.ticker,
            'name': stock_info.get('name', pred.ticker),
            'sector': stock_info.get('sector', 'Unknown'),
            'market_cap': stock_info.get('market_cap', 0),
            'current_price': pred.current_price,
            'priority': priority,
            'reason': reason,
            'signals': [pred.action],
            'confidence': pred.confidence,
            'change_percent': pred.change_percent,
            'predicted_price': pred.predicted_price
        })

    # Sort by priority (HIGH > MEDIUM > LOW) and then by confidence
    priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    recommendations.sort(key=lambda x: (priority_order[x['priority']], x['confidence']), reverse=True)

    result_dict = {
        'trained_count': len(trained_tickers),
        'untrained_count': 0,  # Not relevant for batch predictions
        'recommendations': recommendations[:50],  # Limit to 50
        'signals': {
            'volume_spikes': buy_signals,
            'price_movements': sell_signals,
            'high_priority': len([r for r in recommendations if r['priority'] == 'HIGH'])
        },
        'generated_at': datetime.utcnow().isoformat()
    }

    # Save to cache before returning
    _discovery_cache[cache_key] = result_dict
    _discovery_cache_time[cache_key] = now
    print(f"💾 Cached discovery results for {cache_key}")

    return result_dict


@router.get("/discover/signals")
def get_market_signals(
    market: str = Query('ALL', description="Market filter: US, KR, or ALL"),
):
    """
    Get current market signals (volume spikes, price movements)
    for ALL stocks, not just untrained ones
    """
    from app.services.stock_screener import StockScreener

    candidates = StockScreener.get_all_top_stocks() if market == 'ALL' else StockScreener.get_top_stocks_by_market(market)

    volume_spikes = []
    price_movements = []

    for ticker in candidates:
        # Check volume
        spike = StockScreener.detect_volume_spike(ticker)
        if spike:
            volume_spikes.append(spike)

        # Check price
        movement = StockScreener.detect_price_movement(ticker)
        if movement:
            price_movements.append(movement)

    return {
        'volume_spikes': sorted(volume_spikes, key=lambda x: x['spike_ratio'], reverse=True)[:20],
        'price_movements': sorted(price_movements, key=lambda x: abs(x['change_percent']), reverse=True)[:20],
        'total_checked': len(candidates),
        'generated_at': datetime.utcnow().isoformat()
    }


# ============================================
# Prediction Validation Endpoints
# ============================================

class ValidationSummary(BaseModel):
    validation_date: str
    total_predictions: int
    validated: int
    skipped: int
    message: str


class AccuracyMetrics(BaseModel):
    ticker: str
    model_type: str
    model_version: str
    total_predictions: int
    correct_direction: int
    avg_price_error: float
    avg_price_error_percent: float
    direction_accuracy: float
    price_accuracy: float
    overall_accuracy: float
    period_start: str
    period_end: str

    class Config:
        from_attributes = True


class ValidationHistory(BaseModel):
    validation_date: str
    predicted_price: float
    actual_price: float
    price_error: float
    price_error_percent: float
    direction_correct: bool
    model_type: str
    confidence: float


@router.post("/validate/{validation_date}", response_model=ValidationSummary)
def validate_predictions(
    validation_date: str,
    db: Session = Depends(get_db)
):
    """
    Validate all predictions for a specific date against actual prices

    Args:
        validation_date: Date in YYYY-MM-DD format
    """
    try:
        target_date = datetime.strptime(validation_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Don't validate future dates
    if target_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Cannot validate future dates"
        )

    validator = PredictionValidator(db)
    result = validator.validate_predictions_for_date(target_date)

    return result


@router.post("/validate/today")
def validate_today(db: Session = Depends(get_db)):
    """Validate all predictions targeting today"""
    validator = PredictionValidator(db)
    result = validator.validate_predictions_for_date(date.today())
    return result


@router.get("/accuracy", response_model=List[AccuracyMetrics])
def get_model_accuracy(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    db: Session = Depends(get_db)
):
    """
    Get accuracy metrics for models

    Returns aggregated accuracy metrics for the last 30 days
    """
    validator = PredictionValidator(db)
    accuracy_records = validator.get_model_accuracy(ticker=ticker, model_type=model_type)

    # Convert to response model
    results = []
    for record in accuracy_records:
        results.append(AccuracyMetrics(
            ticker=record.ticker,
            model_type=record.model_type,
            model_version=record.model_version,
            total_predictions=record.total_predictions,
            correct_direction=record.correct_direction,
            avg_price_error=record.avg_price_error,
            avg_price_error_percent=record.avg_price_error_percent,
            direction_accuracy=record.direction_accuracy,
            price_accuracy=record.price_accuracy,
            overall_accuracy=record.overall_accuracy,
            period_start=record.period_start.isoformat(),
            period_end=record.period_end.isoformat()
        ))

    return results


@router.get("/accuracy/{ticker}", response_model=List[AccuracyMetrics])
def get_ticker_accuracy(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get accuracy metrics for a specific ticker across all models"""
    validator = PredictionValidator(db)
    accuracy_records = validator.get_model_accuracy(ticker=ticker)

    if not accuracy_records:
        raise HTTPException(
            status_code=404,
            detail=f"No accuracy data found for ticker {ticker}"
        )

    results = []
    for record in accuracy_records:
        results.append(AccuracyMetrics(
            ticker=record.ticker,
            model_type=record.model_type,
            model_version=record.model_version,
            total_predictions=record.total_predictions,
            correct_direction=record.correct_direction,
            avg_price_error=record.avg_price_error,
            avg_price_error_percent=record.avg_price_error_percent,
            direction_accuracy=record.direction_accuracy,
            price_accuracy=record.price_accuracy,
            overall_accuracy=record.overall_accuracy,
            period_start=record.period_start.isoformat(),
            period_end=record.period_end.isoformat()
        ))

    return results


@router.get("/history/{ticker}", response_model=List[ValidationHistory])
def get_validation_history(
    ticker: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get validation history for a ticker

    Shows how accurate predictions have been over time
    """
    validator = PredictionValidator(db)
    history = validator.get_validation_history(ticker=ticker, days=days)

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No validation history found for ticker {ticker}"
        )

    return history


@router.get("/{ticker}/backtest")
def backtest_prediction(
    ticker: str,
    period: str = Query("3mo", description="Backtest period: 1mo, 3mo, 6mo, 1y"),
    db: Session = Depends(get_db)
):
    """
    Backtest AI predictions against actual historical performance with caching (1 hour TTL)

    Returns:
    - Win rate (% of correct predictions)
    - Average return when following AI recommendations
    - Best/worst trades
    - Month-by-month performance
    """
    # Check cache first
    cache_key = f"backtest_{ticker}_{period}"
    cached_backtest = stock_info_cache.get(cache_key)

    if cached_backtest:
        print(f"✅ Returning cached backtest for {ticker} ({period})")
        return cached_backtest

    import yfinance as yf
    import pandas as pd
    import numpy as np
    from datetime import timedelta

    # Convert period to days
    period_days = {
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365
    }

    days = period_days.get(period, 90)

    try:
        # Fetch historical data
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {ticker}"
            )

        # Simulate predictions on historical data
        # We'll use a rolling window approach
        trades = []
        win_count = 0
        loss_count = 0
        total_return = 0.0

        # Use 5-day prediction window
        prediction_window = 5

        for i in range(len(hist) - prediction_window):
            entry_date = hist.index[i]
            entry_price = hist['Close'].iloc[i]
            exit_date = hist.index[min(i + prediction_window, len(hist) - 1)]
            exit_price = hist['Close'].iloc[min(i + prediction_window, len(hist) - 1)]

            actual_return = ((exit_price - entry_price) / entry_price) * 100

            # Simple prediction logic based on recent trend
            # In real backtest, we'd use the actual model predictions if available
            recent_prices = hist['Close'].iloc[max(0, i-5):i+1]
            trend = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]

            # Predict BUY if uptrend, SELL if downtrend
            predicted_action = "BUY" if trend > 0 else "SELL"

            # Calculate if prediction was correct
            if predicted_action == "BUY" and actual_return > 0:
                win_count += 1
                total_return += actual_return
            elif predicted_action == "SELL" and actual_return < 0:
                win_count += 1
                total_return += abs(actual_return)  # Profit from shorting
            else:
                loss_count += 1
                total_return += actual_return if predicted_action == "BUY" else -actual_return

            trades.append({
                "entry_date": entry_date.strftime("%Y-%m-%d"),
                "exit_date": exit_date.strftime("%Y-%m-%d"),
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "predicted_action": predicted_action,
                "actual_return": float(actual_return),
                "profit": float(actual_return if predicted_action == "BUY" else -actual_return)
            })

        total_trades = win_count + loss_count
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        avg_return = total_return / total_trades if total_trades > 0 else 0

        # Get best and worst trades
        sorted_trades = sorted(trades, key=lambda x: x['profit'], reverse=True)
        best_trades = sorted_trades[:5]
        worst_trades = sorted_trades[-5:]

        # Calculate monthly performance
        df = pd.DataFrame(trades)
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        df['month'] = df['entry_date'].dt.to_period('M')

        monthly_performance = []
        for month in df['month'].unique():
            month_trades = df[df['month'] == month]
            monthly_performance.append({
                "month": str(month),
                "trades": len(month_trades),
                "wins": len(month_trades[month_trades['profit'] > 0]),
                "total_return": float(month_trades['profit'].sum()),
                "avg_return": float(month_trades['profit'].mean())
            })

        result = {
            "ticker": ticker,
            "period": period,
            "summary": {
                "total_trades": total_trades,
                "wins": win_count,
                "losses": loss_count,
                "win_rate": round(win_rate, 2),
                "avg_return": round(avg_return, 2),
                "total_return": round(total_return, 2)
            },
            "best_trades": best_trades,
            "worst_trades": worst_trades,
            "monthly_performance": monthly_performance,
            "all_trades": trades[-30:]  # Return last 30 trades only
        }

        # Cache the backtest result
        stock_info_cache.set(cache_key, result, STOCK_INFO_TTL)
        print(f"💾 Cached backtest for {ticker} ({period}) (1 hour TTL)")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {str(e)}"
        )


# ============================================
# Excluded Tickers Management
# ============================================

@router.post("/discover/exclude/{ticker}")
def exclude_ticker_from_discovery(
    ticker: str,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """Exclude a ticker from discovery recommendations"""
    from app.models.excluded_ticker import ExcludedTicker

    # Check if already excluded
    existing = db.query(ExcludedTicker).filter(ExcludedTicker.ticker == ticker).first()
    if existing:
        return {"status": "already_excluded", "ticker": ticker}

    # Add to excluded list
    excluded = ExcludedTicker(ticker=ticker, reason=reason)
    db.add(excluded)
    db.commit()

    # Clear discovery cache
    global _discovery_cache, _discovery_cache_time
    _discovery_cache.clear()
    _discovery_cache_time.clear()

    return {"status": "excluded", "ticker": ticker}


@router.delete("/discover/exclude/{ticker}")
def unexclude_ticker_from_discovery(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Remove a ticker from exclusion list"""
    from app.models.excluded_ticker import ExcludedTicker

    excluded = db.query(ExcludedTicker).filter(ExcludedTicker.ticker == ticker).first()
    if not excluded:
        return {"status": "not_excluded", "ticker": ticker}

    db.delete(excluded)
    db.commit()

    # Clear discovery cache
    global _discovery_cache, _discovery_cache_time
    _discovery_cache.clear()
    _discovery_cache_time.clear()

    return {"status": "unexcluded", "ticker": ticker}


@router.get("/discover/excluded")
def get_excluded_tickers(db: Session = Depends(get_db)):
    """Get all excluded tickers"""
    from app.models.excluded_ticker import ExcludedTicker

    excluded = db.query(ExcludedTicker).all()
    return {
        "count": len(excluded),
        "tickers": [{"ticker": e.ticker, "reason": e.reason, "excluded_at": e.excluded_at} for e in excluded]
    }


@router.post("/discover/exclude-all")
def exclude_all_current_candidates(
    market: str = "ALL",
    db: Session = Depends(get_db)
):
    """Exclude all current discovery candidates"""
    from app.models.excluded_ticker import ExcludedTicker

    # Get current candidates
    recommendations = get_discovery_candidates(market=market, check_signals=False, db=db)

    excluded_count = 0
    for stock in recommendations.get("recommendations", []):
        ticker = stock["ticker"]
        # Check if already excluded
        existing = db.query(ExcludedTicker).filter(ExcludedTicker.ticker == ticker).first()
        if not existing:
            excluded = ExcludedTicker(ticker=ticker, reason="Bulk exclusion from discovery")
            db.add(excluded)
            excluded_count += 1

    db.commit()

    # Clear discovery cache
    global _discovery_cache, _discovery_cache_time
    _discovery_cache.clear()
    _discovery_cache_time.clear()

    return {
        "status": "success",
        "excluded_count": excluded_count,
        "message": f"{excluded_count} tickers excluded from discovery"
    }


