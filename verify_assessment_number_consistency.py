"""
Verify Assessment Number Consistency

This script checks that assessment numbers 1-4 are handled consistently 
across all assessment routes and templates.
"""

import os
import re
from app import app, db
from models import Assessment

def check_assessment_number_routes():
    """Check all routes that handle assessment numbers 1-4."""
    
    print("Checking assessment number handling across all routes...")
    print("="*60)
    
    # Files to check
    route_files = ['routes.py', 'assessment_routes.py', 'writing_assessment_routes.py']
    template_files = ['templates/profile.html', 'templates/assessments/speaking_start.html']
    
    # Check route files
    for filename in route_files:
        if os.path.exists(filename):
            print(f"\nChecking {filename}...")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            # Find all functions that accept assessment_number
            number_functions = re.findall(r'def\s+(\w+)\([^)]*assessment_number[^)]*\)', content)
            
            # Find all functions that accept assessment_id
            id_functions = re.findall(r'def\s+(\w+)\([^)]*assessment_id[^)]*\)', content)
            
            # Find validation patterns for assessment_number
            validations = re.findall(r'assessment_number.*?\[1,\s*2,\s*3,\s*4\]', content)
            
            print(f"  Functions using assessment_number: {number_functions}")
            print(f"  Functions using assessment_id: {id_functions}")
            print(f"  Number validations found: {len(validations)}")
            
            # Check for package access patterns
            package_checks = re.findall(r'has_package_access\([^)]+\)', content)
            print(f"  Package access checks: {len(package_checks)}")
            
            for check in package_checks:
                print(f"    {check}")
    
    # Check template files
    for filename in template_files:
        if os.path.exists(filename):
            print(f"\nChecking {filename}...")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            # Find URL patterns
            url_patterns = re.findall(r'url_for\([^)]+assessment[^)]*\)', content)
            print(f"  URL patterns found: {len(url_patterns)}")
            
            for pattern in url_patterns:
                print(f"    {pattern}")
    
    print("\n" + "="*60)
    print("ASSESSMENT NUMBER CONSISTENCY CHECK")
    print("="*60)
    
    # Check database to see what assessments exist
    with app.app_context():
        academic_speaking = Assessment.query.filter_by(assessment_type='academic').all()
        general_speaking = Assessment.query.filter_by(assessment_type='general').all()
        
        print(f"Academic assessments in database: {len(academic_speaking)}")
        print(f"General assessments in database: {len(general_speaking)}")
        
        if academic_speaking:
            print("Academic assessment IDs:", [a.id for a in academic_speaking])
        if general_speaking:
            print("General assessment IDs:", [a.id for a in general_speaking])
    
    print("\nRECOMMENDATIONS:")
    print("1. All user-facing routes should accept assessment_number (1-4)")
    print("2. All package access checks should use proper package names")
    print("3. Templates should link to assessment_number routes")
    print("4. Database operations should convert number to ID as needed")

if __name__ == "__main__":
    check_assessment_number_routes()