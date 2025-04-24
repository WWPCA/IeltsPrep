import re

def remove_duplicate_defs(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Find repeated "def function_name" lines and replace them with a single def line
    pattern = r'def ([a-zA-Z0-9_]+)(\s*\([^)]*\):)(?:\s*def \1)*'
    fixed_content = re.sub(pattern, r'def \1\2', content)
    
    with open(output_file, 'w') as f:
        f.write(fixed_content)

# Fix routes.py
remove_duplicate_defs('routes.py', 'routes.py.fixed')
import os
os.rename('routes.py.fixed', 'routes.py')
print("File fixed successfully!")
