"""Create notification tables"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models.notification import Notification, NotificationSetting

if __name__ == "__main__":
    print("Creating notification tables...")

    # Create tables
    Base.metadata.create_all(bind=engine, tables=[
        Notification.__table__,
        NotificationSetting.__table__
    ])

    print("✅ Notification tables created successfully!")
