"""
Simple database reconnection script.
This script uses the environment variables directly to reconnect to the database.
"""

import os
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reconnect_database():
    """Reconnect to the database using environment variables."""
    try:
        # Get database credentials from environment variables
        dbname = os.environ.get("PGDATABASE")
        user = os.environ.get("PGUSER")
        password = os.environ.get("PGPASSWORD")
        host = os.environ.get("PGHOST")
        port = os.environ.get("PGPORT")
        
        logger.info(f"Connecting to database {dbname} on {host}:{port} as {user}")
        
        # Create a direct PostgreSQL connection
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # Set autocommit mode to run administrative commands
        conn.autocommit = True
        
        # Create cursor for executing SQL
        cursor = conn.cursor()
        
        # Check connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.info(f"Connected to {version}")
        
        # Terminate all other connections to the database
        logger.info("Terminating all other connections...")
        cursor.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE pid <> pg_backend_pid() 
            AND datname = %s
        """, (dbname,))
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        logger.info("Database connections have been reset")
        print("Database connections have been reset successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error reconnecting to database: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    reconnect_database()