"""Prediction validation service - validates ML predictions against actual prices"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.prediction import Prediction
from app.models.prediction_validation import PredictionValidation, ModelAccuracy
from app.services.data_fetcher import StockDataFetcher


class PredictionValidator:
    """Service to validate predictions against actual stock prices"""

    def __init__(self, db: Session):
        self.db = db

    def validate_predictions_for_date(self, validation_date: date) -> Dict:
        """
        Validate all predictions that targeted this date

        Args:
            validation_date: The date to validate predictions for

        Returns:
            Summary of validation results
        """
        # Find all predictions targeting this date that haven't been validated yet
        predictions = (
            self.db.query(Prediction)
            .filter(
                and_(
                    Prediction.target_date == validation_date,
                    ~Prediction.id.in_(
                        self.db.query(PredictionValidation.prediction_id)
                    )
                )
            )
            .all()
        )

        if not predictions:
            return {
                "validation_date": validation_date.isoformat(),
                "total_predictions": 0,
                "validated": 0,
                "skipped": 0,
                "message": "No predictions found for this date"
            }

        validated_count = 0
        skipped_count = 0

        for prediction in predictions:
            # Get actual price for the target date
            actual_price = self._get_actual_price(prediction.ticker, validation_date)

            if actual_price is None:
                skipped_count += 1
                continue

            # Calculate accuracy metrics
            price_error = abs(prediction.predicted_price - actual_price)
            price_error_percent = (price_error / actual_price) * 100

            # Determine if direction was correct
            # We need the price from prediction_date to know direction
            prev_price = self._get_actual_price(prediction.ticker, prediction.prediction_date)

            if prev_price:
                predicted_direction = "UP" if prediction.predicted_price > prev_price else "DOWN"
                actual_direction = "UP" if actual_price > prev_price else "DOWN"
                direction_correct = predicted_direction == actual_direction
            else:
                direction_correct = False

            # Create validation record
            validation = PredictionValidation(
                prediction_id=prediction.id,
                actual_price=actual_price,
                validation_date=validation_date,
                price_error=price_error,
                price_error_percent=price_error_percent,
                direction_correct=direction_correct
            )

            self.db.add(validation)
            validated_count += 1

        self.db.commit()

        # Update aggregated accuracy metrics
        self._update_model_accuracy(validation_date)

        return {
            "validation_date": validation_date.isoformat(),
            "total_predictions": len(predictions),
            "validated": validated_count,
            "skipped": skipped_count,
            "message": f"Successfully validated {validated_count} predictions"
        }

    def _get_actual_price(self, ticker: str, target_date: date) -> Optional[float]:
        """Get actual closing price for a ticker on a specific date"""
        try:
            # Fetch historical data around the target date
            df = StockDataFetcher.fetch_yahoo_finance(ticker, period="5d")

            if df is None or df.empty:
                return None

            # Find the row for the target date (or closest date)
            df['date'] = df['date'].dt.date
            target_row = df[df['date'] == target_date]

            if not target_row.empty:
                return float(target_row.iloc[0]['close'])

            # If exact date not found, try the next available trading day
            future_rows = df[df['date'] > target_date]
            if not future_rows.empty:
                return float(future_rows.iloc[0]['close'])

            return None

        except Exception as e:
            print(f"Error fetching actual price for {ticker} on {target_date}: {e}")
            return None

    def _update_model_accuracy(self, validation_date: date):
        """Update aggregated accuracy metrics for all models"""
        # Calculate period (last 30 days)
        period_start = validation_date - timedelta(days=30)
        period_end = validation_date

        # Get all unique ticker + model combinations that have validations
        ticker_model_combos = (
            self.db.query(
                Prediction.ticker,
                Prediction.model_type,
                Prediction.model_version
            )
            .join(PredictionValidation)
            .filter(PredictionValidation.validation_date.between(period_start, period_end))
            .distinct()
            .all()
        )

        for ticker, model_type, model_version in ticker_model_combos:
            # Get all validations for this combination in the period
            validations = (
                self.db.query(PredictionValidation)
                .join(Prediction)
                .filter(
                    and_(
                        Prediction.ticker == ticker,
                        Prediction.model_type == model_type,
                        Prediction.model_version == model_version,
                        PredictionValidation.validation_date.between(period_start, period_end)
                    )
                )
                .all()
            )

            if not validations:
                continue

            # Calculate aggregated metrics
            total_predictions = len(validations)
            correct_direction = sum(1 for v in validations if v.direction_correct)
            avg_price_error = sum(v.price_error for v in validations) / total_predictions
            avg_price_error_percent = sum(v.price_error_percent for v in validations) / total_predictions

            # Calculate accuracy scores
            direction_accuracy = correct_direction / total_predictions
            price_accuracy = max(0.0, 1.0 - (avg_price_error_percent / 100))

            # Overall accuracy: weighted combination (60% direction, 40% price)
            overall_accuracy = (direction_accuracy * 0.6) + (price_accuracy * 0.4)

            # Update or create ModelAccuracy record
            accuracy_record = (
                self.db.query(ModelAccuracy)
                .filter(
                    and_(
                        ModelAccuracy.ticker == ticker,
                        ModelAccuracy.model_type == model_type.value,
                        ModelAccuracy.model_version == model_version
                    )
                )
                .first()
            )

            if accuracy_record:
                # Update existing record
                accuracy_record.total_predictions = total_predictions
                accuracy_record.correct_direction = correct_direction
                accuracy_record.avg_price_error = avg_price_error
                accuracy_record.avg_price_error_percent = avg_price_error_percent
                accuracy_record.direction_accuracy = direction_accuracy
                accuracy_record.price_accuracy = price_accuracy
                accuracy_record.overall_accuracy = overall_accuracy
                accuracy_record.period_start = period_start
                accuracy_record.period_end = period_end
            else:
                # Create new record
                accuracy_record = ModelAccuracy(
                    ticker=ticker,
                    model_type=model_type.value,
                    model_version=model_version,
                    total_predictions=total_predictions,
                    correct_direction=correct_direction,
                    avg_price_error=avg_price_error,
                    avg_price_error_percent=avg_price_error_percent,
                    direction_accuracy=direction_accuracy,
                    price_accuracy=price_accuracy,
                    overall_accuracy=overall_accuracy,
                    period_start=period_start,
                    period_end=period_end
                )
                self.db.add(accuracy_record)

        self.db.commit()

    def get_model_accuracy(
        self,
        ticker: Optional[str] = None,
        model_type: Optional[str] = None
    ) -> List[ModelAccuracy]:
        """
        Get accuracy metrics for models

        Args:
            ticker: Filter by ticker (optional)
            model_type: Filter by model type (optional)

        Returns:
            List of ModelAccuracy records
        """
        query = self.db.query(ModelAccuracy)

        if ticker:
            query = query.filter(ModelAccuracy.ticker == ticker)

        if model_type:
            query = query.filter(ModelAccuracy.model_type == model_type)

        return query.order_by(ModelAccuracy.overall_accuracy.desc()).all()

    def get_validation_history(
        self,
        ticker: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get validation history for a ticker

        Args:
            ticker: Stock ticker
            days: Number of days to look back

        Returns:
            List of validation records with prediction info
        """
        cutoff_date = date.today() - timedelta(days=days)

        results = (
            self.db.query(PredictionValidation, Prediction)
            .join(Prediction)
            .filter(
                and_(
                    Prediction.ticker == ticker,
                    PredictionValidation.validation_date >= cutoff_date
                )
            )
            .order_by(PredictionValidation.validation_date.desc())
            .all()
        )

        history = []
        for validation, prediction in results:
            history.append({
                "validation_date": validation.validation_date.isoformat(),
                "predicted_price": prediction.predicted_price,
                "actual_price": validation.actual_price,
                "price_error": validation.price_error,
                "price_error_percent": validation.price_error_percent,
                "direction_correct": validation.direction_correct,
                "model_type": prediction.model_type.value,
                "confidence": prediction.confidence
            })

        return history
