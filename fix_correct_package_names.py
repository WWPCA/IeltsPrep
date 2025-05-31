"""
Fix Package Names to Match Actual Products
Corrects package names to:
1. Academic Speaking
2. Academic Writing  
3. General Speaking
4. General Writing
"""

import os
import re

def fix_package_names():
    """Fix package names to match the actual 4 products"""
    
    print("FIXING PACKAGE NAMES TO MATCH ACTUAL PRODUCTS")
    print("=" * 60)
    
    # Files to fix
    files_to_fix = [
        'routes.py',
        'templates/profile.html', 
        'enhanced_browser_speech_routes.py',
        'assessment_type_converters.py'
    ]
    
    # Incorrect mappings to fix
    replacements = [
        ("'General Training Speaking'", "'General Speaking'"),
        ('"General Training Speaking"', '"General Speaking"'),
        ("'General Training Writing'", "'General Writing'"),
        ('"General Training Writing"', '"General Writing"')
    ]
    
    files_modified = []
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            print(f"\nFixing {filename}...")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            changes_made = 0
            
            for old_text, new_text in replacements:
                count = content.count(old_text)
                if count > 0:
                    content = content.replace(old_text, new_text)
                    changes_made += count
                    print(f"  ✓ {old_text} → {new_text} ({count} times)")
            
            if changes_made > 0:
                with open(filename, 'w') as f:
                    f.write(content)
                files_modified.append(filename)
                print(f"  Total changes: {changes_made}")
            else:
                print("  No changes needed")
    
    return files_modified

def main():
    """Main function"""
    modified_files = fix_package_names()
    
    print(f"\nSUMMARY")
    print("=" * 30)
    print(f"Modified {len(modified_files)} files:")
    for filename in modified_files:
        print(f"  ✓ {filename}")
    
    print("\nCorrect package names now:")
    print("  1. Academic Speaking")
    print("  2. Academic Writing")
    print("  3. General Speaking") 
    print("  4. General Writing")

if __name__ == '__main__':
    main()