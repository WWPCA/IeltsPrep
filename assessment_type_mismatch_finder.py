"""
Assessment Type Mismatch Finder
Comprehensive analysis to find and fix assessment type inconsistencies
"""

import os
import re

def check_routes_assessment_types():
    """Check routes.py for assessment type consistency"""
    
    print("CHECKING ROUTES.PY ASSESSMENT TYPES")
    print("=" * 50)
    
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Find all assessment type references
    assessment_refs = []
    
    # Route parameters with assessment_type
    route_params = re.findall(r'assessment_type[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
    for param in route_params:
        assessment_refs.append(('route_parameter', param))
    
    # URL route definitions
    url_routes = re.findall(r'@app\.route.*?<([^>]*assessment_type[^>]*)>', content)
    for route in url_routes:
        assessment_refs.append(('url_route', route))
    
    # Function parameters
    func_params = re.findall(r'def\s+\w+\([^)]*assessment_type\s*=\s*[\'"]([^\'\"]+)[\'"]', content)
    for param in func_params:
        assessment_refs.append(('function_default', param))
    
    # Template variables
    template_vars = re.findall(r'{{\s*assessment_type\s*}}\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
    for var in template_vars:
        assessment_refs.append(('template_variable', var))
    
    print("Found assessment type references:")
    for ref_type, value in assessment_refs:
        print(f"  {ref_type}: '{value}'")
    
    return assessment_refs

def check_package_name_consistency():
    """Check package name consistency across files"""
    
    print("\nCHECKING PACKAGE NAME CONSISTENCY")
    print("=" * 50)
    
    files_to_check = [
        'routes.py', 'models.py', 'assessment_assignment_service.py',
        'enhanced_assessment_assignment_service.py', 'payment_services.py'
    ]
    
    package_refs = {}
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
            
            # Find package name patterns
            package_names = re.findall(r'package_name[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
            if package_names:
                package_refs[filename] = package_names
            
            # Also check for hardcoded package names
            hardcoded = re.findall(r'[\'"]([^\'\"]*(?:Speaking|Writing)[^\'\"]*)[\'"]', content)
            speaking_writing = [h for h in hardcoded if ('Speaking' in h or 'Writing' in h) and len(h) > 5]
            if speaking_writing:
                package_refs[f"{filename}_hardcoded"] = speaking_writing
    
    print("Package name references found:")
    for filename, names in package_refs.items():
        print(f"\n{filename}:")
        for name in set(names):  # Remove duplicates
            print(f"  '{name}'")
    
    return package_refs

def check_maya_conversation_types():
    """Check Maya conversation system for type consistency"""
    
    print("\nCHECKING MAYA CONVERSATION TYPES")
    print("=" * 50)
    
    files_to_check = ['nova_sonic_services.py', 'templates/assessments/conversational_speaking.html']
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\nChecking {filename}...")
            with open(filename, 'r') as f:
                content = f.read()
            
            # Look for assessment_type references
            assessment_types = re.findall(r'assessment_type[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
            if assessment_types:
                print(f"  Assessment types: {assessment_types}")
            
            # Look for route format vs database format mismatches
            underscore_types = [t for t in assessment_types if '_' in t]
            space_types = [t for t in assessment_types if ' ' in t and '_' not in t]
            
            if underscore_types:
                print(f"  Route format (underscore): {underscore_types}")
            if space_types:
                print(f"  Database format (spaces): {space_types}")
            
            if not assessment_types:
                print("  No assessment type references found")

def check_database_model_consistency():
    """Check database models for assessment type consistency"""
    
    print("\nCHECKING DATABASE MODEL CONSISTENCY")
    print("=" * 50)
    
    with open('models.py', 'r') as f:
        content = f.read()
    
    # Look for assessment_type field definitions
    type_fields = re.findall(r'assessment_type\s*=\s*[^,\n]+', content)
    print("Assessment type field definitions:")
    for field in type_fields:
        print(f"  {field}")
    
    # Look for any hardcoded assessment types in models
    hardcoded = re.findall(r'[\'"]([^\'\"]*(?:Speaking|Writing|Academic|General)[^\'\"]*)[\'"]', content)
    assessment_related = [h for h in hardcoded if any(word in h for word in ['Speaking', 'Writing', 'Academic', 'General']) and len(h) > 3]
    
    if assessment_related:
        print("\nHardcoded assessment-related strings:")
        for item in set(assessment_related):
            print(f"  '{item}'")

def identify_conversion_needs():
    """Identify where type conversion is needed"""
    
    print("\nIDENTIFYING CONVERSION NEEDS")
    print("=" * 50)
    
    with open('routes.py', 'r') as f:
        routes_content = f.read()
    
    # Find routes that receive underscore format but query database
    route_functions = re.findall(r'@app\.route.*?\ndef\s+(\w+)\([^)]*assessment_type[^)]*\):(.*?)(?=@app\.route|\ndef\s+\w+|$)', routes_content, re.DOTALL)
    
    conversion_needed = []
    
    for func_name, func_body in route_functions:
        # Check if function queries database with assessment_type
        if 'AssessmentStructure.query' in func_body or 'filter_by' in func_body:
            # Check if it uses assessment_type directly in query
            if 'assessment_type' in func_body and 'filter' in func_body:
                conversion_needed.append(func_name)
    
    if conversion_needed:
        print("Functions that may need type conversion:")
        for func in conversion_needed:
            print(f"  {func}")
    else:
        print("No obvious conversion needs found")

def main():
    """Run comprehensive assessment type review"""
    
    print("COMPREHENSIVE ASSESSMENT TYPE MISMATCH REVIEW")
    print("=" * 60)
    
    # Check different components
    route_refs = check_routes_assessment_types()
    package_refs = check_package_name_consistency()
    check_maya_conversation_types()
    check_database_model_consistency()
    identify_conversion_needs()
    
    # Summary
    print("\nSUMMARY OF FINDINGS")
    print("=" * 50)
    
    # Expected formats
    expected_route_formats = ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing']
    expected_db_formats = ['Academic Speaking', 'General Speaking', 'Academic Writing', 'General Writing']
    expected_package_formats = ['Academic Speaking', 'General Training Speaking', 'Academic Writing', 'General Training Writing']
    
    print("Expected formats:")
    print(f"  Routes: {expected_route_formats}")
    print(f"  Database: {expected_db_formats}")
    print(f"  Packages: {expected_package_formats}")
    
    # Check for mismatches
    route_values = [ref[1] for ref in route_refs]
    route_mismatches = [v for v in route_values if v not in expected_route_formats and v not in expected_db_formats]
    
    if route_mismatches:
        print(f"\nPOTENTIAL MISMATCHES FOUND:")
        for mismatch in route_mismatches:
            print(f"  Unexpected format: '{mismatch}'")
    else:
        print("\n✓ No obvious format mismatches found")

if __name__ == '__main__':
    main()