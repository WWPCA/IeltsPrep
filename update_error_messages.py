"""
Update Error Messages to User-Friendly Format

This script updates all error messages in routes to be user-friendly
without exposing technical details.
"""

import re

def update_error_messages():
    """Update all error messages to be user-friendly"""
    
    # Read the current routes.py file
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Update error messages to be user-friendly
    updates = [
        # Change danger alerts to info
        (r"flash\('Invalid assessment type\.', 'danger'\)", 
         "flash('Assessment not found. Please start an assessment from your dashboard.', 'info')"),
        
        (r"flash\('You do not have access to this assessment type\. Please purchase an assessment package\.', 'danger'\)",
         "flash('You need to purchase an assessment package to access this feature.', 'info')"),
        
        # Already updated assessment not found messages - make sure they're consistent
        (r"flash\('Assessment not found\. Please start an assessment from your dashboard\.', 'danger'\)",
         "flash('Assessment not found. Please start an assessment from your dashboard.', 'info')"),
    ]
    
    for pattern, replacement in updates:
        content = re.sub(pattern, replacement, content)
    
    # Write the updated content back
    with open('routes.py', 'w') as f:
        f.write(content)
    
    print("Updated all error messages to be user-friendly")
    
    # Also update other route files
    update_assessment_details_route()
    update_writing_assessment_routes()

def update_assessment_details_route():
    """Update error messages in assessment details route"""
    try:
        with open('add_assessment_details_route.py', 'r') as f:
            content = f.read()
        
        # Update error messages
        updates = [
            (r"abort\(404\)", 
             "flash('Assessment not found. Please start an assessment from your dashboard.', 'info')\n        return redirect(url_for('profile'))"),
        ]
        
        for pattern, replacement in updates:
            content = re.sub(pattern, replacement, content)
        
        # Add import for flash and redirect if not present
        if 'from flask import' in content and 'flash' not in content:
            content = content.replace(
                'from flask import render_template, redirect, url_for, flash, abort',
                'from flask import render_template, redirect, url_for, flash'
            )
        
        with open('add_assessment_details_route.py', 'w') as f:
            f.write(content)
        
        print("Updated assessment details route error messages")
    except Exception as e:
        print(f"Note: Could not update assessment details route: {e}")

def update_writing_assessment_routes():
    """Update error messages in writing assessment routes"""
    try:
        with open('writing_assessment_routes.py', 'r') as f:
            content = f.read()
        
        # Update any technical error messages to be user-friendly
        updates = [
            (r"flash\('Invalid assessment type for this route\.', 'danger'\)",
             "flash('Assessment not found. Please start an assessment from your dashboard.', 'info')"),
            
            (r"flash\('You do not have permission to access this assessment attempt\.', 'danger'\)",
             "flash('Assessment not available. Please start an assessment from your dashboard.', 'info')"),
        ]
        
        for pattern, replacement in updates:
            content = re.sub(pattern, replacement, content)
        
        with open('writing_assessment_routes.py', 'w') as f:
            f.write(content)
        
        print("Updated writing assessment routes error messages")
    except Exception as e:
        print(f"Note: Could not update writing assessment routes: {e}")

if __name__ == '__main__':
    update_error_messages()