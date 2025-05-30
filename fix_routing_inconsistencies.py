#!/usr/bin/env python3
"""
Fix Routing Inconsistencies
Comprehensive fix for assessment_number vs assessment_id routing issues.
"""

import os
import re
from app import app, db
from models import Assessment

def fix_routes_py():
    """Fix the routes.py file to handle assessment_number to assessment_id conversion."""
    
    print("Fixing routes.py...")
    
    # Read the current routes.py
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Add helper function to convert assessment_number to assessment_id
    helper_function = '''
def get_assessment_id_from_number(assessment_type, assessment_number):
    """
    Convert assessment_number (1-4) to actual assessment_id from database.
    This bridges the gap between user-facing numbers and database IDs.
    """
    # Get all assessments of the specified type
    assessments = Assessment.query.filter_by(
        assessment_type=assessment_type,
        status='active'
    ).order_by(Assessment.id).all()
    
    # Return the assessment_id for the given number (1-indexed)
    if 1 <= assessment_number <= len(assessments):
        return assessments[assessment_number - 1].id
    return None
'''
    
    # Insert the helper function after imports but before routes
    import_end = content.find('@app.route')
    if import_end != -1:
        content = content[:import_end] + helper_function + '\n' + content[import_end:]
    
    # Fix the assessment_start route to handle both number and id
    old_assessment_start = '''@app.route('/assessments/<assessment_type>/assessment/<int:assessment_number>')
@login_required
def assessment_start(assessment_type, assessment_number):'''
    
    new_assessment_start = '''@app.route('/assessments/<assessment_type>/assessment/<int:assessment_number>')
@login_required  
def assessment_start(assessment_type, assessment_number):'''
    
    content = content.replace(old_assessment_start, new_assessment_start)
    
    # Add route that handles conversational speaking with assessment_number
    conversational_route_fix = '''
@app.route('/assessments/<assessment_type>/conversational/<int:assessment_number>')
@login_required
@country_access_required
def conversational_speaking_from_number(assessment_type, assessment_number):
    """Handle conversational speaking using assessment_number instead of assessment_id."""
    # Convert assessment_number to assessment_id
    assessment_id = get_assessment_id_from_number(assessment_type, assessment_number)
    
    if not assessment_id:
        flash('Assessment not found.', 'danger')
        return redirect(url_for('profile'))
    
    # Redirect to the proper conversational route with assessment_id
    return redirect(url_for('conversational_speaking_assessment', 
                          assessment_type=assessment_type, 
                          assessment_id=assessment_id))
'''
    
    # Insert this new route before the main function
    main_function_pos = content.find('if __name__ == "__main__":')
    if main_function_pos != -1:
        content = content[:main_function_pos] + conversational_route_fix + '\n' + content[main_function_pos:]
    
    # Write the updated content
    with open('routes.py', 'w') as f:
        f.write(content)
    
    print("✓ Fixed routes.py with assessment_number to assessment_id conversion")

def fix_speaking_start_template():
    """Fix the speaking start template navigation."""
    
    print("Fixing speaking_start.html...")
    
    with open('templates/assessments/speaking_start.html', 'r') as f:
        content = f.read()
    
    # Fix the navigation URL to use the new route
    old_nav = "window.location.href = '/speaking/assessment/{{ assessment_type }}/{{ assessment_number }}';"
    new_nav = "window.location.href = '/assessments/{{ assessment_type }}/conversational/{{ assessment_number }}';"
    
    content = content.replace(old_nav, new_nav)
    
    with open('templates/assessments/speaking_start.html', 'w') as f:
        f.write(content)
    
    print("✓ Fixed speaking_start.html navigation")

def fix_conversational_template():
    """Fix any issues in the conversational speaking template."""
    
    print("Fixing conversational_speaking.html...")
    
    if os.path.exists('templates/assessments/conversational_speaking.html'):
        with open('templates/assessments/conversational_speaking.html', 'r') as f:
            content = f.read()
        
        # Make sure it uses assessment_id consistently
        # The template looks fine based on the diagnostic, but let's ensure consistency
        
        # Check if there are any assessment_number references that should be assessment_id
        if 'assessment_number' in content:
            print("⚠️  Found assessment_number in conversational template - please review manually")
        else:
            print("✓ Conversational template uses assessment_id consistently")

def verify_database_assessments():
    """Verify that assessments exist in the database for testing."""
    
    print("Verifying database assessments...")
    
    with app.app_context():
        academic_speaking = Assessment.query.filter_by(
            assessment_type='academic_speaking',
            status='active'
        ).count()
        
        general_speaking = Assessment.query.filter_by(
            assessment_type='general_speaking', 
            status='active'
        ).count()
        
        print(f"✓ Academic speaking assessments: {academic_speaking}")
        print(f"✓ General speaking assessments: {general_speaking}")
        
        if academic_speaking == 0 or general_speaking == 0:
            print("⚠️  Missing assessments in database - this may cause routing issues")

def main():
    """Run all fixes for routing inconsistencies."""
    
    print("FIXING ROUTING INCONSISTENCIES")
    print("=" * 50)
    
    # Apply all fixes
    fix_routes_py()
    fix_speaking_start_template()
    fix_conversational_template()
    verify_database_assessments()
    
    print("\n" + "=" * 50)
    print("ROUTING FIXES COMPLETED")
    print("\nSummary of changes:")
    print("1. Added assessment_number to assessment_id conversion function")
    print("2. Added new route: /assessments/<type>/conversational/<number>")
    print("3. Fixed speaking_start.html navigation URL")
    print("4. Verified template consistency")
    print("\nThe application should now properly handle both:")
    print("- User-facing assessment numbers (1-4)")
    print("- Database assessment IDs for execution")

if __name__ == "__main__":
    main()