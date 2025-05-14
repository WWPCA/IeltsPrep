"""
Script to add account_activated column to the User table.

This script adds the missing account_activated column to the User table.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables.")
    exit(1)

# Connect to the database
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Successfully connected to the database.")
except SQLAlchemyError as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

# Add account_activated column if it doesn't exist
try:
    # Check if column already exists
    check_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='account_activated'")
    result = connection.execute(check_query)
    column_exists = result.fetchone() is not None
    
    if column_exists:
        print("The 'account_activated' column already exists. No changes needed.")
    else:
        # Add the column
        add_column_query = text("ALTER TABLE \"user\" ADD COLUMN account_activated BOOLEAN DEFAULT TRUE")
        connection.execute(add_column_query)
        connection.commit()
        print("Successfully added 'account_activated' column to the User table.")
    
except SQLAlchemyError as e:
    connection.rollback()
    print(f"Error modifying the database: {e}")
finally:
    connection.close()
    engine.dispose()