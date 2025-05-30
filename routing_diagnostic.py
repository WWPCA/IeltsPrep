#!/usr/bin/env python3
"""
Routing Diagnostic Tool
Identifies inconsistencies between assessment_number and assessment_id usage across the application.
"""

import os
import re
from pathlib import Path

def analyze_file(file_path):
    """Analyze a single file for routing patterns."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {
        'file': str(file_path),
        'assessment_number_patterns': [],
        'assessment_id_patterns': [],
        'route_definitions': [],
        'template_variables': [],
        'navigation_urls': []
    }
    
    # Find assessment_number patterns
    assessment_number_matches = re.finditer(r'assessment_number', content)
    for match in assessment_number_matches:
        line_num = content[:match.start()].count('\n') + 1
        line = content.split('\n')[line_num - 1].strip()
        results['assessment_number_patterns'].append(f"Line {line_num}: {line}")
    
    # Find assessment_id patterns
    assessment_id_matches = re.finditer(r'assessment_id', content)
    for match in assessment_id_matches:
        line_num = content[:match.start()].count('\n') + 1
        line = content.split('\n')[line_num - 1].strip()
        results['assessment_id_patterns'].append(f"Line {line_num}: {line}")
    
    # Find route definitions
    route_matches = re.finditer(r'@app\.route\([\'"]([^\'\"]*)[\'"]', content)
    for match in route_matches:
        line_num = content[:match.start()].count('\n') + 1
        route_pattern = match.group(1)
        results['route_definitions'].append(f"Line {line_num}: {route_pattern}")
    
    # Find template variable usage
    template_var_matches = re.finditer(r'\{\{[^}]*assessment_[^}]*\}\}', content)
    for match in template_var_matches:
        line_num = content[:match.start()].count('\n') + 1
        var_usage = match.group(0)
        results['template_variables'].append(f"Line {line_num}: {var_usage}")
    
    # Find navigation URLs
    nav_matches = re.finditer(r'window\.location\.href\s*=\s*[\'"]([^\'\"]*)[\'"]', content)
    for match in nav_matches:
        line_num = content[:match.start()].count('\n') + 1
        url = match.group(1)
        results['navigation_urls'].append(f"Line {line_num}: {url}")
    
    # Find URL generation patterns
    url_for_matches = re.finditer(r'url_for\([\'"]([^\'\"]*)[\'"][^)]*\)', content)
    for match in url_for_matches:
        line_num = content[:match.start()].count('\n') + 1
        url_for_call = match.group(0)
        results['navigation_urls'].append(f"Line {line_num}: {url_for_call}")
    
    return results

def main():
    """Run the diagnostic."""
    print("ROUTING DIAGNOSTIC REPORT")
    print("=" * 50)
    
    # Files to analyze
    files_to_check = [
        'routes.py',
        'templates/assessments/speaking_start.html',
        'templates/assessments/conversational_speaking.html',
        'templates/assessments/speaking_assessment.html',
        'templates/assessments/speaking_selection.html',
        'templates/assessments/general_speaking_selection.html',
        'templates/assessments/academic_writing_selection.html',
        'templates/assessments/general_writing_selection.html',
        'assessment_assignment_service.py',
        'enhanced_nova_assessment.py'
    ]
    
    inconsistencies = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\nAnalyzing {file_path}:")
            print("-" * 30)
            
            results = analyze_file(file_path)
            
            if results['route_definitions']:
                print("Route Definitions:")
                for route in results['route_definitions']:
                    print(f"  {route}")
            
            if results['assessment_number_patterns']:
                print("Assessment Number Usage:")
                for pattern in results['assessment_number_patterns'][:5]:  # Limit output
                    print(f"  {pattern}")
            
            if results['assessment_id_patterns']:
                print("Assessment ID Usage:")
                for pattern in results['assessment_id_patterns'][:5]:  # Limit output
                    print(f"  {pattern}")
            
            if results['template_variables']:
                print("Template Variables:")
                for var in results['template_variables']:
                    print(f"  {var}")
            
            if results['navigation_urls']:
                print("Navigation URLs:")
                for url in results['navigation_urls']:
                    print(f"  {url}")
            
            # Check for inconsistencies
            has_number = bool(results['assessment_number_patterns'])
            has_id = bool(results['assessment_id_patterns'])
            
            if has_number and has_id:
                inconsistencies.append({
                    'file': file_path,
                    'issue': 'Mixed usage of assessment_number and assessment_id',
                    'details': f"Found {len(results['assessment_number_patterns'])} number refs and {len(results['assessment_id_patterns'])} id refs"
                })
        else:
            print(f"File not found: {file_path}")
    
    print("\n\nINCONSISTENCY SUMMARY")
    print("=" * 50)
    
    if inconsistencies:
        for issue in inconsistencies:
            print(f"❌ {issue['file']}: {issue['issue']}")
            print(f"   {issue['details']}")
    else:
        print("✅ No mixed usage detected in analyzed files")
    
    print("\nROUTE PATTERN ANALYSIS")
    print("=" * 50)
    
    # Analyze route patterns specifically
    route_patterns = {
        'assessment_number_routes': [],
        'assessment_id_routes': []
    }
    
    if os.path.exists('routes.py'):
        with open('routes.py', 'r') as f:
            content = f.read()
        
        # Find all route patterns
        route_matches = re.finditer(r'@app\.route\([\'"]([^\'\"]*)[\'"].*?\ndef\s+(\w+)', content, re.DOTALL)
        for match in route_matches:
            route_pattern = match.group(1)
            function_name = match.group(2)
            
            if 'assessment_number' in route_pattern:
                route_patterns['assessment_number_routes'].append(f"{function_name}: {route_pattern}")
            elif 'assessment_id' in route_pattern:
                route_patterns['assessment_id_routes'].append(f"{function_name}: {route_pattern}")
    
    print("Routes using assessment_number:")
    for route in route_patterns['assessment_number_routes']:
        print(f"  {route}")
    
    print("\nRoutes using assessment_id:")
    for route in route_patterns['assessment_id_routes']:
        print(f"  {route}")
    
    print("\nRECOMMENDATIONS")
    print("=" * 50)
    print("1. Use assessment_number (1-4) for user-facing assessment selection")
    print("2. Use assessment_id (database ID) for actual assessment execution")
    print("3. Convert between them in route handlers as needed")
    print("4. Ensure templates receive the correct variable type")

if __name__ == "__main__":
    main()