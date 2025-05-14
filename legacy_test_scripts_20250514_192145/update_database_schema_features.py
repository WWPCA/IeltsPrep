"""
Update database schema to add _features column to PracticeTest table.
This is needed for General Training Reading Matching Features tests.
"""
from app import app, db
from sqlalchemy import text

def update_database_schema():
    """Add the _features column to the PracticeTest table."""
    with app.app_context():
        # Check if the column already exists
        try:
            # Try to add the column
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE practice_test ADD COLUMN _features TEXT'))
                conn.commit()
            print("Added _features column to practice_test table")
        except Exception as e:
            if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
                print("Column _features already exists in practice_test table")
            else:
                print(f"Error adding column: {str(e)}")
                
        print("Database schema update completed")

if __name__ == "__main__":
    update_database_schema()