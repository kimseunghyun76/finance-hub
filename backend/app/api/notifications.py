"""Notification API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.database import get_db
from app.models.notification import Notification, NotificationSetting

router = APIRouter(tags=["notifications"])


class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: int
    user_id: Optional[int]
    ticker: Optional[str]
    type: str
    title: str
    message: str
    severity: str
    is_read: bool
    data: Optional[str]
    created_at: str
    read_at: Optional[str]

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Create notification schema"""
    user_id: Optional[int] = None
    ticker: Optional[str] = None
    type: str
    title: str
    message: str
    severity: str = "info"
    data: Optional[dict] = None


class NotificationSettingResponse(BaseModel):
    """Notification settings response"""
    id: int
    user_id: Optional[int]
    price_alert_enabled: bool
    prediction_update_enabled: bool
    rebalance_alert_enabled: bool
    news_alert_enabled: bool
    portfolio_goal_enabled: bool
    price_change_threshold: float
    rebalance_threshold: float

    class Config:
        from_attributes = True


class NotificationSettingUpdate(BaseModel):
    """Update notification settings"""
    price_alert_enabled: Optional[bool] = None
    prediction_update_enabled: Optional[bool] = None
    rebalance_alert_enabled: Optional[bool] = None
    news_alert_enabled: Optional[bool] = None
    portfolio_goal_enabled: Optional[bool] = None
    price_change_threshold: Optional[float] = None
    rebalance_threshold: Optional[float] = None


@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    user_id: Optional[int] = Query(None),
    is_read: Optional[bool] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get notifications with filters"""
    query = db.query(Notification)

    # Filter by user_id or system-wide
    if user_id is not None:
        query = query.filter(or_(
            Notification.user_id == user_id,
            Notification.user_id.is_(None)
        ))

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    if type:
        query = query.filter(Notification.type == type)

    notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()

    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            ticker=n.ticker,
            type=n.type,
            title=n.title,
            message=n.message,
            severity=n.severity,
            is_read=n.is_read,
            data=n.data,
            created_at=n.created_at.isoformat() if n.created_at else "",
            read_at=n.read_at.isoformat() if n.read_at else None
        )
        for n in notifications
    ]


@router.get("/notifications/unread-count")
def get_unread_count(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    query = db.query(Notification).filter(Notification.is_read == False)

    if user_id is not None:
        query = query.filter(or_(
            Notification.user_id == user_id,
            Notification.user_id.is_(None)
        ))

    count = query.count()

    return {"unread_count": count}


@router.post("/notifications", response_model=NotificationResponse)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    data_json = json.dumps(notification.data, ensure_ascii=False) if notification.data else None

    new_notification = Notification(
        user_id=notification.user_id,
        ticker=notification.ticker,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        severity=notification.severity,
        data=data_json,
        is_read=False
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return NotificationResponse(
        id=new_notification.id,
        user_id=new_notification.user_id,
        ticker=new_notification.ticker,
        type=new_notification.type,
        title=new_notification.title,
        message=new_notification.message,
        severity=new_notification.severity,
        is_read=new_notification.is_read,
        data=new_notification.data,
        created_at=new_notification.created_at.isoformat() if new_notification.created_at else "",
        read_at=None
    )


@router.patch("/notifications/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    notification.read_at = datetime.now()
    db.commit()

    return {"success": True, "message": "Notification marked as read"}


@router.patch("/notifications/mark-all-read")
def mark_all_as_read(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    query = db.query(Notification).filter(Notification.is_read == False)

    if user_id is not None:
        query = query.filter(or_(
            Notification.user_id == user_id,
            Notification.user_id.is_(None)
        ))

    count = query.update({
        "is_read": True,
        "read_at": datetime.now()
    })
    db.commit()

    return {"success": True, "message": f"Marked {count} notifications as read"}


@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()

    return {"success": True, "message": "Notification deleted"}


# Notification Settings endpoints
@router.get("/notifications/settings", response_model=NotificationSettingResponse)
def get_notification_settings(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get notification settings for user"""
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.user_id == user_id
    ).first()

    if not settings:
        # Create default settings
        settings = NotificationSetting(
            user_id=user_id,
            price_alert_enabled=True,
            prediction_update_enabled=True,
            rebalance_alert_enabled=True,
            news_alert_enabled=False,
            portfolio_goal_enabled=True,
            price_change_threshold=5.0,
            rebalance_threshold=5.0
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return NotificationSettingResponse(
        id=settings.id,
        user_id=settings.user_id,
        price_alert_enabled=settings.price_alert_enabled,
        prediction_update_enabled=settings.prediction_update_enabled,
        rebalance_alert_enabled=settings.rebalance_alert_enabled,
        news_alert_enabled=settings.news_alert_enabled,
        portfolio_goal_enabled=settings.portfolio_goal_enabled,
        price_change_threshold=settings.price_change_threshold,
        rebalance_threshold=settings.rebalance_threshold
    )


@router.patch("/notifications/settings", response_model=NotificationSettingResponse)
def update_notification_settings(
    update: NotificationSettingUpdate,
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Update notification settings"""
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.user_id == user_id
    ).first()

    if not settings:
        settings = NotificationSetting(user_id=user_id)
        db.add(settings)

    # Update only provided fields
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)

    return NotificationSettingResponse(
        id=settings.id,
        user_id=settings.user_id,
        price_alert_enabled=settings.price_alert_enabled,
        prediction_update_enabled=settings.prediction_update_enabled,
        rebalance_alert_enabled=settings.rebalance_alert_enabled,
        news_alert_enabled=settings.news_alert_enabled,
        portfolio_goal_enabled=settings.portfolio_goal_enabled,
        price_change_threshold=settings.price_change_threshold,
        rebalance_threshold=settings.rebalance_threshold
    )
