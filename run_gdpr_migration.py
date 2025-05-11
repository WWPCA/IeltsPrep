"""
Run GDPR Compliance Database Migration

This script runs the necessary database migrations to support
GDPR compliance features and updates the User model.
"""

import os
import sys
import logging
from app import app, db
from add_gdpr_fields import add_gdpr_fields, update_user_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the GDPR database migration"""
    logger.info("Running GDPR database migration...")
    
    try:
        # Add GDPR fields to database schema
        add_gdpr_fields()
        
        # Update User model
        update_user_model()
        
        # Create GDPR logs directory
        os.makedirs('gdpr_logs', exist_ok=True)
        
        logger.info("GDPR database migration completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during GDPR database migration: {str(e)}")
        return False

def print_migration_steps():
    """Print the migration steps for manual verification"""
    print("=== GDPR Compliance Migration Steps ===")
    print("1. Adding 'consent_settings' column (TEXT)")
    print("2. Adding 'cookie_preferences' column (TEXT)")
    print("3. Adding 'data_processing_consents' column (TEXT)")
    print("4. Adding 'last_consent_update' column (TIMESTAMP)")
    print("5. Adding 'marketing_preferences' column (TEXT)")
    print("6. Adding 'data_retention_policy' column (TEXT)")
    print("7. Creating GDPR logs directory structure")
    print("\nAfter migration, the User model will have the following new fields:")
    print("- consent_settings: JSON string of consent settings")
    print("- cookie_preferences: JSON string of cookie preferences")
    print("- data_processing_consents: JSON string of data processing consents")
    print("- last_consent_update: Last time consent was updated")
    print("- marketing_preferences: JSON string of marketing preferences")
    print("- data_retention_policy: JSON string of data retention policy")
    print("\nThese changes enable:")
    print("- Comprehensive consent management")
    print("- GDPR-compliant data access and portability")
    print("- Right to be forgotten implementation")
    print("- Enhanced privacy controls for users")

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