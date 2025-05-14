"""
Update the PracticeTest model to include a _content field for storing the passage text.
"""
from app import app, db
from sqlalchemy import Column, Text

def add_content_field():
    """Add a _content field to the PracticeTest table."""
    with app.app_context():
        # Check if the column already exists
        try:
            # Try to execute a query that would fail if the column doesn't exist
            db.session.execute("SELECT _content FROM practice_test LIMIT 1")
            print("_content column already exists")
        except Exception:
            # The column doesn't exist, so add it
            db.session.execute('ALTER TABLE practice_test ADD COLUMN _content TEXT')
            db.session.commit()
            print("Added _content column to practice_test table")

if __name__ == "__main__":
    add_content_field()