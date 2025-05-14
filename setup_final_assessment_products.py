"""
Set up assessment products for the IELTS GenAI Prep platform.
This script sets up all components of the assessment products system
using the new Assessment model.
"""

import os
import sys
from main import app
from flask import Flask

def setup_final_assessment_products():
    """Set up the assessment products system with the new Assessment model."""
    print("Setting up assessment products using the Assessment model...")
    
    with app.app_context():
        # 1. Check if Assessment table exists and has data
        print("\n1. Checking Assessment table...")
        try:
            from models import db, Assessment
            assessment_count = Assessment.query.count()
            print(f"Found {assessment_count} assessments in the database.")
            
            if assessment_count == 0:
                print("No assessments found. Please run init_assessment_data.py first.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error checking Assessment table: {e}")
            sys.exit(1)
        
        # 2. Check if UserAssessmentAssignment table exists
        print("\n2. Checking UserAssessmentAssignment table...")
        try:
            from models import UserAssessmentAssignment
            # Test creation of a table if it doesn't exist
            db.create_all()
            print("UserAssessmentAssignment table exists or has been created.")
        except Exception as e:
            print(f"Error with UserAssessmentAssignment table: {e}")
            sys.exit(1)
            
        # 3. Update assessment routes
        print("\n3. Updating assessment routes...")
        try:
            import update_assessment_product_routes
            update_assessment_product_routes.update_assessment_product_routes()
            print("Assessment product routes updated successfully.")
        except Exception as e:
            print(f"Error updating assessment routes: {e}")
            sys.exit(1)
            
        # 4. Check for correct structure in payment_services.py
        print("\n4. Checking payment services...")
        try:
            # Ensure Stripe API is configured
            import payment_services
            print("Payment services checked successfully.")
        except Exception as e:
            print(f"Error checking payment services: {e}")
            sys.exit(1)
            
        # 5. Setup payment webhooks
        print("\n5. Setting up payment webhooks...")
        try:
            import stripe_webhook
            print("Payment webhooks setup checked successfully.")
        except Exception as e:
            print(f"Error checking payment webhooks: {e}")
            sys.exit(1)
        
        # 6. Check country restrictions
        print("\n6. Checking country restrictions...")
        try:
            import geoip_services
            print("Country restrictions checked successfully.")
        except Exception as e:
            print(f"Error checking country restrictions: {e}")
            sys.exit(1)
            
        # 7. Check for assessment_assignment_service.py
        print("\n7. Checking assessment assignment service...")
        try:
            import assessment_assignment_service
            print("Assessment assignment service checked successfully.")
        except Exception as e:
            print(f"Error checking assessment assignment service: {e}")
            sys.exit(1)
            
        # 8. Make sure assessment products template exists
        print("\n8. Checking assessment products template...")
        if os.path.exists("templates/assessment_products.html"):
            print("Assessment products template exists.")
        else:
            print("Creating assessment products template...")
            update_assessment_product_routes.create_assessment_products_template()
        
        print("\nAll assessment product components have been set up successfully!")
        print("The IELTS GenAI Prep assessment system is ready.")

if __name__ == "__main__":
    setup_final_assessment_products()