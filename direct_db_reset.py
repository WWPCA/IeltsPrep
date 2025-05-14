"""
Direct reset of database connections and transaction issues.
This script uses direct SQL commands to terminate all connections and reset the database
directly at the PostgreSQL level, which should help fix persistent transaction issues.
"""

import os
import psycopg2
import logging
import time
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database credentials from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection_params():
    """Extract connection parameters from DATABASE_URL."""
    try:
        # Parse the DATABASE_URL into components
        if DATABASE_URL.startswith("postgresql://"):
            # Remove the protocol part
            conn_str = DATABASE_URL[len("postgresql://"):]
            
            # Split user:password@host:port/dbname
            user_pass, host_port_db = conn_str.split("@", 1)
            
            # Handle user and password
            if ":" in user_pass:
                user, password = user_pass.split(":", 1)
            else:
                user = user_pass
                password = ""
            
            # Handle host, port, and dbname
            if "/" in host_port_db:
                host_port, dbname = host_port_db.split("/", 1)
            else:
                host_port = host_port_db
                dbname = ""
            
            # Handle host and port
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                port = int(port)
            else:
                host = host_port
                port = 5432  # Default PostgreSQL port
            
            # Return connection parameters
            return {
                "user": user,
                "password": password,
                "host": host,
                "port": port,
                "dbname": dbname
            }
        else:
            # Cannot parse the URL
            raise ValueError(f"Invalid DATABASE_URL format: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Error parsing DATABASE_URL: {e}")
        raise

@contextmanager
def get_pg_connection():
    """Get a raw PostgreSQL connection."""
    conn = None
    try:
        # Get connection parameters
        params = get_db_connection_params()
        
        # Create a direct PostgreSQL connection
        conn = psycopg2.connect(**params)
        conn.autocommit = True  # Important for administrative commands
        yield conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def reset_database_connections():
    """Reset all database connections and abort any stuck transactions."""
    try:
        # Get a direct connection to the database
        with get_pg_connection() as conn:
            # Create a cursor for executing SQL commands
            with conn.cursor() as cur:
                # Get PostgreSQL version for info
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"Connected to {version}")
                
                # Terminate all connections except our own
                logger.info("Terminating all active connections...")
                cur.execute("""
                    SELECT pg_terminate_backend(pid) 
                    FROM pg_stat_activity 
                    WHERE pid <> pg_backend_pid() 
                    AND datname = current_database()
                """)
                
                # Give PostgreSQL a moment to process termination requests
                time.sleep(1)
                
                # Check if we're successful
                cur.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE pid <> pg_backend_pid() 
                    AND datname = current_database()
                """)
                count = cur.fetchone()[0]
                
                if count == 0:
                    logger.info("All connections terminated successfully")
                else:
                    logger.warning(f"Some connections ({count}) could not be terminated")
                    
        logger.info("Database connections have been reset")
        print("Database connections have been reset successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error resetting database connections: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    reset_database_connections()