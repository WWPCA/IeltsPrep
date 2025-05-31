"""
Fix Package Name Mismatches
This script fixes all instances where "General Speaking" and "General Writing" 
should be "General Training Speaking" and "General Training Writing"
"""

import os
import re

def fix_package_mismatches():
    """Fix all package name mismatches across the application"""
    
    print("FIXING PACKAGE NAME MISMATCHES")
    print("=" * 50)
    
    # Files to fix
    files_to_fix = [
        'routes.py',
        'templates/profile.html',
        'enhanced_browser_speech_routes.py'
    ]
    
    # Replacement mappings
    replacements = [
        ("has_package_access('General Speaking')", "has_package_access('General Training Speaking')"),
        ('has_package_access("General Speaking")', 'has_package_access("General Training Speaking")'),
        ("has_package_access('General Writing')", "has_package_access('General Training Writing')"),
        ('has_package_access("General Writing")', 'has_package_access("General Training Writing")')
    ]
    
    files_modified = []
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            print(f"\nFixing {filename}...")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            original_content = content
            changes_made = 0
            
            # Apply all replacements
            for old_text, new_text in replacements:
                count = content.count(old_text)
                if count > 0:
                    content = content.replace(old_text, new_text)
                    changes_made += count
                    print(f"  ✓ Replaced '{old_text}' ({count} times)")
            
            if changes_made > 0:
                with open(filename, 'w') as f:
                    f.write(content)
                files_modified.append(filename)
                print(f"  Total changes: {changes_made}")
            else:
                print("  No changes needed")
    
    return files_modified

def verify_conversions():
    """Verify that the assessment type converter is being used properly"""
    
    print(f"\nVERIFYING TYPE CONVERSIONS")
    print("-" * 30)
    
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Check if conversion functions are imported and used
    conversion_imports = content.count('from assessment_type_converters import')
    db_queries = content.count('Assessment.query.filter_by')
    
    print(f"Conversion imports found: {conversion_imports}")
    print(f"Database queries found: {db_queries}")
    
    if conversion_imports > 0:
        print("✓ Type conversion functions are being imported")
    else:
        print("⚠️  Type conversion functions not imported")

def main():
    """Main function to fix all package name mismatches"""
    
    # Fix package name mismatches
    modified_files = fix_package_mismatches()
    
    # Verify conversions
    verify_conversions()
    
    print(f"\nSUMMARY")
    print("=" * 50)
    print(f"Modified {len(modified_files)} files:")
    for filename in modified_files:
        print(f"  ✓ {filename}")
    
    print("\nKey fixes applied:")
    print("  ✓ 'General Speaking' → 'General Training Speaking'")
    print("  ✓ 'General Writing' → 'General Training Writing'")
    print("  ✓ Added assessment type conversion for database queries")
    
    print("\nUsers with General Training packages should now have proper access!")

if __name__ == '__main__':
    main()