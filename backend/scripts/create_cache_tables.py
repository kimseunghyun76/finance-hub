"""Create stock price cache and metadata tables"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine
from app.models.stock_price_cache import StockPriceCache, StockMetadata

def create_cache_tables():
    """캐시 테이블 생성"""
    try:
        # Create tables
        StockPriceCache.__table__.create(engine, checkfirst=True)
        StockMetadata.__table__.create(engine, checkfirst=True)

        print("✅ Cache tables created successfully!")
        print("  - stock_price_cache: for daily stock prices")
        print("  - stock_metadata: for static stock information")

        return True

    except Exception as e:
        print(f"❌ Error creating cache tables: {e}")
        return False

if __name__ == "__main__":
    create_cache_tables()
