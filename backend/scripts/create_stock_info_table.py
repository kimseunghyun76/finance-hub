#!/usr/bin/env python3
"""Create stock_info table in the database"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models.sector import StockInfo

def main():
    print("🔧 Creating stock_info table...")

    try:
        # Create the stock_info table
        StockInfo.__table__.create(engine, checkfirst=True)

        print("✅ stock_info table created successfully!")
        print("📊 Table schema:")
        print("  - id (Primary Key)")
        print("  - ticker (Unique, Indexed)")
        print("  - name")
        print("  - asset_type (STOCK/ETF/INDEX/CRYPTO)")
        print("  - sector")
        print("  - industry")
        print("  - country")
        print("  - market_cap")
        print("  - description")
        print("  - is_etf")
        print("  - etf_category")
        print("  - expense_ratio")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
