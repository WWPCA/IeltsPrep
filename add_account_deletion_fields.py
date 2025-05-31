"""
Add Account Deletion Fields to User Model
This script adds the necessary fields for the enhanced account deletion system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from sqlalchemy import text

def add_account_deletion_fields():
    """Add account deletion fields to User table."""
    with app.app_context():
        try:
            # Check if fields already exist
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('user')]
            
            fields_to_add = [
                ('deletion_requested', 'BOOLEAN DEFAULT FALSE NOT NULL'),
                ('deletion_requested_at', 'TIMESTAMP NULL'),
                ('deletion_scheduled_for', 'TIMESTAMP NULL'),
                ('reactivation_token', 'VARCHAR(255) NULL')
            ]
            
            for field_name, field_definition in fields_to_add:
                if field_name not in columns:
                    try:
                        db.session.execute(text(f'ALTER TABLE "user" ADD COLUMN {field_name} {field_definition}'))
                        print(f"✓ Added {field_name} column")
                    except Exception as e:
                        print(f"✗ Failed to add {field_name}: {str(e)}")
                else:
                    print(f"✓ {field_name} column already exists")
            
            db.session.commit()
            print("\n✓ Account deletion fields migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Migration failed: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    add_account_deletion_fields()