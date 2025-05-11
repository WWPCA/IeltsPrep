"""
Apply Country Restrictions to Application

This script applies country-based access restrictions to the application,
allowing access only from approved countries.
"""

import sys
import logging
from app import app
from country_access_control import apply_country_restrictions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_restrictions():
    """Apply country restrictions to the application."""
    try:
        logger.info("Applying country-based access restrictions...")
        
        with app.app_context():
            # Apply restrictions to all relevant routes
            apply_country_restrictions(app)
        
        logger.info("Country restrictions successfully applied")
        return True
    
    except Exception as e:
        logger.error(f"Error applying country restrictions: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== Country Restriction System =====")
    print("This will restrict access to only the following countries:")
    print("- Canada (CA)")
    print("- United States (US)")
    print("- India (IN)")
    print("- Nepal (NP)")
    print("- Kuwait (KW)")
    print("- Qatar (QA)")
    print()
    print("EU countries and the UK will be explicitly blocked for regulatory compliance reasons.")
    print("This restriction will apply to all routes except essential system paths.")
    
    # Ask for confirmation
    confirm = input("\nDo you want to apply these restrictions? (y/n): ")
    
    if confirm.lower() == 'y':
        success = apply_restrictions()
        
        if success:
            print("\nCountry restrictions successfully applied!")
            print("GeoIP detection is now active for all visitors.")
            sys.exit(0)
        else:
            print("\nFailed to apply country restrictions. See log for details.")
            sys.exit(1)
    else:
        print("Operation cancelled.")
        sys.exit(0)