"""
Create a comprehensive test account with full access to all assessment products.
This script creates an admin test account with all assessment packages enabled.
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append('.')

from app import app, db
from models import User, AssignedAssessmentSet

def create_test_admin_account():
    """Create a test admin account with full access to all assessment products."""
    
    with app.app_context():
        # Check if test account already exists
        existing_user = User.query.filter_by(email='test@ielts-genai.com').first()
        if existing_user:
            print("Test account already exists. Updating permissions...")
            user = existing_user
        else:
            # Create new test admin account
            user = User(
                username='test_admin',
                email='test@ielts-genai.com',
                password_hash=generate_password_hash('TestPassword123!'),
                account_activated=True,
                email_verified=True,
                is_admin=True,
                current_streak=0,
                longest_streak=0,
                assessment_package_status='unlimited_access',
                assessment_package_expiry=datetime.utcnow() + timedelta(days=365),  # 1 year access
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            print("Test admin account created successfully!")
        
        # Assign all assessment packages
        assessment_products = [
            'academic_writing_assessment',
            'academic_speaking_assessment', 
            'general_writing_assessment',
            'general_speaking_assessment'
        ]
        
        for product_id in assessment_products:
            # Check if assignment already exists
            existing_assignment = AssignedAssessmentSet.query.filter_by(
                user_id=user.id,
                assessment_type=product_id.replace('_assessment', '').replace('academic_', '').replace('general_', ''),
                test_category='Academic' if 'academic' in product_id else 'General Training'
            ).first()
            
            if not existing_assignment:
                # Create new assignment
                assignment = AssignedAssessmentSet(
                    user_id=user.id,
                    assessment_type='writing' if 'writing' in product_id else 'speaking',
                    test_category='Academic' if 'academic' in product_id else 'General Training',
                    assigned_count=4,  # 4 assessments per package
                    used_count=0,
                    expiry_date=datetime.utcnow() + timedelta(days=365),
                    created_at=datetime.utcnow()
                )
                db.session.add(assignment)
                print(f"Assigned {product_id} package to test account")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 TEST ACCOUNT CREATED SUCCESSFULLY! 🎉")
        print("="*60)
        print(f"Email: test@ielts-genai.com")
        print(f"Password: TestPassword123!")
        print(f"Username: test_admin")
        print(f"Admin Access: Yes")
        print(f"Assessment Packages: All 4 products (Academic + General Writing & Speaking)")
        print(f"Package Expiry: {(datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%d')}")
        print("="*60)
        print("✅ Ready to test TrueScore® writing assessments")
        print("✅ Ready to test ClearScore pronunciation scoring")
        print("✅ Full access to all assessment types")
        print("="*60)

if __name__ == "__main__":
    create_test_admin_account()