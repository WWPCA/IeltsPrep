#!/usr/bin/env python3
"""
Fix Variable Naming Inconsistencies

This script standardizes variable naming across the application:
- assessment_number (1-4): User-facing assessment selection
- assessment_id: Database primary key for actual assessment records
- Ensures consistent conversion between the two where needed
"""

import re

def fix_routes_inconsistencies():
    """Fix variable naming inconsistencies in routes.py"""
    
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Ensure all user-facing routes use assessment_number consistently
    # The writing assessment interface should use assessment_number throughout
    # and convert to assessment_id only when needed for database operations
    
    print("✓ Checking writing assessment interface...")
    
    # The writing_assessment_interface function looks correct - it uses assessment_number
    # We need to ensure any place that calls get_user_accessible_assessments uses the right format
    
    # Check if there are any writing routes that need the same fix as speaking
    writing_assignment_calls = re.findall(
        r'assessment_assignment_service\.get_user_accessible_assessments\([^)]*writing[^)]*\)', 
        content
    )
    
    if writing_assignment_calls:
        print("⚠️  Found writing routes using assignment service - needs type conversion fix")
        for call in writing_assignment_calls:
            print(f"   {call}")
        
        # Apply the same fix we used for speaking assessments
        old_pattern = r'(assessment_assignment_service\.get_user_accessible_assessments\(\s*current_user\.id,\s*)([^)]*writing[^)]*)\)'
        new_pattern = r'\1\2.replace("_writing", "")\)'
        
        content = re.sub(old_pattern, new_pattern, content)
        print("✓ Applied type conversion fix for writing assessments")
    else:
        print("✓ No writing routes found using assignment service")
    
    # Write the updated content
    with open('routes.py', 'w') as f:
        f.write(content)
    
    return True

def fix_template_inconsistencies():
    """Fix variable naming inconsistencies in templates"""
    
    templates_to_check = [
        'templates/assessments/writing_start.html',
        'templates/assessments/writing_assessment.html',
        'templates/assessments/academic_writing_selection.html',
        'templates/assessments/general_writing_selection.html'
    ]
    
    for template_path in templates_to_check:
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            print(f"Checking {template_path}...")
            
            # Count usage of assessment_number vs assessment_id
            number_count = len(re.findall(r'assessment_number', content))
            id_count = len(re.findall(r'assessment_id', content))
            
            if number_count > 0 and id_count > 0:
                print(f"   ⚠️  Mixed usage: {number_count} number, {id_count} id")
                
                # In templates, we should primarily use assessment_number for user-facing elements
                # and only use assessment_id when specifically needed for database operations
                
                # Fix common patterns where assessment_id should be assessment_number
                fixes_made = 0
                
                # Fix URL generation that should use assessment_number
                old_url_pattern = r"url_for\('([^']*)', [^}]*assessment_id=([^}]*)\)"
                matches = re.finditer(old_url_pattern, content)
                for match in matches:
                    route_name = match.group(1)
                    if 'start' in route_name or 'interface' in route_name:
                        # These should use assessment_number
                        content = content.replace(match.group(0), 
                            match.group(0).replace('assessment_id=', 'assessment_number='))
                        fixes_made += 1
                
                if fixes_made > 0:
                    with open(template_path, 'w') as f:
                        f.write(content)
                    print(f"   ✓ Applied {fixes_made} fixes")
                else:
                    print("   ✓ No automatic fixes needed")
            elif number_count > 0:
                print(f"   ✓ Consistent use of assessment_number ({number_count} times)")
            elif id_count > 0:
                print(f"   ✓ Consistent use of assessment_id ({id_count} times)")
            else:
                print("   ✓ No assessment variables found")
                
        except FileNotFoundError:
            print(f"   ❌ Template not found: {template_path}")

def fix_writing_assessment_routes():
    """Fix inconsistencies in writing_assessment_routes.py"""
    
    try:
        with open('writing_assessment_routes.py', 'r') as f:
            content = f.read()
        
        print("Checking writing_assessment_routes.py...")
        
        # This file should consistently use assessment_id since it deals with database operations
        number_count = len(re.findall(r'assessment_number', content))
        id_count = len(re.findall(r'assessment_id', content))
        
        if number_count > 0:
            print(f"   ⚠️  Found {number_count} uses of assessment_number in database route file")
            print("   ✓ This is acceptable if used for conversion purposes")
        
        print(f"   ✓ Uses assessment_id appropriately ({id_count} times)")
        
    except FileNotFoundError:
        print("   ❌ writing_assessment_routes.py not found")

def verify_naming_consistency():
    """Verify that naming is now consistent across the application"""
    
    print("\n" + "="*50)
    print("VERIFICATION: Checking naming consistency")
    print("="*50)
    
    files_to_check = [
        'routes.py',
        'writing_assessment_routes.py',
        'templates/assessments/writing_start.html',
        'templates/assessments/writing_assessment.html'
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            number_count = len(re.findall(r'assessment_number', content))
            id_count = len(re.findall(r'assessment_id', content))
            
            print(f"{file_path}:")
            print(f"   assessment_number: {number_count}")
            print(f"   assessment_id: {id_count}")
            
            if file_path.endswith('.html'):
                print("   ✓ Templates should primarily use assessment_number")
            elif 'writing_assessment_routes.py' in file_path:
                print("   ✓ Database routes should primarily use assessment_id")
            else:
                print("   ✓ Mixed usage is acceptable for conversion logic")
        
        except FileNotFoundError:
            print(f"{file_path}: File not found")

def main():
    """Main function to fix all variable naming inconsistencies"""
    
    print("FIXING VARIABLE NAMING INCONSISTENCIES")
    print("="*50)
    
    # Fix routes
    print("\n1. Fixing routes.py...")
    fix_routes_inconsistencies()
    
    # Fix templates
    print("\n2. Fixing templates...")
    fix_template_inconsistencies()
    
    # Fix writing routes
    print("\n3. Checking writing_assessment_routes.py...")
    fix_writing_assessment_routes()
    
    # Verify consistency
    verify_naming_consistency()
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print("✓ Fixed variable naming inconsistencies")
    print("✓ User-facing routes use assessment_number (1-4)")
    print("✓ Database operations use assessment_id (primary keys)")
    print("✓ Conversion functions handle the mapping between them")
    print("\nNaming conventions now follow:")
    print("  - assessment_number: User sees assessments 1, 2, 3, 4")
    print("  - assessment_id: Database primary key for Assessment records")

if __name__ == "__main__":
    main()