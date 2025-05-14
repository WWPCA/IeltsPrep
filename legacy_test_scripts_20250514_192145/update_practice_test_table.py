"""
Update the practice_test table to include the complete_test_id column.
"""
import os
from app import app, db
from sqlalchemy import text

def update_practice_test_table():
    """Add complete_test_id column to the practice_test table."""
    try:
        with app.app_context():
            conn = db.engine.connect()
            
            # Check if the column already exists
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='practice_test' AND column_name='complete_test_id'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add the column
                alter_table_query = text(
                    "ALTER TABLE practice_test ADD COLUMN complete_test_id INTEGER"
                )
                conn.execute(alter_table_query)
                
                # Add foreign key constraint
                add_fk_query = text(
                    "ALTER TABLE practice_test ADD CONSTRAINT fk_practice_test_complete_test "
                    "FOREIGN KEY (complete_test_id) REFERENCES complete_practice_test (id)"
                )
                conn.execute(add_fk_query)
                
                # Add 'ielts_test_type' column
                alter_table_query = text(
                    "ALTER TABLE practice_test ADD COLUMN ielts_test_type VARCHAR(20) DEFAULT 'academic'"
                )
                conn.execute(alter_table_query)
                
                # Add 'is_free' column
                alter_table_query = text(
                    "ALTER TABLE practice_test ADD COLUMN is_free BOOLEAN DEFAULT FALSE"
                )
                conn.execute(alter_table_query)
                
                # Add 'time_limit' column
                alter_table_query = text(
                    "ALTER TABLE practice_test ADD COLUMN time_limit INTEGER"
                )
                conn.execute(alter_table_query)
                
                conn.commit()
                print("Updated practice_test table successfully.")
            else:
                print("Column complete_test_id already exists in practice_test table.")
            
            conn.close()
    except Exception as e:
        print(f"Error updating practice_test table: {str(e)}")

if __name__ == "__main__":
    update_practice_test_table()