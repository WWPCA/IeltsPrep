"""
Setup multiple individual assessment packages for test user.
This demonstrates how the system handles users with multiple package purchases.
"""
from app import app, db
from models import User, UserPackage
from datetime import datetime, timedelta

def setup_test_user_packages():
    """Set up the test user with multiple individual packages."""
    
    with app.app_context():
        user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        if not user:
            print("Test user not found")
            return
        
        # Clear any existing packages for this user
        UserPackage.query.filter_by(user_id=user.id).delete()
        
        # Add multiple individual packages
        packages_to_add = [
            "Academic Speaking",
            "Academic Writing", 
            "General Speaking"
        ]
        
        for package_name in packages_to_add:
            package = UserPackage(
                user_id=user.id,
                package_name=package_name,
                purchase_date=datetime.utcnow(),
                expiry_date=datetime.utcnow() + timedelta(days=30),  # 30 days from now
                status='active'
            )
            db.session.add(package)
        
        # Clear the legacy assessment_package_status to force use of new system
        user.assessment_package_status = "none"
        
        db.session.commit()
        
        print(f"Successfully added {len(packages_to_add)} packages for test user:")
        for package_name in packages_to_add:
            print(f"  - {package_name}")
        
        # Verify the packages
        user_packages = UserPackage.query.filter_by(user_id=user.id).all()
        print(f"\nVerification - User now has {len(user_packages)} active packages:")
        for pkg in user_packages:
            print(f"  - {pkg.package_name} (expires: {pkg.expiry_date})")
        
        print(f"\nUser has active assessment package: {user.has_active_assessment_package()}")
        print(f"User has Academic Speaking access: {user.has_package_access('Academic Speaking')}")
        print(f"User has General Writing access: {user.has_package_access('General Writing')}")

if __name__ == "__main__":
    setup_test_user_packages()