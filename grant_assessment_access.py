"""
Grant assessment access to a user for testing.
This script assigns all four IELTS assessment products to a user account.
"""

from app import app, db
from models import User
from datetime import datetime, timedelta
import sys

def grant_all_assessment_access(username_or_email=None):
    """
    Grant access to all IELTS assessment products to a user.
    
    Args:
        username_or_email (str): Username or email of the user to grant access to
    """
    with app.app_context():
        # Find the target user
        user = None
        if username_or_email:
            # Try to find by username
            user = User.query.filter_by(username=username_or_email).first()
            
            # If not found, try by email
            if not user:
                user = User.query.filter_by(email=username_or_email).first()
        else:
            # If no username/email is provided, use the first user in the database
            user = User.query.first()
            
        if not user:
            print("User not found. Please provide a valid username or email.")
            return
        
        print(f"Granting assessment access to user: {user.username} (ID: {user.id})")
        
        # Set the assessment package status to use a standard format that fits in the field
        user.assessment_package_status = "All Products"
        
        # Set expiry date to 365 days from now for extended testing
        user.assessment_package_expiry = datetime.utcnow() + timedelta(days=365)
        
        # Create assessment history entries for each product type
        assessment_types = [
            'academic_writing',
            'academic_speaking',
            'general_writing',
            'general_speaking'
        ]
        
        # Initialize assessment history if needed
        if not hasattr(user, 'assessment_history') or not user.assessment_history:
            user.assessment_history = []
        
        # Add entries for each product type
        now = datetime.utcnow()
        for product_id in assessment_types:
            purchase = {
                'date': now,
                'product_id': product_id,
                'assigned': True,
                'assigned_assessment_ids': [],  # Will be populated in the next step
            }
            user.assessment_history.append(purchase)
        
        # Commit changes to database
        db.session.commit()
        print(f"User {user.username} now has access to all assessment products.")
        
        # Assign actual assessment sets
        try:
            import assessment_assignment_service
            
            for product_id in assessment_types:
                # Determine base assessment type (academic or general)
                base_assessment_type = 'academic' if product_id.startswith('academic_') else 'general'
                
                # Assign 4 assessments (standard package size)
                assigned_ids, success = assessment_assignment_service.assign_assessments_to_user(
                    user_id=user.id,
                    assessment_type=base_assessment_type,
                    num_assessments=4,
                    access_days=365
                )
                
                if success:
                    print(f"Successfully assigned {len(assigned_ids)} {product_id} assessments to user {user.id}")
                    
                    # Update the assessment history with the assigned IDs
                    for i, item in enumerate(user.assessment_history):
                        if item.get('product_id') == product_id:
                            user.assessment_history[i]['assigned_assessment_ids'] = assigned_ids
                            break
                else:
                    print(f"Failed to assign {product_id} assessments: not enough unique assessments available")
            
            # Commit the final changes with assigned assessment IDs
            db.session.commit()
            
        except Exception as e:
            print(f"Error assigning assessments to user: {str(e)}")
            
        print("All assessment access granted successfully!")
        return user

if __name__ == "__main__":
    username_or_email = sys.argv[1] if len(sys.argv) > 1 else None
    grant_all_assessment_access(username_or_email)