"""
Add GDPR Compliance Fields to Database Schema
This script adds the necessary fields to the User model to support GDPR compliance.
"""

import os
from app import app, db
from sqlalchemy import text

def add_gdpr_fields():
    """Add GDPR compliance fields to the User table."""
    try:
        with app.app_context():
            conn = db.engine.connect()
            
            # Check if the consent_settings column already exists
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='consent_settings'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add consent_settings column
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN consent_settings TEXT"
                )
                conn.execute(alter_table_query)
                print("Added consent_settings column to user table.")
            else:
                print("Column consent_settings already exists in user table.")
            
            # Check for cookie_preferences column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='cookie_preferences'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add cookie_preferences column
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN cookie_preferences TEXT"
                )
                conn.execute(alter_table_query)
                print("Added cookie_preferences column to user table.")
            else:
                print("Column cookie_preferences already exists in user table.")
            
            # Check for data_processing_consents column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='data_processing_consents'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add data_processing_consents column
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN data_processing_consents TEXT"
                )
                conn.execute(alter_table_query)
                print("Added data_processing_consents column to user table.")
            else:
                print("Column data_processing_consents already exists in user table.")
            
            # Check for last_consent_update column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='last_consent_update'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add last_consent_update column with timestamp
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN last_consent_update TIMESTAMP WITH TIME ZONE"
                )
                conn.execute(alter_table_query)
                print("Added last_consent_update column to user table.")
            else:
                print("Column last_consent_update already exists in user table.")
            
            # Check for marketing_preferences column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='marketing_preferences'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add marketing_preferences column
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN marketing_preferences TEXT"
                )
                conn.execute(alter_table_query)
                print("Added marketing_preferences column to user table.")
            else:
                print("Column marketing_preferences already exists in user table.")
            
            # Check for data_retention_policy column
            check_column_query = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='data_retention_policy'"
            )
            result = conn.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                # Add data_retention_policy column
                alter_table_query = text(
                    "ALTER TABLE \"user\" ADD COLUMN data_retention_policy TEXT"
                )
                conn.execute(alter_table_query)
                print("Added data_retention_policy column to user table.")
            else:
                print("Column data_retention_policy already exists in user table.")
            
            # Commit all changes
            conn.commit()
            conn.close()
            print("Successfully updated User table with GDPR compliance fields.")
    except Exception as e:
        print(f"Error updating User table: {str(e)}")

def update_user_model():
    """Update the User model with the new fields."""
    try:
        # Load the models.py file
        with open('models.py', 'r') as f:
            content = f.read()
        
        # Create a backup
        with open('models.py.bak', 'w') as f:
            f.write(content)
        
        # Check if fields are already added
        if "consent_settings" in content and "cookie_preferences" in content:
            print("GDPR fields already exist in User model.")
            return
        
        # Find the User class definition
        user_class_start = content.find("class User(UserMixin, db.Model):")
        if user_class_start == -1:
            print("User class not found in models.py")
            return
        
        # Find a good insertion point - after the last User field
        # This is a bit tricky, we'll try to find a pattern that indicates the end of the field definitions
        
        # Let's find the last field definition before methods
        target_pattern = "    # Store password history as JSON string (stores hashed passwords only)\n    _password_history = db.Column(db.Text, default='[]')"
        
        # If pattern not found, try to find the start of the first method
        if target_pattern not in content:
            # Find the first method in the User class
            method_pattern = "    def set_password"
            method_pos = content.find(method_pattern, user_class_start)
            
            if method_pos == -1:
                print("Could not find a suitable insertion point in User class")
                return
            
            # Find the beginning of the line for the method
            insertion_point = content.rfind('\n', user_class_start, method_pos) + 1
        else:
            # Insert after the target pattern
            pattern_pos = content.find(target_pattern)
            insertion_point = content.find('\n', pattern_pos) + 1
        
        # Define new fields
        new_fields = """
    # GDPR Compliance Fields
    consent_settings = db.Column(db.Text, nullable=True)  # JSON string of consent settings
    cookie_preferences = db.Column(db.Text, nullable=True)  # JSON string of cookie preferences
    data_processing_consents = db.Column(db.Text, nullable=True)  # JSON string of data processing consents
    last_consent_update = db.Column(db.DateTime, nullable=True)  # Last time consent was updated
    marketing_preferences = db.Column(db.Text, nullable=True)  # JSON string of marketing preferences
    data_retention_policy = db.Column(db.Text, nullable=True)  # JSON string of data retention policy
    """
        
        # Insert the new fields
        updated_content = content[:insertion_point] + new_fields + content[insertion_point:]
        
        # Write the updated file
        with open('models.py', 'w') as f:
            f.write(updated_content)
        
        print("Successfully updated User model with GDPR compliance fields.")
    except Exception as e:
        print(f"Error updating User model: {str(e)}")

if __name__ == "__main__":
    # Add database fields
    add_gdpr_fields()
    
    # Update User model
    update_user_model()
    
    print("GDPR field updates complete.")