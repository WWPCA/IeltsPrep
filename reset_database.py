"""
Reset database connections and transactions.
This script completely resets the database connection pool and aborted transactions.
"""

from app import app, db
import logging

def reset_database_connections():
    """Reset all database connections and transactions."""
    
    with app.app_context():
        logging.info("Resetting database connections...")
        
        # Close all sessions and connection pools
        db.session.close()
        db.engine.dispose()
        
        # Create a fresh session
        db.create_all()
        
        logging.info("Database connections reset successfully")
        print("Database connections have been reset")

if __name__ == "__main__":
    reset_database_connections()