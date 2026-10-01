"""
Reset Nexus Mind database to a clean production slate.
Deletes all rows from all tables in correct dependency order.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base
# Import models so all tables are registered on Base.metadata
from app import models

def reset_database():
    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        print("Successfully wiped all data! Database is now a 100% clean production slate.")
    except Exception as e:
        db.rollback()
        print(f"Error resetting database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
