"""
Fix database transaction issues.
This script resolves any pending transactions that might be in a failed state.
"""

from app import app, db
import logging

def fix_database_transaction():
    """Fix database transaction issues."""
    
    with app.app_context():
        logging.info("Attempting to fix database transaction issues...")
        
        # Close and refresh the session to resolve any transaction issues
        db.session.remove()
        
        # Create a new engine-level connection to execute raw SQL
        connection = db.engine.raw_connection()
        try:
            cursor = connection.cursor()
            # Execute ROLLBACK as a safeguard
            cursor.execute("ROLLBACK")
            connection.commit()
            logging.info("Transaction rollback complete")
            
            # Check the database connection by running a simple query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                logging.info("Database connection test successful")
            else:
                logging.error("Database connection test failed")
                
            cursor.close()
        except Exception as e:
            logging.error(f"Error fixing transaction: {e}")
        finally:
            connection.close()
            
        print("Database transaction fix attempt complete")

if __name__ == "__main__":
    fix_database_transaction()