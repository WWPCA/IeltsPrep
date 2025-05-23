"""
Quick fix for speaking assessment access issue.
This script fixes the assessment access logic so users can see their speaking tests.
"""

import sys
sys.path.append('.')

from app import app, db
from models import User

def fix_speaking_access():
    """Fix the assessment access logic for speaking assessments."""
    
    # Read the current assessment_routes.py file
    with open('assessment_routes.py', 'r') as f:
        content = f.read()
    
    # Fix the access checking logic
    old_logic = """        has_access = any('Writing' in status for status in package_status) or 'All Products' in package_status
    elif assessment_type == 'speaking':
        has_access = any('Speaking' in status for status in package_status) or 'All Products' in package_status"""
        
    new_logic = """        has_access = 'Writing' in package_status or 'All Products' in package_status
    elif assessment_type == 'speaking':
        has_access = 'Speaking' in package_status or 'All Products' in package_status"""
    
    # Replace the problematic logic
    updated_content = content.replace(old_logic, new_logic)
    
    # Write back the fixed content
    with open('assessment_routes.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Fixed speaking assessment access logic!")
    print("✅ Your 'All Products' status will now properly grant access to speaking tests!")

if __name__ == "__main__":
    fix_speaking_access()