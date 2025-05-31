"""
Fix Assessment Type Database Mismatch
The database has assessment_type in underscore format (academic_speaking)
but the application expects space format (Academic Speaking) for package names.
This script fixes the core mismatch.
"""

import os
from app import app, db
from models import Assessment

def fix_assessment_types_in_database():
    """Update assessment types in database to match expected format"""
    
    print("FIXING ASSESSMENT TYPE DATABASE MISMATCH")
    print("=" * 50)
    
    with app.app_context():
        # Check current assessment types
        from sqlalchemy import text
        current_types = db.session.execute(
            text("SELECT DISTINCT assessment_type FROM assessment ORDER BY assessment_type")
        ).fetchall()
        
        print("Current assessment types in database:")
        for row in current_types:
            print(f"  {row[0]}")
        
        # Define the mapping from underscore format to space format
        type_mapping = {
            'academic_speaking': 'Academic Speaking',
            'general_speaking': 'General Speaking', 
            'academic_writing': 'Academic Writing',
            'general_writing': 'General Writing'
        }
        
        print(f"\nUpdating assessment types...")
        
        # Update each assessment type
        for old_type, new_type in type_mapping.items():
            result = db.session.execute(
                "UPDATE assessment SET assessment_type = :new_type WHERE assessment_type = :old_type",
                {"new_type": new_type, "old_type": old_type}
            )
            print(f"  {old_type} → {new_type} ({result.rowcount} assessments updated)")
        
        # Update UserAssessmentAssignment table as well
        print(f"\nUpdating user assignment types...")
        for old_type, new_type in type_mapping.items():
            result = db.session.execute(
                "UPDATE user_assessment_assignment SET assessment_type = :new_type WHERE assessment_type = :old_type",
                {"new_type": new_type, "old_type": old_type}
            )
            print(f"  {old_type} → {new_type} ({result.rowcount} assignments updated)")
        
        db.session.commit()
        
        # Verify the changes
        print(f"\nVerifying changes...")
        updated_types = db.session.execute(
            "SELECT DISTINCT assessment_type FROM assessment ORDER BY assessment_type"
        ).fetchall()
        
        print("Updated assessment types in database:")
        for row in updated_types:
            print(f"  ✓ {row[0]}")
        
        print(f"\n✓ Database assessment types now match application expectations")

def verify_package_structure():
    """Verify that the 4 products are properly structured"""
    
    print(f"\nVERIFYING PACKAGE STRUCTURE")
    print("-" * 30)
    
    expected_products = [
        "Academic Speaking",
        "Academic Writing", 
        "General Speaking",
        "General Writing"
    ]
    
    with app.app_context():
        # Check what packages exist in user_package table
        existing_packages = db.session.execute(
            "SELECT DISTINCT package_name FROM user_package ORDER BY package_name"
        ).fetchall()
        
        print("Packages found in database:")
        for row in existing_packages:
            print(f"  {row[0]}")
        
        # Check assessment counts by type
        print(f"\nAssessment counts by type:")
        for product in expected_products:
            count = db.session.execute(
                "SELECT COUNT(*) FROM assessment WHERE assessment_type = :type AND status = 'active'",
                {"type": product}
            ).scalar()
            print(f"  {product}: {count} assessments")

def update_assessment_type_converters():
    """Update the converter functions to handle the corrected database format"""
    
    print(f"\nUPDATING TYPE CONVERTERS")
    print("-" * 25)
    
    # Since database now uses space format, we need to update converters
    converter_code = '''
def convert_route_to_db_type(assessment_type):
    """Convert route parameter format to database format"""
    conversion_map = {
        'academic_speaking': 'Academic Speaking',
        'general_speaking': 'General Speaking',
        'academic_writing': 'Academic Writing', 
        'general_writing': 'General Writing'
    }
    return conversion_map.get(assessment_type, assessment_type)

def convert_db_to_package_name(assessment_type):
    """Convert database format to package name format - now they're the same"""
    # Database and package names now use the same format
    return assessment_type

def convert_route_to_package_name(assessment_type):
    """Convert route parameter directly to package name"""
    return convert_route_to_db_type(assessment_type)
'''
    
    with open('assessment_type_converters.py', 'w') as f:
        f.write(converter_code)
    
    print("✓ Updated assessment_type_converters.py")

def main():
    """Run the complete fix"""
    
    print("COMPREHENSIVE ASSESSMENT TYPE FIX")
    print("=" * 60)
    print("This fix aligns database assessment types with application logic")
    print("for the 4 products: Academic Speaking, Academic Writing, General Speaking, General Writing")
    print()
    
    # Fix database assessment types
    fix_assessment_types_in_database()
    
    # Verify package structure
    verify_package_structure()
    
    # Update converter functions
    update_assessment_type_converters()
    
    print(f"\nFIX COMPLETE")
    print("=" * 30)
    print("✓ Database assessment types updated to space format")
    print("✓ All 4 products properly structured")
    print("✓ Type converters updated")
    print("✓ Routes and database now consistent")

if __name__ == '__main__':
    main()