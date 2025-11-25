"""Create test notifications for demonstration"""
from app.database import SessionLocal
from app.services.notification_service import NotificationService

def create_test_notifications():
    """Create sample notifications for testing"""
    db = SessionLocal()

    try:
        # Test 1: Price alert notification
        NotificationService.create_notification(
            db=db,
            user_id=None,
            ticker="AAPL",
            notification_type="price_alert",
            title="AAPL 가격 급등",
            message="AAPL의 가격이 7.5% 급등했습니다. 현재가: $185.92",
            severity="warning",
            data={
                "current_price": 185.92,
                "previous_price": 172.48,
                "change_percent": 7.79
            }
        )

        # Test 2: Prediction update
        NotificationService.create_notification(
            db=db,
            user_id=None,
            ticker="TSLA",
            notification_type="prediction_update",
            title="TSLA 예측 업데이트",
            message="TSLA의 예측가가 업데이트되었습니다. 상승 예상: 5.3%",
            severity="info",
            data={
                "predicted_price": 265.40,
                "current_price": 252.00,
                "change_percent": 5.3,
                "confidence": 0.85
            }
        )

        # Test 3: Success notification
        NotificationService.create_notification(
            db=db,
            user_id=None,
            ticker=None,
            notification_type="portfolio_goal",
            title="포트폴리오 목표 달성",
            message="축하합니다! 월간 수익률 목표 10%를 달성했습니다.",
            severity="success",
            data={
                "goal_type": "monthly_return",
                "target": 10.0,
                "achieved": 12.5
            }
        )

        # Test 4: Error notification
        NotificationService.create_notification(
            db=db,
            user_id=None,
            ticker="005930.KS",
            notification_type="price_alert",
            title="005930.KS 가격 급락",
            message="삼성전자의 가격이 8.2% 급락했습니다. 현재가: ₩68,900",
            severity="error",
            data={
                "current_price": 68900,
                "previous_price": 75100,
                "change_percent": -8.25
            }
        )

        print("✅ Successfully created 4 test notifications")

    except Exception as e:
        print(f"❌ Error creating test notifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_notifications()
