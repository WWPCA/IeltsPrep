"""
Get Test Account Access
Provides access to the test account with all assessment packages
"""

from main import app
from models import User
from werkzeug.security import generate_password_hash

def setup_test_account_access():
    """Set up access to the test account with known password"""
    
    with app.app_context():
        # Find the test account
        test_user = User.query.filter_by(email='test@ieltsaiprep.com').first()
        
        if test_user:
            print('TEST ACCOUNT FOUND')
            print('=' * 40)
            print(f'Email: {test_user.email}')
            print('Current packages available:')
            print('- Academic Writing (1 assessment)')
            print('- Academic Speaking (1 assessment)')  
            print('- General Writing (1 assessment)')
            print('- General Speaking (1 assessment)')
            
            # Set a known password for testing
            new_password = 'TestPass123!'
            test_user.password_hash = generate_password_hash(new_password)
            
            # Ensure account is activated
            test_user.account_activated = True
            test_user.email_verified = True
            test_user.is_active = True
            
            from app import db
            db.session.commit()
            
            print('\nACCOUNT READY FOR TESTING')
            print('=' * 40)
            print(f'Email: {test_user.email}')
            print(f'Password: {new_password}')
            print('\nYou can now login and test:')
            print('1. Academic Speaking with Maya')
            print('2. General Speaking with Maya') 
            print('3. Academic Writing assessments')
            print('4. General Writing assessments')
            
        else:
            print('Test account not found')

if __name__ == "__main__":
    setup_test_account_access()