"""
Update User model to handle both subscription and assessment columns.
This script modifies the User model to work with both column naming conventions
during the transition period.
"""

from app import app, db
from models import User
from sqlalchemy.ext.hybrid import hybrid_property
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_user_model():
    """Update User model to handle both subscription and assessment columns."""
    
    # Add hybrid properties to handle both column names
    @hybrid_property
    def assessment_package_status(self):
        """Get assessment_package_status, falling back to subscription_status if needed."""
        # First try to get the new column name
        try:
            # See if the attribute exists on this instance
            return object.__getattribute__(self, '_assessment_package_status')
        except AttributeError:
            try:
                # Fall back to the old column name
                return object.__getattribute__(self, 'subscription_status')
            except AttributeError:
                return 'inactive'
    
    @assessment_package_status.setter
    def assessment_package_status(self, value):
        """Set both assessment_package_status and subscription_status."""
        try:
            # Try to set the new column
            object.__setattr__(self, '_assessment_package_status', value)
        except AttributeError:
            pass
            
        try:
            # Try to set the old column for backward compatibility
            object.__setattr__(self, 'subscription_status', value)
        except AttributeError:
            pass
    
    @hybrid_property
    def assessment_package_expiry(self):
        """Get assessment_package_expiry, falling back to subscription_expiry if needed."""
        try:
            return object.__getattribute__(self, '_assessment_package_expiry')
        except AttributeError:
            try:
                return object.__getattribute__(self, 'subscription_expiry')
            except AttributeError:
                return None
    
    @assessment_package_expiry.setter
    def assessment_package_expiry(self, value):
        """Set both assessment_package_expiry and subscription_expiry."""
        try:
            object.__setattr__(self, '_assessment_package_expiry', value)
        except AttributeError:
            pass
            
        try:
            object.__setattr__(self, 'subscription_expiry', value)
        except AttributeError:
            pass
    
    # Add these methods to the User class
    User.assessment_package_status = assessment_package_status
    User.assessment_package_expiry = assessment_package_expiry
    
    logger.info("User model updated with hybrid properties for subscription/assessment compatibility")
    print("User model updated successfully")

if __name__ == "__main__":
    with app.app_context():
        update_user_model()