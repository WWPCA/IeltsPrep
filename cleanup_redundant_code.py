#!/usr/bin/env python3
"""
Cleanup Redundant Code

This script removes redundant code and routes from the IELTS GenAI Prep application,
focusing on:
1. Removing deprecated test-related routes from routes.py
2. Archiving outdated script files
3. Consolidating assessment routes

Run this script to clean up the codebase and improve maintainability.
"""

import os
import re
import shutil
from datetime import datetime

def create_archive_directory():
    """Create an archive directory with timestamp for outdated files."""
    archive_dir = f"legacy_scripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created archive directory: {archive_dir}")
    return archive_dir

def move_files_to_archive(file_list, archive_dir):
    """Move specified files to the archive directory."""
    moved_count = 0
    for filename in file_list:
        if os.path.exists(filename):
            try:
                shutil.move(filename, os.path.join(archive_dir, filename))
                moved_count += 1
                print(f"Moved: {filename}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"File does not exist or already archived: {filename}")
    
    return moved_count

def remove_duplicate_defs(file_path):
    """
    Remove duplicate function definitions from routes files.
    This fixes issues where 'def function_name' appears multiple times.
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return 0
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Save original line count
    original_lines = content.count('\n')
    
    # Find repeated "def function_name" lines and replace them with a single def line
    pattern = r'def ([a-zA-Z0-9_]+)(\s*\([^)]*\):)(?:\s*def \1)*'
    fixed_content = re.sub(pattern, r'def \1\2', content)
    
    # Count lines after removal
    new_lines = fixed_content.count('\n')
    lines_removed = original_lines - new_lines
    
    if lines_removed > 0:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print(f"Removed {lines_removed} duplicate 'def' lines from {file_path}")
    else:
        print(f"No duplicate 'def' lines found in {file_path}")
    
    return lines_removed

def remove_deprecated_routes(file_path, route_patterns):
    """
    Remove deprecated route functions from routes.py.
    
    Args:
        file_path: Path to the routes file
        route_patterns: List of regex patterns matching routes to remove
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return 0
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Save original line count
    original_lines = content.count('\n')
    
    for pattern in route_patterns:
        # Find route function blocks
        # Format: @app.route('PATTERN') followed by function definition and content
        route_pattern = re.compile(
            rf'@app\.route\([\'"].*{pattern}.*[\'"]\).*?\n'
            rf'@?\w*.*?\n'
            rf'def .*?\).*?:.*?\n'
            rf'(?:(?!@app\.route|\ndef\s).*?\n)*',
            re.DOTALL
        )
        
        # Remove the matched routes
        content = route_pattern.sub('', content)
    
    # Count lines after removal
    new_lines = content.count('\n')
    lines_removed = original_lines - new_lines
    
    if lines_removed > 0:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Removed {lines_removed} lines containing deprecated routes from {file_path}")
    else:
        print(f"No deprecated routes found in {file_path}")
    
    return lines_removed

def cleanup_import_tryexcept_blocks(file_path):
    """
    Clean up try/except import blocks that are no longer needed.
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return 0
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Look for try/except import blocks
    original_lines = content.count('\n')
    
    # Pattern to match try/except blocks around imports that define fallback functions
    pattern = re.compile(
        r'try:\s*\n'
        r'\s*from\s+[a-zA-Z0-9_]+\s+import\s+[a-zA-Z0-9_]+\s*\n'
        r'except\s+ImportError:\s*\n'
        r'\s*#\s*Define\s+it\s+directly.*?\n'
        r'\s*def\s+[a-zA-Z0-9_]+\(.*?\):.*?\n'
        r'(?:(?!\n\s*@app\.route|\n\s*def\s|\n\s*try:|\n\n).*?\n)*',
        re.DOTALL
    )
    
    # Check if we have successful imports for these functions
    # If yes, replace the try/except block with just the import
    updated_content = content
    
    for match in pattern.finditer(content):
        block = match.group(0)
        import_line = re.search(r'\s*from\s+([a-zA-Z0-9_]+)\s+import\s+([a-zA-Z0-9_]+)', block)
        
        if import_line:
            module_name = import_line.group(1)
            function_name = import_line.group(2)
            
            # Check if the imported module exists
            module_path = f"{module_name}.py"
            if os.path.exists(module_path):
                # Replace the try/except block with just the import
                updated_content = updated_content.replace(
                    block, 
                    f"from {module_name} import {function_name}\n\n"
                )
    
    new_lines = updated_content.count('\n')
    lines_removed = original_lines - new_lines
    
    if content != updated_content:
        with open(file_path, 'w') as file:
            file.write(updated_content)
        print(f"Cleaned up try/except import blocks in {file_path}, removed {lines_removed} lines")
    else:
        print(f"No try/except import blocks to clean up in {file_path}")
    
    return lines_removed

def main():
    print("Starting redundant code cleanup...")
    
    # Create archive directory
    archive_dir = create_archive_directory()
    
    # List of outdated files to archive
    outdated_files = [
        "integrate_subscription_routes.py",  # Replaced by add_assessment_routes.py
        "update_subscription_routes.py",     # Replaced by update_assessment_product_routes.py
        "fix_routes.sh",                     # One-time fix, no longer needed
        "fix_routes_syntax.py",              # One-time fix, no longer needed
        "check_test_counter.py",             # Deprecated test-related script
        "update_test_counter.py",            # Deprecated test-related script
        "check_available_tests.py",          # Deprecated test-related script
    ]
    
    # Move outdated files to archive
    moved_count = move_files_to_archive(outdated_files, archive_dir)
    print(f"Archived {moved_count} outdated files")
    
    # Remove duplicate function definitions from routes.py
    routes_file = "routes.py"
    remove_duplicate_defs(routes_file)
    
    # List of route patterns to remove (these are handled by assessment routes now)
    deprecated_route_patterns = [
        '/practice/(?!session)',  # All practice routes except session-related ones
        '/test-day',              # Replaced by assessment structure routes
        '/api/submit-test',       # Replaced by assessment submission routes
        '/speaking-assessment',   # Replaced by speaking_assessment_routes.py
        '/writing-assessment',    # Replaced by writing_assessment_routes.py
    ]
    
    # Remove deprecated routes
    remove_deprecated_routes(routes_file, deprecated_route_patterns)
    
    # Clean up try/except import blocks
    cleanup_import_tryexcept_blocks(routes_file)
    
    print("Redundant code cleanup completed successfully!")

if __name__ == "__main__":
    main()