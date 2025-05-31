"""
Comprehensive Assessment Diagnostic
Checks for mismatches between routes, database queries, and assessment numbering (1-4)
for all four assessment types: Academic Speaking, Academic Writing, General Speaking, General Writing
"""

import os
import re

def check_assessment_routes():
    """Check all assessment-related routes for consistency"""
    
    print("COMPREHENSIVE ASSESSMENT ROUTE DIAGNOSTIC")
    print("=" * 60)
    
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Expected assessment types in routes (underscore format)
    expected_route_types = ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing']
    
    # Expected package names for access checks
    expected_packages = ['Academic Speaking', 'General Speaking', 'Academic Writing', 'General Writing']
    
    # Find all route definitions with assessment_type
    route_patterns = re.findall(r'@app\.route\([\'"]([^\'\"]*<assessment_type>[^\'\"]*)[\'"].*?\ndef\s+(\w+)', content, re.DOTALL)
    
    print("ASSESSMENT ROUTES FOUND:")
    print("-" * 30)
    for route_pattern, function_name in route_patterns:
        print(f"  {function_name}: {route_pattern}")
    
    # Check assessment number routes (1-4)
    number_routes = re.findall(r'@app\.route\([\'"]([^\'\"]*<int:assessment_number>[^\'\"]*)[\'"].*?\ndef\s+(\w+)', content, re.DOTALL)
    
    print(f"\nASSESSMENT NUMBER ROUTES (1-4):")
    print("-" * 30)
    for route_pattern, function_name in number_routes:
        print(f"  {function_name}: {route_pattern}")
    
    # Check for database queries that might have type mismatches
    print(f"\nDATABASE QUERY ANALYSIS:")
    print("-" * 30)
    
    # Find Assessment.query.filter_by patterns
    db_queries = re.findall(r'Assessment\.query\.filter_by\([^)]*assessment_type\s*=\s*([^,)]+)', content)
    print("Assessment queries with assessment_type:")
    for query in db_queries:
        print(f"  {query}")
    
    # Check package access patterns
    package_checks = re.findall(r'has_package_access\([\'"]([^\'\"]+)[\'"]', content)
    print(f"\nPackage access checks:")
    for package in set(package_checks):
        status = "✓" if package in expected_packages else "⚠️"
        print(f"  {status} {package}")
    
    return route_patterns, number_routes, db_queries, package_checks

def check_assessment_assignment_service():
    """Check assessment assignment service for type consistency"""
    
    print(f"\nASSESSMENT ASSIGNMENT SERVICE ANALYSIS:")
    print("-" * 40)
    
    files_to_check = ['assessment_assignment_service.py', 'enhanced_assessment_assignment_service.py']
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\nChecking {filename}...")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            # Check for assessment type handling
            type_patterns = re.findall(r'assessment_type[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
            if type_patterns:
                print(f"  Assessment types referenced:")
                for pattern in set(type_patterns):
                    print(f"    {pattern}")
            
            # Check for package name patterns
            package_patterns = re.findall(r'package_name[\'"]?\s*[=:]\s*[\'"]([^\'\"]+)[\'"]', content)
            if package_patterns:
                print(f"  Package names referenced:")
                for pattern in set(package_patterns):
                    print(f"    {pattern}")

def check_template_consistency():
    """Check templates for route and assessment consistency"""
    
    print(f"\nTEMPLATE ANALYSIS:")
    print("-" * 20)
    
    template_files = [
        'templates/profile.html',
        'templates/assessments/speaking_start.html',
        'templates/assessments/writing_start.html',
        'templates/assessments/speaking_selection.html',
        'templates/assessments/academic_writing_selection.html',
        'templates/assessments/general_writing_selection.html'
    ]
    
    for template_path in template_files:
        if os.path.exists(template_path):
            print(f"\nChecking {template_path}...")
            
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check url_for patterns with assessment numbers
            url_patterns = re.findall(r'url_for\([\'"]([^\'\"]+)[\'"][^)]*assessment_number[^)]*\)', content)
            if url_patterns:
                print(f"  URL patterns with assessment_number:")
                for pattern in url_patterns:
                    print(f"    {pattern}")
            
            # Check url_for patterns with assessment_type
            type_url_patterns = re.findall(r'url_for\([\'"]([^\'\"]+)[\'"][^)]*assessment_type[^)]*\)', content)
            if type_url_patterns:
                print(f"  URL patterns with assessment_type:")
                for pattern in type_url_patterns:
                    print(f"    {pattern}")
            
            # Check package access in templates
            template_package_checks = re.findall(r'has_package_access\([\'"]([^\'\"]+)[\'"]', content)
            if template_package_checks:
                print(f"  Package access checks:")
                for package in set(template_package_checks):
                    print(f"    {package}")

def check_assessment_number_handling():
    """Check how assessment numbers 1-4 are handled across the system"""
    
    print(f"\nASSESSMENT NUMBER (1-4) HANDLING:")
    print("-" * 35)
    
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Find functions that accept assessment_number parameter
    number_functions = re.findall(r'def\s+(\w+)\([^)]*assessment_number[^)]*\):', content)
    print("Functions accepting assessment_number:")
    for func in number_functions:
        print(f"  {func}")
    
    # Find validation logic for assessment numbers
    validations = re.findall(r'assessment_number\s+(?:not\s+)?in\s+\[[^\]]+\]', content)
    if validations:
        print(f"\nValidation patterns found:")
        for validation in validations:
            print(f"  {validation}")
    
    # Check for number to ID conversion logic
    conversions = re.findall(r'assessments\[assessment_number\s*[-+]\s*\d+\]', content)
    if conversions:
        print(f"\nNumber to ID conversions found:")
        for conversion in conversions:
            print(f"  {conversion}")

def identify_potential_mismatches():
    """Identify potential mismatches and inconsistencies"""
    
    print(f"\nPOTENTIAL MISMATCH ANALYSIS:")
    print("-" * 30)
    
    issues = []
    
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Check for mixed format usage
    if 'academic_speaking' in content and 'Academic Speaking' in content:
        # This is expected - route params vs package names
        pass
    
    # Check for incorrect assessment_type in database queries
    incorrect_db_queries = re.findall(r'filter_by\([^)]*assessment_type\s*=\s*assessment_type[^)]*\)', content)
    if incorrect_db_queries:
        issues.append("Direct assessment_type usage in database queries (may need conversion)")
    
    # Check for hardcoded assessment numbers outside 1-4 range
    hardcoded_numbers = re.findall(r'assessment_number\s*[=!<>]+\s*([0-9]+)', content)
    for number in hardcoded_numbers:
        if int(number) < 1 or int(number) > 4:
            issues.append(f"Assessment number {number} outside expected range 1-4")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✓ No obvious mismatches detected")

def main():
    """Run comprehensive diagnostic"""
    
    # Check all components
    route_patterns, number_routes, db_queries, package_checks = check_assessment_routes()
    check_assessment_assignment_service()
    check_template_consistency()
    check_assessment_number_handling()
    identify_potential_mismatches()
    
    # Summary
    print(f"\nDIAGNOSTIC SUMMARY:")
    print("=" * 50)
    print(f"✓ Assessment type routes found: {len(route_patterns)}")
    print(f"✓ Assessment number routes found: {len(number_routes)}")
    print(f"✓ Database queries found: {len(db_queries)}")
    print(f"✓ Package access checks found: {len(set(package_checks))}")
    
    print(f"\nExpected package names:")
    expected_packages = ['Academic Speaking', 'Academic Writing', 'General Speaking', 'General Writing']
    for package in expected_packages:
        status = "✓" if package in package_checks else "⚠️"
        print(f"  {status} {package}")
    
    print(f"\nExpected route formats:")
    expected_routes = ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing']
    for route_type in expected_routes:
        print(f"  ✓ {route_type}")

if __name__ == '__main__':
    main()