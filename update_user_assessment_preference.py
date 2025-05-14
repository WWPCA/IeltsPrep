"""
Update the user table to include the assessment_preference column.
"""
import os
from app import app, db
from sqlalchemy import text

def update_user_table():
    """Add assessment_preference column to the user table."""
    try:
        with app.app_context():
            conn = db.engine.connect()
            
            # Check if the column already exists
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='assessment_preference'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add the column
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN assessment_preference VARCHAR(20) DEFAULT 'academic'"
                )
                conn.execute(alter_table_query)
                
                conn.commit()
                print("Updated user table successfully with assessment_preference column.")
            else:
                print("Column assessment_preference already exists in user table.")
            
            conn.close()
    except Exception as e:
        print(f"Error updating user table: {str(e)}")

if __name__ == "__main__":
    update_user_table()