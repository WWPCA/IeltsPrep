"""
Set up assessment products for the IELTS preparation app.
This script sets up all components of the assessment products system.
"""

import os
import sys
from main import app
from flask import Flask

def setup_assessment_products():
    """Set up the assessment products system."""
    print("Setting up assessment products...")
    
    with app.app_context():
        # 1. Make sure the database model is updated
        print("\n1. Checking database model...")
        try:
            # Check if test_number column is nullable
            from models import db, CompletePracticeTest
            with db.engine.connect() as conn:
                result = conn.execute("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name = 'complete_practice_test' AND column_name = 'test_number'")
                row = result.fetchone()
                
                if row and row[1] == 'NO':
                    print("Making test_number column nullable...")
                    conn.execute("ALTER TABLE complete_practice_test ALTER COLUMN test_number DROP NOT NULL")
                    print("test_number column is now nullable.")
                else:
                    print("test_number column is already nullable.")
            
            # Check if product_type column exists
            result = db.engine.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'complete_practice_test' AND column_name = 'product_type'")
            
            if not result.fetchone():
                print("Adding product_type, status, and _tests columns...")
                db.engine.execute("ALTER TABLE complete_practice_test ADD COLUMN product_type VARCHAR(50) NULL")
                db.engine.execute("ALTER TABLE complete_practice_test ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'")
                db.engine.execute("ALTER TABLE complete_practice_test ADD COLUMN _tests TEXT NULL")
                print("Columns added successfully.")
            else:
                print("product_type column already exists.")
        except Exception as e:
            print(f"Error updating database model: {str(e)}")
            print("Proceeding to next step...")
        
        # 2. Create assessment sets
        print("\n2. Creating assessment sets...")
        try:
            # Check if sets already exist
            from models import CompletePracticeTest
            existing_sets = CompletePracticeTest.query.filter(CompletePracticeTest.product_type.isnot(None)).count()
            
            if existing_sets > 0:
                print(f"Assessment sets already exist ({existing_sets} sets). Skipping.")
            else:
                print("Running create_assessment_sets.py...")
                os.system("python create_assessment_sets.py")
                
                # If some sets are missing, create them separately
                from models import CompletePracticeTest
                general_speaking_sets = CompletePracticeTest.query.filter_by(product_type='general_speaking').count()
                
                if general_speaking_sets < 4:
                    print("Creating missing general speaking sets...")
                    os.system("python create_general_speaking_sets.py")
        except Exception as e:
            print(f"Error creating assessment sets: {str(e)}")
            print("Proceeding to next step...")
    
    # 3. Verify template exists
    print("\n3. Verifying assessment products template...")
    template_path = os.path.join('templates', 'assessment_products.html')
    if os.path.exists(template_path):
        print(f"Template exists at {template_path}.")
    else:
        print(f"Template does not exist at {template_path}.")
        print("Please create the template file manually.")
    
    # 4. Add assessment routes
    print("\n4. Setting up assessment routes...")
    try:
        # Import the routes module
        import add_assessment_routes
        
        # Run the function to add the routes
        add_assessment_routes.add_assessment_routes()
        print("Assessment routes added.")
    except Exception as e:
        print(f"Error adding assessment routes: {str(e)}")
        print("Proceeding to next step...")
    
    # 5. Update routes.py
    print("\n5. Updating routes.py...")
    try:
        import update_routes
        update_routes.update_routes()
        print("Routes updated.")
    except Exception as e:
        print(f"Error updating routes: {str(e)}")
        print("Proceeding to next step...")
    
    print("\nAssessment products setup complete!")
    print("\nTo test the implementation:")
    print("1. Visit /assessment-products to see the products page")
    print("2. Click on a product to go to checkout")
    print("3. Complete the payment flow to test the integration")

if __name__ == "__main__":
    setup_assessment_products()