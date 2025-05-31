"""
Standardize Package Names Across All Routes and Templates

This script ensures consistent package naming throughout the application.
Database stores: "Academic Speaking", "General Speaking", "Academic Writing", "General Writing"
Routes should use these exact names when calling has_package_access()
"""

import os
import re
from app import app, db
from models import User, UserPackage

def standardize_package_names():
    """Standardize package names across all files in the application."""
    
    # Standard package names (how they're stored in database)
    standard_names = {
        'academic_speaking': 'Academic Speaking',
        'general_speaking': 'General Speaking', 
        'academic_writing': 'Academic Writing',
        'general_writing': 'General Writing'
    }
    
    # Files to check and update
    files_to_check = [
        'routes.py',
        'enhanced_browser_speech_routes.py',
        'assessment_routes.py',
        'writing_assessment_routes.py',
        'add_assessment_routes.py'
    ]
    
    print("Standardizing package names across all routes...")
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\nChecking {filename}...")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Fix has_package_access calls
            for route_name, standard_name in standard_names.items():
                # Pattern: has_package_access('academic_speaking') -> has_package_access('Academic Speaking')
                pattern = f"has_package_access\\(['\"]({route_name})['\"]\\)"
                replacement = f"has_package_access('{standard_name}')"
                content = re.sub(pattern, replacement, content)
                
                # Pattern: has_package_access("academic_speaking") -> has_package_access("Academic Speaking")
                pattern = f'has_package_access\\(["\']({route_name})["\']\\)'
                replacement = f'has_package_access("{standard_name}")'
                content = re.sub(pattern, replacement, content)
            
            # Check for old-style package status checking patterns
            old_patterns = [
                (r"'Academic Speaking' in package_status", "current_user.has_package_access('Academic Speaking')"),
                (r"'General Speaking' in package_status", "current_user.has_package_access('General Speaking')"),
                (r"'Academic Writing' in package_status", "current_user.has_package_access('Academic Writing')"),
                (r"'General Writing' in package_status", "current_user.has_package_access('General Writing')"),
                (r'"Academic Speaking" in package_status', 'current_user.has_package_access("Academic Speaking")'),
                (r'"General Speaking" in package_status', 'current_user.has_package_access("General Speaking")'),
                (r'"Academic Writing" in package_status', 'current_user.has_package_access("Academic Writing")'),
                (r'"General Writing" in package_status', 'current_user.has_package_access("General Writing")')
            ]
            
            for old_pattern, new_pattern in old_patterns:
                content = re.sub(old_pattern, new_pattern, content)
            
            # Only write if content changed
            if content != original_content:
                with open(filename, 'w') as f:
                    f.write(content)
                print(f"  ✓ Updated {filename}")
            else:
                print(f"  - No changes needed in {filename}")
    
    # Check database consistency
    print("\nChecking database package names...")
    
    with app.app_context():
        # Get all unique package names from UserPackage table
        package_names = db.session.query(UserPackage.package_name).distinct().all()
        package_names = [name[0] for name in package_names if name[0]]
        
        print(f"Found package names in database: {package_names}")
        
        # Check for any non-standard names
        expected_names = set(standard_names.values())
        found_names = set(package_names)
        
        unexpected_names = found_names - expected_names
        if unexpected_names:
            print(f"⚠️  Found unexpected package names: {unexpected_names}")
            print("Consider updating these to match standard naming convention.")
        else:
            print("✓ All database package names follow standard convention")
    
    print("\n" + "="*60)
    print("PACKAGE NAME STANDARDIZATION COMPLETE")
    print("="*60)
    print("Standard package names:")
    for route_name, standard_name in standard_names.items():
        print(f"  Route type '{route_name}' -> Database name '{standard_name}'")
    
    print("\nAll routes should now use:")
    print("  - has_package_access('Academic Speaking')")
    print("  - has_package_access('General Speaking')")  
    print("  - has_package_access('Academic Writing')")
    print("  - has_package_access('General Writing')")

if __name__ == "__main__":
    standardize_package_names()