import os
import re

def remove_route_functions(file_path, route_patterns):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Keep track of original line count
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
    
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Removed {lines_removed} lines containing deprecated test/practice routes from {file_path}")
    return lines_removed

if __name__ == "__main__":
    routes_file = "routes.py"
    
    # List of route patterns to remove (these are now handled by assessment routes)
    route_patterns = [
        '/practice/(?!session)', # All practice routes except session-related ones
        '/test-day',
        '/api/submit-test'
    ]
    
    if os.path.exists(routes_file):
        lines_removed = remove_route_functions(routes_file, route_patterns)
        print(f"Clean-up complete: {lines_removed} lines removed.")
    else:
        print(f"Error: {routes_file} not found!")