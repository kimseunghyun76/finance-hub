"""Create prediction cache table in database"""
import sys
sys.path.append('.')

from app.database import engine, Base
from app.models.prediction_cache import PredictionCache

def create_cache_table():
    """Create the prediction_cache table"""
    print("🔧 Creating prediction_cache table...")

    try:
        # Import all models to ensure they're registered
        from app.models import user, portfolio, holding

        # Create only the prediction_cache table if it doesn't exist
        PredictionCache.__table__.create(bind=engine, checkfirst=True)

        print("✅ prediction_cache table created successfully!")
        print("📊 Table schema:")
        print("  - id (Primary Key)")
        print("  - ticker (Indexed)")
        print("  - predicted_price")
        print("  - current_price")
        print("  - change")
        print("  - change_percent")
        print("  - confidence")
        print("  - action (BUY/SELL/HOLD)")
        print("  - forecast_days")
        print("  - created_at")
        print("  - expires_at")

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise

if __name__ == "__main__":
    create_cache_table()
