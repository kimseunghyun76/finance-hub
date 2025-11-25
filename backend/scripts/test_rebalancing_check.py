"""Test portfolio rebalancing check functionality"""
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.services.scheduler import check_portfolio_rebalancing

if __name__ == "__main__":
    print("🧪 Testing portfolio rebalancing check...")
    print("=" * 60)

    try:
        check_portfolio_rebalancing()
        print("\n✅ Rebalancing check test completed successfully")
    except Exception as e:
        print(f"\n❌ Error during rebalancing check: {e}")
        import traceback
        traceback.print_exc()
