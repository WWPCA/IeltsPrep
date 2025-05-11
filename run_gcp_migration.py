"""
Run GCP Storage Database Migration

This script runs the necessary database migrations to support
GCP storage integration, primarily by adding storage reference columns
to the UserTestAttempt model.
"""

import os
import sys
import logging
from app import app, db
from add_gcp_storage_columns import add_gcp_storage_columns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the GCP storage database migration"""
    logger.info("Running GCP storage database migration...")
    
    try:
        # Add GCP storage columns
        add_gcp_storage_columns()
        
        logger.info("Database migration completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during database migration: {str(e)}")
        return False

def print_migration_steps():
    """Print the migration steps for manual verification"""
    print("=== GCP Storage Migration Steps ===")
    print("1. Adding 'gcp_transcript_path' column (VARCHAR 255)")
    print("2. Adding 'gcp_assessment_path' column (VARCHAR 255)")
    print("3. Adding 'transcript_expiry_date' column (TIMESTAMP)")
    print("\nAfter migration, the UserTestAttempt model will have the following new fields:")
    print("- gcp_transcript_path: Path to transcript in GCP")
    print("- gcp_assessment_path: Path to assessment in GCP")
    print("- transcript_expiry_date: When transcript expires (6 months)")
    print("\nThese changes enable:")
    print("- Scalable cloud storage for 1M+ users")
    print("- Proper transcript lifecycle management (6-month retention)")
    print("- GDPR compliance with right-to-be-forgotten support")
    print("- Reliable fallback to local storage when GCP is unavailable")

if __name__ == "__main__":
    # Print migration information
    print_migration_steps()
    
    # Ask for confirmation
    confirm = input("\nDo you want to run this migration? (y/n): ")
    
    if confirm.lower() == 'y':
        success = run_migration()
        
        if success:
            print("\nMigration completed successfully")
            sys.exit(0)
        else:
            print("\nMigration failed. See log for details.")
            sys.exit(1)
    else:
        print("Migration cancelled.")
        sys.exit(0)