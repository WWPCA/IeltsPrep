"""
Initialize Database Schema
This script updates the database schema to include our new models.
It creates tables if they don't exist and runs our test repository initialization.
"""
import sys
from app import db, app

def init_db():
    """Create all tables in the database."""
    with app.app_context():
        print("Creating database tables...")
        
        # Import models to ensure they're registered with SQLAlchemy
        import models
        
        # Create tables
        db.create_all()
        
        print("Database tables successfully created.")
        
        # Initialize test repository
        try:
            from init_test_repository import init_test_repository
            init_test_repository()
        except Exception as e:
            print(f"Error initializing test repository: {str(e)}")

if __name__ == "__main__":
    init_db()