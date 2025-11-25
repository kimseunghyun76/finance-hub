"""Create portfolio snapshot table"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine
from app.models.portfolio_snapshot import PortfolioSnapshot

def create_snapshot_table():
    """스냅샷 테이블 생성"""
    try:
        # Create table
        PortfolioSnapshot.__table__.create(engine, checkfirst=True)

        print("✅ Portfolio snapshot table created successfully!")
        print("  - portfolio_snapshots: for daily portfolio performance tracking")

        return True

    except Exception as e:
        print(f"❌ Error creating snapshot table: {e}")
        return False

if __name__ == "__main__":
    create_snapshot_table()
