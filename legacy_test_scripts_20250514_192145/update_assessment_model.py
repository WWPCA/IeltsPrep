"""
Update the CompletePracticeTest model with new columns for assessment products.
This script adds the product_type, status, and _tests columns to the table.
"""

from main import app
from models import db
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, Text

def update_assessment_model():
    """Add new columns to CompletePracticeTest table."""
    with app.app_context():
        # Check if columns already exist
        inspector = sa.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('complete_practice_test')]
        
        print(f"Current columns: {columns}")
        
        if 'product_type' not in columns:
            print("Adding product_type column")
            add_column('complete_practice_test', Column('product_type', String(50), nullable=True))
        
        if 'status' not in columns:
            print("Adding status column")
            add_column('complete_practice_test', Column('status', String(20), nullable=False, server_default='active'))
        
        if '_tests' not in columns:
            print("Adding _tests column")
            add_column('complete_practice_test', Column('_tests', Text, nullable=True))
        
        print("Database schema updated successfully.")

def add_column(table_name, column):
    """Add a column to a table."""
    engine = db.engine
    column_name = column.name
    column_type = column.type.compile(engine.dialect)
    
    if column.nullable:
        nullable = "NULL"
    else:
        nullable = "NOT NULL"
    
    # Add default value if specified
    default = ""
    if column.server_default:
        default = f" DEFAULT '{column.server_default.arg}'"
    
    # Execute the ALTER TABLE statement
    query = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable}{default};'
    print(f"Executing: {query}")
    with engine.connect() as conn:
        conn.execute(sa.text(query))

if __name__ == "__main__":
    update_assessment_model()