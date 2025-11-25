"""Fix sector data in database to match Enum"""
import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal

def fix_sector_data():
    """Fix sector strings in database"""
    db = SessionLocal()
    try:
        print("🔧 Fixing sector data...")
        
        # Check current values
        result = db.execute(text("SELECT DISTINCT sector FROM stock_info"))
        sectors = [row[0] for row in result]
        print(f"Found sectors: {sectors}")
        
        # Updates
        updates = {
            'Financial Services': 'FINANCE',
            'Financials': 'FINANCE',
            'Technology': 'TECHNOLOGY',
            'Healthcare': 'HEALTHCARE',
            'Consumer Cyclical': 'CONSUMER',
            'Consumer Defensive': 'CONSUMER',
            'Energy': 'ENERGY',
            'Industrials': 'INDUSTRIAL',
            'Basic Materials': 'MATERIALS',
            'Utilities': 'UTILITIES',
            'Real Estate': 'REAL_ESTATE',
            'Communication Services': 'COMMUNICATION',
            'Materials': 'MATERIALS',
            'Communication': 'COMMUNICATION',
            'Consumer': 'CONSUMER'
        }
        
        for old, new in updates.items():
            # Update using raw SQL to bypass Enum check
            query = text(f"UPDATE stock_info SET sector = '{new}' WHERE sector = '{old}'")
            result = db.execute(query)
            if result.rowcount > 0:
                print(f"  ✅ Updated {result.rowcount} rows: {old} -> {new}")
                
        db.commit()
        print("✨ Sector data fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_sector_data()
