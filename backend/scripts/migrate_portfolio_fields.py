"""Add new fields to portfolio table"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import sqlite3

def migrate_portfolio_table():
    """포트폴리오 테이블에 새로운 필드 추가"""
    db_path = "/Users/dennis/finance-hub/backend/finance_hub.db"

    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(portfolios)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {columns}")

        # Add new columns if they don't exist
        new_columns = [
            ("initial_value", "REAL DEFAULT 0.0 NOT NULL"),
            ("target_return", "REAL"),
            ("risk_tolerance", "VARCHAR"),
        ]

        for col_name, col_def in new_columns:
            if col_name not in columns:
                sql = f"ALTER TABLE portfolios ADD COLUMN {col_name} {col_def}"
                print(f"Adding column: {col_name}")
                cursor.execute(sql)
                print(f"✅ Added {col_name}")
            else:
                print(f"⏭️  Column {col_name} already exists")

        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_portfolio_table()
