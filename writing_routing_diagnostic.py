#!/usr/bin/env python3
"""
Writing Assessment Routing Diagnostic
Identifies routing inconsistencies in writing assessment flows.
"""

import os
import re

def analyze_writing_routes():
    """Analyze writing-specific routes and templates."""
    
    print("WRITING ASSESSMENT ROUTING DIAGNOSTIC")
    print("=" * 50)
    
    # Files to check for writing assessments
    writing_files = [
        'routes.py',
        'templates/assessments/writing_start.html',
        'templates/assessments/writing_assessment.html', 
        'templates/assessments/academic_writing_selection.html',
        'templates/assessments/general_writing_selection.html',
        'writing_assessment_routes.py'
    ]
    
    writing_routes = []
    writing_issues = []
    
    for file_path in writing_files:
        if os.path.exists(file_path):
            print(f"\nAnalyzing {file_path}:")
            print("-" * 30)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find writing-related routes
            route_matches = re.finditer(r'@app\.route\([\'"]([^\'\"]*writing[^\'\"]*)[\'"]', content)
            for match in route_matches:
                line_num = content[:match.start()].count('\n') + 1
                route_pattern = match.group(1)
                writing_routes.append(f"{file_path} Line {line_num}: {route_pattern}")
                print(f"  Route: {route_pattern}")
            
            # Check for assessment_number vs assessment_id usage
            number_count = len(re.findall(r'assessment_number', content))
            id_count = len(re.findall(r'assessment_id', content))
            
            if number_count > 0 and id_count > 0:
                writing_issues.append(f"{file_path}: Mixed usage ({number_count} number, {id_count} id)")
                print(f"  ⚠️  Mixed usage: {number_count} assessment_number, {id_count} assessment_id")
            elif number_count > 0:
                print(f"  ✓ Uses assessment_number ({number_count} times)")
            elif id_count > 0:
                print(f"  ✓ Uses assessment_id ({id_count} times)")
            
            # Find navigation patterns
            nav_matches = re.finditer(r'window\.location\.href\s*=\s*[\'"]([^\'\"]*)[\'"]', content)
            for match in nav_matches:
                line_num = content[:match.start()].count('\n') + 1
                url = match.group(1)
                if 'writing' in url:
                    print(f"  Navigation: {url}")
            
            # Find url_for patterns for writing
            url_for_matches = re.finditer(r'url_for\([\'"]([^\'\"]*writing[^\'\"]*)[\'"]', content)
            for match in url_for_matches:
                line_num = content[:match.start()].count('\n') + 1
                url_for_call = match.group(1)
                print(f"  URL generation: {url_for_call}")
        
        else:
            print(f"File not found: {file_path}")
    
    print(f"\n\nWRITING ROUTES SUMMARY")
    print("=" * 50)
    
    if writing_routes:
        print("Writing-related routes found:")
        for route in writing_routes:
            print(f"  {route}")
    else:
        print("❌ No writing-specific routes found")
    
    print(f"\nISSUES DETECTED")
    print("=" * 20)
    if writing_issues:
        for issue in writing_issues:
            print(f"❌ {issue}")
    else:
        print("✅ No mixed assessment_number/assessment_id usage detected")

def check_writing_flow_consistency():
    """Check if writing assessment flow is consistent."""
    
    print(f"\n\nWRITING FLOW CONSISTENCY CHECK")
    print("=" * 50)
    
    # Check if writing selection pages link properly
    selection_files = [
        'templates/assessments/academic_writing_selection.html',
        'templates/assessments/general_writing_selection.html'
    ]
    
    for file_path in selection_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            print(f"\nChecking {file_path}:")
            
            # Find assessment links
            link_matches = re.finditer(r'href="([^"]*assessment[^"]*)"', content)
            for match in link_matches:
                link = match.group(1)
                print(f"  Assessment link: {link}")
                
                # Check if it uses assessment_number correctly
                if 'assessment_number' in link:
                    print(f"    ✓ Uses assessment_number")
                elif 'assessment_id' in link:
                    print(f"    ⚠️  Uses assessment_id (may need conversion)")

def analyze_writing_start_template():
    """Analyze the writing start template specifically."""
    
    print(f"\n\nWRITING START TEMPLATE ANALYSIS")
    print("=" * 50)
    
    writing_start_path = 'templates/assessments/writing_start.html'
    
    if os.path.exists(writing_start_path):
        with open(writing_start_path, 'r') as f:
            content = f.read()
        
        print("Checking writing_start.html:")
        
        # Check for navigation patterns
        nav_patterns = [
            r'window\.location\.href\s*=\s*[\'"]([^\'\"]*)[\'"]',
            r'action="([^"]*)"',
            r'href="([^"]*)"'
        ]
        
        for pattern in nav_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                url = match.group(1)
                if 'assessment' in url or 'writing' in url:
                    line_num = content[:match.start()].count('\n') + 1
                    print(f"  Line {line_num}: {url}")
        
        # Check template variables
        var_matches = re.finditer(r'\{\{[^}]*assessment_[^}]*\}\}', content)
        for match in var_matches:
            var = match.group(0)
            line_num = content[:match.start()].count('\n') + 1
            print(f"  Variable Line {line_num}: {var}")
    
    else:
        print("❌ writing_start.html not found")

def main():
    """Run the writing assessment diagnostic."""
    analyze_writing_routes()
    check_writing_flow_consistency()
    analyze_writing_start_template()
    
    print(f"\n\nRECOMMENDATIONS FOR WRITING ASSESSMENTS")
    print("=" * 50)
    print("1. Ensure writing assessments use same number/id conversion as speaking")
    print("2. Check that writing_start.html navigates to correct writing interface")
    print("3. Verify writing selection pages use assessment_number consistently")
    print("4. Consider creating writing-specific conversational route if needed")

if __name__ == "__main__":
    main()