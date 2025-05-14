"""
Reset the database connection to fix InFailedSqlTransaction errors.
This script explicitly rolls back any failed transactions and closes connections.
"""
from app import db

def fix_db_transactions():
    """Roll back any failed transactions and ensure connections are closed."""
    try:
        # Roll back any active transactions
        db.session.rollback()
        print("Successfully rolled back any in-progress transactions.")
        
        # Close all connections in the connection pool
        db.engine.dispose()
        print("Successfully closed all database connections.")
        
        # Create a test connection to verify it's working
        with db.engine.connect() as connection:
            # Execute a simple query to verify connection is working
            result = connection.execute("SELECT 1")
            if result.scalar() == 1:
                print("Database connection is now working correctly.")
            else:
                print("WARNING: Database connection test returned unexpected result.")
        
        return True
    except Exception as e:
        print(f"Error fixing database connections: {e}")
        return False

if __name__ == "__main__":
    fix_db_transactions()