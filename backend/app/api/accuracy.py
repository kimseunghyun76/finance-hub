"""Prediction accuracy dashboard API endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.database import get_db
from app.models.prediction_validation import PredictionValidation, ModelAccuracy
from app.models.prediction import Prediction
from datetime import datetime, date, timedelta
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


# Response models
class AccuracyMetrics(BaseModel):
    """Overall accuracy metrics"""
    total_predictions: int
    correct_direction: int
    direction_accuracy: float
    avg_price_error_percent: float
    overall_score: float


class TickerAccuracy(BaseModel):
    """Accuracy metrics per ticker"""
    ticker: str
    total_predictions: int
    direction_accuracy: float
    avg_price_error_percent: float
    overall_score: float
    last_updated: datetime


class TimeSeriesAccuracy(BaseModel):
    """Accuracy over time"""
    date: date
    predictions_count: int
    direction_accuracy: float
    avg_error_percent: float


class AccuracyDashboardResponse(BaseModel):
    """Complete dashboard data"""
    overall_metrics: AccuracyMetrics
    by_ticker: List[TickerAccuracy]
    time_series: List[TimeSeriesAccuracy]
    top_performers: List[TickerAccuracy]
    worst_performers: List[TickerAccuracy]


@router.get("/metrics", response_model=AccuracyMetrics)
def get_overall_accuracy(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get overall prediction accuracy metrics"""

    cutoff_date = date.today() - timedelta(days=days)

    # Get all validations in the period
    validations = (
        db.query(PredictionValidation)
        .filter(PredictionValidation.validation_date >= cutoff_date)
        .all()
    )

    if not validations:
        return AccuracyMetrics(
            total_predictions=0,
            correct_direction=0,
            direction_accuracy=0.0,
            avg_price_error_percent=0.0,
            overall_score=0.0
        )

    total = len(validations)
    correct = sum(1 for v in validations if v.direction_correct)
    direction_acc = correct / total if total > 0 else 0.0

    avg_error = sum(abs(v.price_error_percent) for v in validations) / total
    price_acc = max(0, 1 - (avg_error / 100))  # Convert error to accuracy

    # Overall score: 60% direction accuracy + 40% price accuracy
    overall = (direction_acc * 0.6) + (price_acc * 0.4)

    return AccuracyMetrics(
        total_predictions=total,
        correct_direction=correct,
        direction_accuracy=direction_acc,
        avg_price_error_percent=avg_error,
        overall_score=overall
    )


@router.get("/by-ticker", response_model=List[TickerAccuracy])
def get_accuracy_by_ticker(
    days: int = Query(30, ge=1, le=365),
    min_predictions: int = Query(5, ge=1, description="Minimum predictions required"),
    db: Session = Depends(get_db)
):
    """Get accuracy metrics grouped by ticker"""

    cutoff_date = date.today() - timedelta(days=days)

    # Query with joins to get ticker information
    results = (
        db.query(
            Prediction.ticker,
            func.count(PredictionValidation.id).label('total'),
            func.sum(func.cast(PredictionValidation.direction_correct, Integer)).label('correct'),
            func.avg(func.abs(PredictionValidation.price_error_percent)).label('avg_error')
        )
        .join(PredictionValidation, Prediction.id == PredictionValidation.prediction_id)
        .filter(PredictionValidation.validation_date >= cutoff_date)
        .group_by(Prediction.ticker)
        .having(func.count(PredictionValidation.id) >= min_predictions)
        .all()
    )

    ticker_accuracies = []
    for ticker, total, correct, avg_error in results:
        direction_acc = (correct or 0) / total if total > 0 else 0.0
        price_acc = max(0, 1 - ((avg_error or 0) / 100))
        overall = (direction_acc * 0.6) + (price_acc * 0.4)

        ticker_accuracies.append(TickerAccuracy(
            ticker=ticker,
            total_predictions=total,
            direction_accuracy=direction_acc,
            avg_price_error_percent=avg_error or 0.0,
            overall_score=overall,
            last_updated=datetime.now()
        ))

    return sorted(ticker_accuracies, key=lambda x: x.overall_score, reverse=True)


@router.get("/time-series", response_model=List[TimeSeriesAccuracy])
def get_accuracy_time_series(
    days: int = Query(30, ge=7, le=365),
    ticker: Optional[str] = Query(None, description="Filter by specific ticker"),
    db: Session = Depends(get_db)
):
    """Get accuracy metrics over time"""

    cutoff_date = date.today() - timedelta(days=days)

    query = (
        db.query(
            PredictionValidation.validation_date,
            func.count(PredictionValidation.id).label('count'),
            func.avg(func.cast(PredictionValidation.direction_correct, Float)).label('direction_acc'),
            func.avg(func.abs(PredictionValidation.price_error_percent)).label('avg_error')
        )
        .join(Prediction, PredictionValidation.prediction_id == Prediction.id)
        .filter(PredictionValidation.validation_date >= cutoff_date)
    )

    if ticker:
        query = query.filter(Prediction.ticker == ticker)

    results = query.group_by(PredictionValidation.validation_date).order_by(PredictionValidation.validation_date).all()

    return [
        TimeSeriesAccuracy(
            date=val_date,
            predictions_count=count,
            direction_accuracy=direction_acc or 0.0,
            avg_error_percent=avg_error or 0.0
        )
        for val_date, count, direction_acc, avg_error in results
    ]


@router.get("/dashboard", response_model=AccuracyDashboardResponse)
def get_accuracy_dashboard(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get complete accuracy dashboard data"""

    overall = get_overall_accuracy(days=days, db=db)
    by_ticker = get_accuracy_by_ticker(days=days, db=db)
    time_series = get_accuracy_time_series(days=days, db=db)

    # Top 5 performers
    top = sorted(by_ticker, key=lambda x: x.overall_score, reverse=True)[:5]

    # Bottom 5 performers (but still have enough predictions)
    worst = sorted(by_ticker, key=lambda x: x.overall_score)[:5]

    return AccuracyDashboardResponse(
        overall_metrics=overall,
        by_ticker=by_ticker,
        time_series=time_series,
        top_performers=top,
        worst_performers=worst
    )


@router.get("/ticker/{ticker}", response_model=TickerAccuracy)
def get_ticker_accuracy(
    ticker: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get accuracy metrics for a specific ticker"""

    cutoff_date = date.today() - timedelta(days=days)

    result = (
        db.query(
            func.count(PredictionValidation.id).label('total'),
            func.sum(func.cast(PredictionValidation.direction_correct, Integer)).label('correct'),
            func.avg(func.abs(PredictionValidation.price_error_percent)).label('avg_error')
        )
        .join(Prediction, PredictionValidation.prediction_id == Prediction.id)
        .filter(
            and_(
                Prediction.ticker == ticker,
                PredictionValidation.validation_date >= cutoff_date
            )
        )
        .first()
    )

    if not result or not result.total:
        return TickerAccuracy(
            ticker=ticker,
            total_predictions=0,
            direction_accuracy=0.0,
            avg_price_error_percent=0.0,
            overall_score=0.0,
            last_updated=datetime.now()
        )

    total, correct, avg_error = result
    direction_acc = (correct or 0) / total if total > 0 else 0.0
    price_acc = max(0, 1 - ((avg_error or 0) / 100))
    overall = (direction_acc * 0.6) + (price_acc * 0.4)

    return TickerAccuracy(
        ticker=ticker,
        total_predictions=total,
        direction_accuracy=direction_acc,
        avg_price_error_percent=avg_error or 0.0,
        overall_score=overall,
        last_updated=datetime.now()
    )


@router.post("/validate-predictions")
def validate_recent_predictions(db: Session = Depends(get_db)):
    """Validate predictions against actual prices (for scheduler)"""
    from app.services.prediction_validator import PredictionValidator

    validator = PredictionValidator(db)
    results = validator.validate_predictions()

    return {
        "success": True,
        "validated": results.get("validated", 0),
        "errors": results.get("errors", 0),
        "message": f"Validated {results.get('validated', 0)} predictions"
    }
