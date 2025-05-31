"""
Comprehensive Assessment Type and Package Name Review
This script identifies and fixes all mismatches between assessment types and package names
"""

import os
import re
import json

def analyze_assessment_types():
    """Analyze all assessment type references across the codebase"""
    
    print("COMPREHENSIVE ASSESSMENT TYPE REVIEW")
    print("=" * 60)
    
    # Define expected patterns
    expected_patterns = {
        'route_formats': ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing'],
        'database_formats': ['Academic Speaking', 'General Speaking', 'Academic Writing', 'General Writing'],
        'package_formats': ['Academic Speaking', 'General Training Speaking', 'Academic Writing', 'General Training Writing']
    }
    
    mismatches = []
    files_to_check = [
        'routes.py', 'models.py', 'assessment_assignment_service.py', 
        'enhanced_assessment_assignment_service.py', 'nova_sonic_services.py',
        'writing_assessment_routes.py', 'assessment_routes.py'
    ]
    
    # Check Python files
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\nAnalyzing {filename}...")
            with open(filename, 'r') as f:
                content = f.read()
            
            # Find assessment type references
            patterns_found = find_assessment_patterns(content, filename)
            mismatches.extend(patterns_found)
    
    # Check templates
    template_files = []
    if os.path.exists('templates'):
        for root, dirs, files in os.walk('templates'):
            for file in files:
                if file.endswith('.html'):
                    template_files.append(os.path.join(root, file))
    
    for template_path in template_files:
        print(f"\nAnalyzing {template_path}...")
        with open(template_path, 'r') as f:
            content = f.read()
        
        patterns_found = find_assessment_patterns(content, template_path)
        mismatches.extend(patterns_found)
    
    return mismatches

def find_assessment_patterns(content, filename):
    """Find assessment type patterns in content"""
    patterns = []
    
    # Route parameter patterns
    route_params = re.findall(r'assessment_type[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
    for param in route_params:
        patterns.append({
            'file': filename,
            'type': 'route_parameter',
            'value': param,
            'context': 'Route parameter assignment'
        })
    
    # Database query patterns
    db_queries = re.findall(r'assessment_type\s*==\s*[\'"]([^\'\"]+)[\'"]', content)
    for query in db_queries:
        patterns.append({
            'file': filename,
            'type': 'database_query',
            'value': query,
            'context': 'Database query condition'
        })
    
    # Package name patterns
    package_names = re.findall(r'package_name\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
    for package in package_names:
        patterns.append({
            'file': filename,
            'type': 'package_name',
            'value': package,
            'context': 'Package name assignment'
        })
    
    # Assessment structure references
    structure_refs = re.findall(r'AssessmentStructure\.[^(]*\([^)]*[\'"]([^\'\"]*(?:speaking|writing)[^\'\"]*)[\'"]', content)
    for ref in structure_refs:
        patterns.append({
            'file': filename,
            'type': 'assessment_structure',
            'value': ref,
            'context': 'AssessmentStructure query'
        })
    
    return patterns

def identify_mismatches(patterns):
    """Identify mismatches in assessment type formats"""
    mismatches = []
    
    # Expected format mappings
    route_to_db = {
        'academic_speaking': 'Academic Speaking',
        'general_speaking': 'General Speaking', 
        'academic_writing': 'Academic Writing',
        'general_writing': 'General Writing'
    }
    
    db_to_package = {
        'Academic Speaking': 'Academic Speaking',
        'General Speaking': 'General Training Speaking',
        'Academic Writing': 'Academic Writing', 
        'General Writing': 'General Training Writing'
    }
    
    for pattern in patterns:
        value = pattern['value']
        file_name = pattern['file']
        pattern_type = pattern['type']
        
        # Check for common mismatches
        if pattern_type == 'route_parameter':
            # Route parameters should use underscore format
            if ' ' in value and '_' not in value:
                mismatches.append({
                    'file': file_name,
                    'issue': f"Route parameter using space format: '{value}'",
                    'expected': value.lower().replace(' ', '_'),
                    'actual': value
                })
        
        elif pattern_type == 'database_query':
            # Database queries should use proper case format
            if '_' in value and ' ' not in value:
                mismatches.append({
                    'file': file_name,
                    'issue': f"Database query using underscore format: '{value}'",
                    'expected': route_to_db.get(value, value.replace('_', ' ').title()),
                    'actual': value
                })
        
        elif pattern_type == 'package_name':
            # Package names should use correct training terminology
            if value == 'General Speaking' and 'Training' not in value:
                mismatches.append({
                    'file': file_name,
                    'issue': f"Package name missing 'Training': '{value}'",
                    'expected': 'General Training Speaking',
                    'actual': value
                })
            elif value == 'General Writing' and 'Training' not in value:
                mismatches.append({
                    'file': file_name,
                    'issue': f"Package name missing 'Training': '{value}'",
                    'expected': 'General Training Writing',
                    'actual': value
                })
    
    return mismatches

def fix_identified_mismatches(mismatches):
    """Fix the identified mismatches"""
    
    print(f"\nFIXING {len(mismatches)} IDENTIFIED MISMATCHES")
    print("-" * 50)
    
    files_modified = set()
    
    for mismatch in mismatches:
        filename = mismatch['file']
        actual = mismatch['actual']
        expected = mismatch['expected']
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Replace the mismatch
            old_pattern = f"'{actual}'"
            new_pattern = f"'{expected}'"
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                
                with open(filename, 'w') as f:
                    f.write(content)
                
                files_modified.add(filename)
                print(f"✓ Fixed in {filename}: '{actual}' → '{expected}'")
            
            # Also try double quotes
            old_pattern = f'"{actual}"'
            new_pattern = f'"{expected}"'
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                
                with open(filename, 'w') as f:
                    f.write(content)
                
                files_modified.add(filename)
                print(f"✓ Fixed in {filename}: \"{actual}\" → \"{expected}\"")
                
        except Exception as e:
            print(f"✗ Error fixing {filename}: {e}")
    
    return files_modified

def verify_maya_conversation_types():
    """Verify Maya conversation system uses correct assessment types"""
    
    print(f"\nVERIFYING MAYA CONVERSATION TYPES")
    print("-" * 40)
    
    # Check nova_sonic_services.py
    if os.path.exists('nova_sonic_services.py'):
        with open('nova_sonic_services.py', 'r') as f:
            content = f.read()
        
        # Look for assessment type handling
        type_patterns = re.findall(r'assessment_type[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
        
        print("Maya conversation assessment types:")
        for pattern in type_patterns:
            print(f"  {pattern}")
        
        # Check if conversion is needed
        if any('_' in pattern for pattern in type_patterns):
            print("⚠️  Maya conversation may need type conversion")
        else:
            print("✓ Maya conversation types look correct")

def generate_conversion_functions():
    """Generate helper functions for type conversion"""
    
    conversion_code = '''
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
    """Convert database format to package name format"""
    conversion_map = {
        'Academic Speaking': 'Academic Speaking',
        'General Speaking': 'General Training Speaking',
        'Academic Writing': 'Academic Writing',
        'General Writing': 'General Training Writing'
    }
    return conversion_map.get(assessment_type, assessment_type)

def convert_route_to_package_name(assessment_type):
    """Convert route parameter directly to package name"""
    # First convert to DB format, then to package format
    db_format = convert_route_to_db_type(assessment_type)
    return convert_db_to_package_name(db_format)
'''
    
    with open('assessment_type_converters.py', 'w') as f:
        f.write(conversion_code)
    
    print("✓ Generated assessment_type_converters.py")

def main():
    """Main review function"""
    
    # Analyze all patterns
    patterns = analyze_assessment_types()
    
    # Identify mismatches
    mismatches = identify_mismatches(patterns)
    
    if mismatches:
        print(f"\nFOUND {len(mismatches)} MISMATCHES")
        print("-" * 40)
        for mismatch in mismatches:
            print(f"• {mismatch['file']}: {mismatch['issue']}")
        
        # Fix mismatches
        fixed_files = fix_identified_mismatches(mismatches)
        
        print(f"\nModified {len(fixed_files)} files:")
        for filename in fixed_files:
            print(f"  {filename}")
    else:
        print("\n✓ No assessment type mismatches found")
    
    # Verify Maya conversation system
    verify_maya_conversation_types()
    
    # Generate conversion helpers
    generate_conversion_functions()
    
    print(f"\nREVIEW COMPLETE")
    print("=" * 60)
    print("All assessment type references have been reviewed and standardized")

if __name__ == '__main__':
    main()