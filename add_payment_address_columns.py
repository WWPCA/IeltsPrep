"""
Add address columns to PaymentRecord table
This script adds columns to store customer address information for tax compliance.
"""
from app import app, db
from models import PaymentRecord
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_payment_address_columns():
    """Add address columns to PaymentRecord table."""
    # Check if columns already exist
    columns = [c.name for c in PaymentRecord.__table__.columns]
    
    # Define columns to add if they don't exist
    address_columns = [
        ('address_line1', 'line1'),
        ('address_line2', 'line2'),
        ('address_city', 'city'),
        ('address_state', 'state'),
        ('address_postal_code', 'postal_code'),
        ('address_country', 'country')
    ]
    
    column_count = 0
    for column_name, _ in address_columns:
        if column_name not in columns:
            column_count += 1
    
    if column_count == 0:
        logger.info("Address columns already exist in PaymentRecord table.")
        return
    
    # Add columns if they don't exist
    with app.app_context():
        # Execute raw SQL to add columns
        for column_name, _ in address_columns:
            if column_name not in columns:
                try:
                    db.engine.execute(f"ALTER TABLE payment_record ADD COLUMN {column_name} VARCHAR(255)")
                    logger.info(f"Added column {column_name} to PaymentRecord table.")
                except Exception as e:
                    logger.error(f"Error adding column {column_name}: {str(e)}")
    
    logger.info(f"Added {column_count} address columns to PaymentRecord table.")

if __name__ == '__main__':
    add_payment_address_columns()