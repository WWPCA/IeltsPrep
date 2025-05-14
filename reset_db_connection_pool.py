"""
Reset the database connection pool and fix transaction issues.
This script closes all existing connection pools, disposes connections,
and reinitializes the database engine to fix stuck transactions.
"""

import logging
import sqlalchemy
from app import app, db

def reset_db_connection_pool():
    """Reset the database connection pool to fix transaction issues."""
    
    with app.app_context():
        logging.info("Starting database connection pool reset...")
        
        try:
            # Close current session
            db.session.remove()
            
            # Dispose all connections in the pool
            db.engine.dispose()
            
            # Create a new database engine with fresh pool settings
            db.engine = sqlalchemy.create_engine(
                app.config["SQLALCHEMY_DATABASE_URI"],
                pool_recycle=10,       # Shorter recycle time 
                pool_pre_ping=True,    # Ensure connections work before use
            )
            
            # Test connection with explicit transaction management
            with db.engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
                
            # Create a fresh database session
            db.session = db.create_scoped_session()
            
            logging.info("Database connection pool has been successfully reset")
            print("Database connection pool has been successfully reset")
            
        except Exception as e:
            logging.error(f"Error resetting database connection pool: {e}")
            print(f"Error: {e}")

if __name__ == "__main__":
    reset_db_connection_pool()