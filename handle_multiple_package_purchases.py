"""
Handle multiple purchases of the same assessment package type.
This demonstrates how the system manages when a user buys 3 of the same type.
"""
from app import app, db
from models import User, UserPackage
from datetime import datetime, timedelta

def purchase_package(user_id, package_name, quantity=1):
    """
    Handle purchasing packages, including multiple of the same type.
    
    Args:
        user_id (int): User ID
        package_name (str): Package name like "Academic Speaking"
        quantity (int): Number of packages to purchase
        
    Returns:
        bool: Success status
    """
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Check if user already has this package type
        existing_package = UserPackage.query.filter_by(
            user_id=user_id,
            package_name=package_name
        ).first()
        
        if existing_package:
            # Add to existing package
            existing_package.add_more_packages(quantity)
            print(f"Added {quantity} more {package_name} packages to existing purchase")
            print(f"User now has {existing_package.quantity_remaining}/{existing_package.quantity_purchased} {package_name} packages")
        else:
            # Create new package entry
            new_package = UserPackage(
                user_id=user_id,
                package_name=package_name,
                quantity_purchased=quantity,
                quantity_remaining=quantity,
                purchase_date=datetime.utcnow(),
                expiry_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(new_package)
            db.session.commit()
            print(f"Created new {package_name} package with {quantity} units")
        
        return True

def use_assessment_package(user_id, package_name):
    """
    Use one unit of an assessment package when taking a test.
    
    Args:
        user_id (int): User ID
        package_name (str): Package name to consume
        
    Returns:
        bool: True if successfully used, False if no packages remaining
    """
    with app.app_context():
        package = UserPackage.query.filter_by(
            user_id=user_id,
            package_name=package_name,
            status='active'
        ).first()
        
        if package and package.quantity_remaining > 0:
            package.use_one_package()
            print(f"Used 1 {package_name} package. Remaining: {package.quantity_remaining}")
            return True
        else:
            print(f"No {package_name} packages remaining for user {user_id}")
            return False

def demo_multiple_purchases():
    """Demonstrate buying 3 of the same package type."""
    
    with app.app_context():
        user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        if not user:
            print("Test user not found")
            return
        
        print("=== Demonstrating Multiple Package Purchases ===")
        
        # Step 1: User buys 3 Academic Speaking packages
        print("\n1. User purchases 3 Academic Speaking packages...")
        purchase_package(user.id, "Academic Speaking", 3)
        
        # Step 2: Show package status
        package = UserPackage.query.filter_by(
            user_id=user.id,
            package_name="Academic Speaking"
        ).first()
        print(f"Package status: {package.quantity_remaining}/{package.quantity_purchased} remaining")
        
        # Step 3: User takes some assessments
        print("\n2. User takes assessments...")
        use_assessment_package(user.id, "Academic Speaking")  # First assessment
        use_assessment_package(user.id, "Academic Speaking")  # Second assessment
        
        # Step 4: User buys 2 more of the same type
        print("\n3. User buys 2 more Academic Speaking packages...")
        purchase_package(user.id, "Academic Speaking", 2)
        
        # Step 5: Continue using assessments
        print("\n4. User continues taking assessments...")
        use_assessment_package(user.id, "Academic Speaking")  # Third assessment
        use_assessment_package(user.id, "Academic Speaking")  # Fourth assessment
        use_assessment_package(user.id, "Academic Speaking")  # Fifth assessment
        
        # Step 6: Final status
        package = UserPackage.query.filter_by(
            user_id=user.id,
            package_name="Academic Speaking"
        ).first()
        print(f"\nFinal status: {package.quantity_remaining}/{package.quantity_purchased} Academic Speaking packages remaining")
        print(f"Package status: {package.status}")

if __name__ == "__main__":
    demo_multiple_purchases()