"""Notification service for generating alerts"""
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationSetting
from app.models.stock_price import StockPrice
from app.models.holding import Holding
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for generating and managing notifications"""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int | None,
        ticker: str | None,
        notification_type: str,
        title: str,
        message: str,
        severity: str = "info",
        data: dict | None = None
    ) -> Notification:
        """Create a new notification"""
        data_json = json.dumps(data, ensure_ascii=False) if data else None

        notification = Notification(
            user_id=user_id,
            ticker=ticker,
            type=notification_type,
            title=title,
            message=message,
            severity=severity,
            data=data_json,
            is_read=False
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        logger.info(f"Created notification: {notification_type} for ticker {ticker}")
        return notification

    @staticmethod
    def check_price_alerts(db: Session):
        """Check for significant price changes and generate alerts"""
        try:
            # Get all holdings with unique tickers
            holdings = db.query(Holding).all()
            unique_tickers = list(set([h.ticker for h in holdings]))

            logger.info(f"Checking price alerts for {len(unique_tickers)} tickers")

            alert_count = 0

            for ticker in unique_tickers:
                # Get last 2 days of prices
                prices = (
                    db.query(StockPrice)
                    .filter(StockPrice.ticker == ticker)
                    .order_by(StockPrice.date.desc())
                    .limit(2)
                    .all()
                )

                if len(prices) < 2:
                    continue

                current_price = prices[0].close
                previous_price = prices[1].close

                change_percent = ((current_price - previous_price) / previous_price) * 100

                # Get notification settings (use default threshold if no user settings)
                settings = db.query(NotificationSetting).first()
                threshold = settings.price_change_threshold if settings else 5.0

                # Check if price change exceeds threshold
                if abs(change_percent) >= threshold:
                    severity = "warning" if abs(change_percent) >= threshold * 1.5 else "info"
                    direction = "급등" if change_percent > 0 else "급락"

                    NotificationService.create_notification(
                        db=db,
                        user_id=None,  # System-wide notification
                        ticker=ticker,
                        notification_type="price_alert",
                        title=f"{ticker} 가격 {direction}",
                        message=f"{ticker}의 가격이 {abs(change_percent):.2f}% {direction}했습니다. 현재가: ${current_price:.2f}",
                        severity=severity,
                        data={
                            "current_price": current_price,
                            "previous_price": previous_price,
                            "change_percent": change_percent,
                            "date": prices[0].date.isoformat()
                        }
                    )
                    alert_count += 1

            logger.info(f"Generated {alert_count} price alert notifications")
            return alert_count

        except Exception as e:
            logger.error(f"Error in check_price_alerts: {e}")
            db.rollback()
            return 0

    @staticmethod
    def create_prediction_update_notification(
        db: Session,
        ticker: str,
        predicted_price: float,
        current_price: float,
        confidence: float
    ):
        """Create notification for prediction updates"""
        try:
            change_percent = ((predicted_price - current_price) / current_price) * 100
            direction = "상승" if change_percent > 0 else "하락"

            NotificationService.create_notification(
                db=db,
                user_id=None,
                ticker=ticker,
                notification_type="prediction_update",
                title=f"{ticker} 예측 업데이트",
                message=f"{ticker}의 예측가가 업데이트되었습니다. {direction} 예상: {abs(change_percent):.2f}%",
                severity="info",
                data={
                    "predicted_price": predicted_price,
                    "current_price": current_price,
                    "change_percent": change_percent,
                    "confidence": confidence
                }
            )
            logger.info(f"Created prediction update notification for {ticker}")

        except Exception as e:
            logger.error(f"Error creating prediction notification: {e}")

    @staticmethod
    def create_rebalance_notification(
        db: Session,
        user_id: int | None,
        portfolio_name: str,
        deviation_percent: float,
        details: dict
    ):
        """Create notification for portfolio rebalancing needs"""
        try:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                ticker=None,
                notification_type="rebalance_needed",
                title=f"{portfolio_name} 리밸런싱 필요",
                message=f"포트폴리오 균형이 {deviation_percent:.1f}% 벗어났습니다. 리밸런싱을 고려해보세요.",
                severity="warning",
                data=details
            )
            logger.info(f"Created rebalance notification for portfolio {portfolio_name}")

        except Exception as e:
            logger.error(f"Error creating rebalance notification: {e}")

    @staticmethod
    def create_portfolio_goal_notification(
        db: Session,
        user_id: int | None,
        portfolio_name: str,
        goal_type: str,
        message: str,
        data: dict | None = None
    ):
        """Create notification for portfolio goal achievements"""
        try:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                ticker=None,
                notification_type="portfolio_goal",
                title=f"{portfolio_name} 목표 {goal_type}",
                message=message,
                severity="success",
                data=data
            )
            logger.info(f"Created portfolio goal notification for {portfolio_name}")

        except Exception as e:
            logger.error(f"Error creating portfolio goal notification: {e}")

    @staticmethod
    def check_user_enabled(db: Session, user_id: int | None, notification_type: str) -> bool:
        """Check if user has enabled this notification type"""
        settings = db.query(NotificationSetting).filter(
            NotificationSetting.user_id == user_id
        ).first()

        if not settings:
            return True  # Default is enabled

        type_mapping = {
            "price_alert": settings.price_alert_enabled,
            "prediction_update": settings.prediction_update_enabled,
            "rebalance_needed": settings.rebalance_alert_enabled,
            "news": settings.news_alert_enabled,
            "portfolio_goal": settings.portfolio_goal_enabled
        }

        return type_mapping.get(notification_type, True)
