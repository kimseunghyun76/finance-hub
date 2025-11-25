"""Create investment insight table"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models.investment_insight import InvestmentInsight

if __name__ == "__main__":
    print("Creating investment insight table...")

    # Create table
    Base.metadata.create_all(bind=engine, tables=[InvestmentInsight.__table__])

    print("✅ Investment insight table created successfully!")
