"""
Update database schema to include new tables for complete tests.
This script will create the necessary tables if they don't exist.
"""

from app import app, db
from models import CompletePracticeTest, CompleteTestProgress

def update_schema():
    """Update the database schema to include tables for complete tests."""
    
    try:
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            print("Database schema updated successfully.")
    except Exception as e:
        print(f"Error updating database schema: {str(e)}")

if __name__ == "__main__":
    update_schema()