"""
Test Payment Flow and Package Assignment
This script tests the complete payment flow to ensure products are correctly assigned.
"""

import os
from app import app, db
from models import User, UserPackage
from add_assessment_routes import assessment_products, handle_assessment_product_payment, assign_assessment_sets
from datetime import datetime, timedelta

def test_payment_flow():
    """Test the complete payment flow for all 4 products"""
    
    print("TESTING COMPLETE PAYMENT FLOW")
    print("=" * 50)
    
    with app.app_context():
        # Get or create test user
        test_user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        if not test_user:
            print("Test user not found. Creating one...")
            test_user = User()
            test_user.email = 'test@ieltsaiprep.com'
            test_user.set_password('testpassword123')
            test_user.account_activated = True
            test_user.email_verified = True
            db.session.add(test_user)
            db.session.commit()
            print(f"Created test user with ID: {test_user.id}")
        else:
            print(f"Using existing test user with ID: {test_user.id}")
        
        # Clear existing packages for clean test
        print(f"\nClearing existing packages for user {test_user.id}...")
        UserPackage.query.filter_by(user_id=test_user.id).delete()
        db.session.commit()
        
        # Test each product
        print(f"\nTesting payment flow for all 4 products:")
        
        for product_id, product_info in assessment_products.items():
            print(f"\n--- Testing {product_id} ---")
            print(f"Product Name: {product_info['name']}")
            print(f"Description: {product_info['description']}")
            print(f"Price: ${product_info['price']}")
            
            # Simulate payment success
            try:
                success = handle_assessment_product_payment(test_user, product_id)
                
                if success:
                    print(f"✓ Payment processed successfully")
                    
                    # Check if UserPackage was created
                    user_package = UserPackage.query.filter_by(
                        user_id=test_user.id,
                        package_name=product_info['name']
                    ).first()
                    
                    if user_package:
                        print(f"✓ UserPackage created: {user_package.package_name}")
                        print(f"  Status: {user_package.status}")
                        print(f"  Quantity: {user_package.quantity_remaining}/{user_package.quantity_purchased}")
                        
                        # Test package access
                        has_access = test_user.has_package_access(product_info['name'])
                        if has_access:
                            print(f"✓ User has access to {product_info['name']}")
                        else:
                            print(f"❌ User does NOT have access to {product_info['name']}")
                    else:
                        print(f"❌ No UserPackage found for {product_info['name']}")
                else:
                    print(f"❌ Payment processing failed")
                    
            except Exception as e:
                print(f"❌ Error processing payment: {str(e)}")
        
        # Verify final state
        print(f"\nFINAL VERIFICATION")
        print("-" * 30)
        
        user_packages = UserPackage.query.filter_by(user_id=test_user.id).all()
        print(f"Total packages for user: {len(user_packages)}")
        
        for package in user_packages:
            print(f"  - {package.package_name}: {package.status} ({package.quantity_remaining}/{package.quantity_purchased})")
        
        # Test package access for all 4 products
        print(f"\nPackage Access Test:")
        for product_id, product_info in assessment_products.items():
            has_access = test_user.has_package_access(product_info['name'])
            status = "✓" if has_access else "❌"
            print(f"  {status} {product_info['name']}: {has_access}")

def verify_database_consistency():
    """Verify that product names match database package names"""
    
    print(f"\nDATABASE CONSISTENCY CHECK")
    print("-" * 40)
    
    with app.app_context():
        # Check assessment types in database
        from sqlalchemy import text
        
        db_assessment_types = db.session.execute(
            text("SELECT DISTINCT assessment_type FROM assessment ORDER BY assessment_type")
        ).fetchall()
        
        print("Assessment types in database:")
        for row in db_assessment_types:
            print(f"  - {row[0]}")
        
        print(f"\nProduct names in checkout:")
        for product_id, product_info in assessment_products.items():
            print(f"  - {product_info['name']}")
        
        # Check if they match
        db_types = [row[0] for row in db_assessment_types]
        product_names = [product_info['name'] for product_info in assessment_products.values()]
        
        print(f"\nConsistency Check:")
        all_match = True
        for product_name in product_names:
            if product_name in db_types:
                print(f"  ✓ {product_name} matches database")
            else:
                print(f"  ❌ {product_name} NOT found in database")
                all_match = False
        
        if all_match:
            print(f"\n✓ ALL PRODUCT NAMES MATCH DATABASE ASSESSMENT TYPES")
        else:
            print(f"\n❌ PRODUCT NAME MISMATCHES FOUND")

if __name__ == '__main__':
    verify_database_consistency()
    test_payment_flow()