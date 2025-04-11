"""
Update the user_test_attempt table to include the complete_test_progress_id column.
"""
import os
from app import app, db
from sqlalchemy import text

def update_test_attempt_table():
    """Add complete_test_progress_id column to the user_test_attempt table."""
    try:
        with app.app_context():
            conn = db.engine.connect()
            
            # Check if the column already exists
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user_test_attempt' AND column_name='complete_test_progress_id'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add the column
                alter_table_query = text(
                    "ALTER TABLE user_test_attempt ADD COLUMN complete_test_progress_id INTEGER"
                )
                conn.execute(alter_table_query)
                
                # Add foreign key constraint
                add_fk_query = text(
                    "ALTER TABLE user_test_attempt ADD CONSTRAINT fk_user_test_attempt_progress "
                    "FOREIGN KEY (complete_test_progress_id) REFERENCES complete_test_progress (id)"
                )
                conn.execute(add_fk_query)
                
                conn.commit()
                print("Updated user_test_attempt table successfully.")
            else:
                print("Column complete_test_progress_id already exists in user_test_attempt table.")
            
            conn.close()
    except Exception as e:
        print(f"Error updating user_test_attempt table: {str(e)}")

if __name__ == "__main__":
    update_test_attempt_table()