"""LSTM Stock Price Predictor"""
import numpy as np
import pandas as pd
try:
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    # Dummy classes to prevent ImportErrors in type hints or usage
    class keras:
        Model = object
    class layers:
        LSTM = object
        Dropout = object
        Dense = object
from sklearn.preprocessing import MinMaxScaler
from typing import Optional, Tuple
import logging
import pickle
import os

logger = logging.getLogger(__name__)


class StockPredictor:
    """LSTM-based stock price predictor"""

    def __init__(
        self,
        lookback_days: int = 60,
        forecast_days: int = 5,
        model_path: Optional[str] = None
    ):
        """
        Initialize predictor

        Args:
            lookback_days: Number of past days to use for prediction
            forecast_days: Number of future days to predict
            model_path: Path to load pre-trained model
        """
        self.lookback_days = lookback_days
        self.forecast_days = forecast_days
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None

        if model_path:
            self.load_model(model_path)

    def prepare_data(
        self,
        df: pd.DataFrame,
        train_split: float = 0.8
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for training/prediction

        Args:
            df: DataFrame with 'close' column
            train_split: Proportion of data for training

        Returns:
            X_train, y_train, X_test, y_test
        """
        # Extract close prices
        data = df['close'].values.reshape(-1, 1)

        # Scale data
        scaled_data = self.scaler.fit_transform(data)

        # Create sequences
        X, y = [], []
        for i in range(self.lookback_days, len(scaled_data) - self.forecast_days + 1):
            X.append(scaled_data[i - self.lookback_days:i, 0])
            y.append(scaled_data[i + self.forecast_days - 1, 0])

        X, y = np.array(X), np.array(y)

        # Reshape for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        # Split train/test
        split_idx = int(len(X) * train_split)
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        X_test = X[split_idx:]
        y_test = y[split_idx:]

        return X_train, y_train, X_test, y_test

    def build_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """
        Build LSTM model

        Args:
            input_shape: (time_steps, features)

        Returns:
            Compiled Keras model
        """
        model = keras.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.2),
            layers.LSTM(50, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(25),
            layers.Dense(1)
        ])

        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )

        return model

    def train(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.1
    ) -> dict:
        """
        Train the model

        Args:
            df: DataFrame with stock data
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Validation split ratio

        Returns:
            Training history
        """
        logger.info(f"Preparing data for training...")
        X_train, y_train, X_test, y_test = self.prepare_data(df)

        logger.info(f"Building model...")
        self.model = self.build_model((X_train.shape[1], 1))

        logger.info(f"Training model for {epochs} epochs...")
        history = self.model.fit(
            X_train,
            y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_split=validation_split,
            verbose=1
        )

        # Evaluate on test set
        test_loss, test_mae = self.model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"Test Loss: {test_loss:.4f}, Test MAE: {test_mae:.4f}")

        return {
            "train_loss": float(history.history['loss'][-1]),
            "val_loss": float(history.history['val_loss'][-1]),
            "test_loss": float(test_loss),
            "test_mae": float(test_mae),
        }

    def predict(self, recent_data: pd.DataFrame) -> dict:
        """
        Make prediction

        Args:
            recent_data: Recent stock data (at least lookback_days)

        Returns:
            Prediction results with confidence
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        if len(recent_data) < self.lookback_days:
            raise ValueError(f"Need at least {self.lookback_days} days of data")

        # Prepare input
        data = recent_data['close'].values[-self.lookback_days:].reshape(-1, 1)
        scaled_data = self.scaler.transform(data)
        X = np.reshape(scaled_data, (1, self.lookback_days, 1))

        # Predict
        prediction_scaled = self.model.predict(X, verbose=0)
        prediction = self.scaler.inverse_transform(prediction_scaled)[0][0]

        # Calculate confidence (inverse of prediction variance)
        # Simple heuristic: use model's training accuracy
        current_price = float(recent_data['close'].iloc[-1])
        price_change = prediction - current_price
        price_change_pct = (price_change / current_price) * 100

        # Confidence: closer to 0% change = higher confidence
        confidence = max(0.5, 1.0 - abs(price_change_pct) / 10)

        return {
            "predicted_price": float(prediction),
            "current_price": current_price,
            "change": float(price_change),
            "change_percent": float(price_change_pct),
            "confidence": float(confidence),
            "forecast_days": self.forecast_days,
        }

    def save_model(self, path: str):
        """Save model and scaler to disk"""
        if self.model is None:
            raise ValueError("No model to save")

        # Save model
        self.model.save(path)

        # Save scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        logger.info(f"Model saved to {path}")
        logger.info(f"Scaler saved to {scaler_path}")

    def load_model(self, path: str):
        """Load model and scaler from disk"""
        # Load model
        self.model = keras.models.load_model(path)

        # Load scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"Scaler loaded from {scaler_path}")
        else:
            logger.warning(f"Scaler file not found at {scaler_path}, using default scaler")

        logger.info(f"Model loaded from {path}")
