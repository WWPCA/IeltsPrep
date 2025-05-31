"""
Comprehensive System Diagnostic Check
This script performs a complete analysis of the database, routes, and payment flow
to identify any mismatches or issues.
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from app import app, db
from models import User, UserPackage, Assessment
import stripe

def check_database_consistency():
    """Check database consistency for assessment types and products."""
    print("="*60)
    print("DATABASE CONSISTENCY CHECK")
    print("="*60)
    
    with app.app_context():
        # Check assessment types in database
        assessment_types = db.session.execute(
            db.text("SELECT DISTINCT assessment_type FROM assessment ORDER BY assessment_type")
        ).fetchall()
        
        print("Assessment types in database:")
        db_types = []
        for row in assessment_types:
            assessment_type = row[0]
            db_types.append(assessment_type)
            print(f"  - {assessment_type}")
        
        # Check UserPackage table structure
        print("\nUserPackage table structure:")
        try:
            sample_packages = UserPackage.query.limit(5).all()
            if sample_packages:
                for pkg in sample_packages:
                    print(f"  - User {pkg.user_id}: {pkg.package_name} ({pkg.status}, {pkg.quantity_remaining}/{pkg.quantity_purchased})")
            else:
                print("  - No packages found")
        except Exception as e:
            print(f"  - Error accessing UserPackage table: {str(e)}")
        
        return db_types

def check_route_configuration():
    """Check route configuration and product definitions."""
    print("\n" + "="*60)
    print("ROUTE CONFIGURATION CHECK")
    print("="*60)
    
    # Import assessment products from routes
    try:
        from add_assessment_routes import assessment_products, assessment_type_mapping
        
        print("Assessment products defined in routes:")
        route_products = []
        for product_id, product_info in assessment_products.items():
            route_products.append(product_info['name'])
            print(f"  - {product_id}: {product_info['name']} (${product_info['price']})")
        
        print("\nAssessment type mapping:")
        for product_id, assessment_type in assessment_type_mapping.items():
            print(f"  - {product_id} → {assessment_type}")
        
        return route_products, assessment_type_mapping
    except Exception as e:
        print(f"Error loading route configuration: {str(e)}")
        return [], {}

def check_stripe_configuration():
    """Check Stripe configuration and products."""
    print("\n" + "="*60)
    print("STRIPE CONFIGURATION CHECK")
    print("="*60)
    
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    if not stripe_key:
        print("❌ STRIPE_SECRET_KEY not found in environment")
        return False
    
    stripe.api_key = stripe_key
    print("✅ Stripe API key configured")
    
    # Test creating a checkout session
    try:
        YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        
        test_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Test Product',
                        'description': 'Test checkout session'
                    },
                    'unit_amount': 2500,
                    'tax_behavior': 'exclusive',
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://' + YOUR_DOMAIN + '/payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://' + YOUR_DOMAIN + '/assessment-products',
            automatic_tax={'enabled': False},
            customer_creation='always',
            billing_address_collection='required',
            metadata={'product_id': 'test_product'}
        )
        print("✅ Stripe checkout session creation successful")
        return True
    except Exception as e:
        print(f"❌ Stripe checkout session creation failed: {str(e)}")
        return False

def check_payment_flow():
    """Test the complete payment flow logic."""
    print("\n" + "="*60)
    print("PAYMENT FLOW CHECK")
    print("="*60)
    
    with app.app_context():
        # Test user creation and package assignment
        try:
            from add_assessment_routes import handle_assessment_product_payment, assessment_products
            
            # Find or create a test user
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User()
                test_user.username = 'testuser'
                test_user.email = 'test@example.com'
                test_user.password_hash = 'test_hash'
                test_user.email_verified = True
                test_user.account_activated = True
                db.session.add(test_user)
                db.session.commit()
                print(f"✅ Created test user with ID: {test_user.id}")
            else:
                print(f"✅ Using existing test user with ID: {test_user.id}")
            
            # Test each product
            for product_id in assessment_products.keys():
                print(f"\nTesting payment flow for {product_id}:")
                
                # Clear existing packages for this test
                existing_packages = UserPackage.query.filter_by(
                    user_id=test_user.id,
                    package_name=assessment_products[product_id]['name']
                ).all()
                for pkg in existing_packages:
                    db.session.delete(pkg)
                db.session.commit()
                
                # Test payment processing
                result = handle_assessment_product_payment(test_user, product_id)
                if result:
                    print(f"  ✅ Payment processing successful")
                    
                    # Check if UserPackage was created
                    package = UserPackage.query.filter_by(
                        user_id=test_user.id,
                        package_name=assessment_products[product_id]['name']
                    ).first()
                    
                    if package:
                        print(f"  ✅ UserPackage created: {package.package_name} ({package.status})")
                        print(f"     Quantity: {package.quantity_remaining}/{package.quantity_purchased}")
                    else:
                        print(f"  ❌ UserPackage not found after payment")
                    
                    # Test package access
                    has_access = test_user.has_package_access(assessment_products[product_id]['name'])
                    if has_access:
                        print(f"  ✅ User has access to package")
                    else:
                        print(f"  ❌ User does not have access to package")
                else:
                    print(f"  ❌ Payment processing failed")
            
            return True
            
        except Exception as e:
            print(f"❌ Payment flow test failed: {str(e)}")
            return False

def check_route_endpoints():
    """Check if all required route endpoints are accessible."""
    print("\n" + "="*60)
    print("ROUTE ENDPOINTS CHECK")
    print("="*60)
    
    with app.test_client() as client:
        endpoints_to_check = [
            '/assessment-products',
            '/product-checkout?product=academic_writing',
            '/payment-success'
        ]
        
        for endpoint in endpoints_to_check:
            try:
                response = client.get(endpoint, follow_redirects=False)
                if response.status_code in [200, 302]:  # 302 for redirects
                    print(f"✅ {endpoint} - Status: {response.status_code}")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {str(e)}")

def check_consistency_between_systems():
    """Check consistency between database, routes, and payment systems."""
    print("\n" + "="*60)
    print("CROSS-SYSTEM CONSISTENCY CHECK")
    print("="*60)
    
    # Get data from different systems
    db_types = check_database_consistency()
    route_products, type_mapping = check_route_configuration()
    
    # Check if route products match assessment types in database
    print("\nProduct name consistency:")
    for product_name in route_products:
        if product_name in db_types:
            print(f"  ✅ {product_name} - matches database")
        else:
            print(f"  ❌ {product_name} - NOT found in database")
    
    # Check if database types have corresponding products
    print("\nDatabase type coverage:")
    for db_type in db_types:
        if db_type in route_products:
            print(f"  ✅ {db_type} - has corresponding product")
        else:
            print(f"  ❌ {db_type} - NO corresponding product")
    
    # Check assessment type mapping consistency
    print("\nAssessment type mapping consistency:")
    for product_id, mapped_type in type_mapping.items():
        if mapped_type in db_types:
            print(f"  ✅ {product_id} → {mapped_type} - valid mapping")
        else:
            print(f"  ❌ {product_id} → {mapped_type} - INVALID mapping")

def main():
    """Run all diagnostic checks."""
    print("IELTS GenAI Prep - Comprehensive System Diagnostic")
    print("=" * 80)
    print(f"Diagnostic run at: {datetime.now()}")
    print("=" * 80)
    
    # Run all checks
    stripe_ok = check_stripe_configuration()
    check_route_endpoints()
    payment_ok = check_payment_flow()
    check_consistency_between_systems()
    
    # Final summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if stripe_ok:
        print("✅ Stripe configuration is working")
    else:
        print("❌ Stripe configuration has issues")
    
    if payment_ok:
        print("✅ Payment flow is working")
    else:
        print("❌ Payment flow has issues")
    
    print("\n🔍 Diagnostic complete. Review any ❌ items above for issues that need fixing.")

if __name__ == "__main__":
    main()