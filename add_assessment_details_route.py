"""
Assessment Details Route Module
Provides route for displaying assessment details before starting
"""

from flask import render_template, abort, session
from flask_login import login_required, current_user
from assessment_assignment_service import has_package_access

def assessment_details_route(assessment_type, assessment_id):
    """Show details about an assessment before starting it"""
    
    # Validate assessment type
    valid_types = ['academic_speaking', 'general_speaking', 'academic_writing', 'general_writing']
    if assessment_type not in valid_types:
        abort(404)
    
    # Check if user has access to this assessment type
    if not has_package_access(current_user.id, assessment_type.replace('_', ' ').title()):
        abort(403)
    
    # Assessment details for display
    assessment_details = {
        'academic_speaking': {
            'title': 'Academic Speaking Assessment',
            'description': 'IELTS Academic Speaking practice with AI examiner Maya',
            'duration': '11-14 minutes',
            'parts': ['Part 1: Introduction (4-5 min)', 'Part 2: Long Turn (3-4 min)', 'Part 3: Discussion (4-5 min)']
        },
        'general_speaking': {
            'title': 'General Training Speaking Assessment',
            'description': 'IELTS General Training Speaking practice with AI examiner Maya',
            'duration': '11-14 minutes',
            'parts': ['Part 1: Introduction (4-5 min)', 'Part 2: Long Turn (3-4 min)', 'Part 3: Discussion (4-5 min)']
        },
        'academic_writing': {
            'title': 'Academic Writing Assessment',
            'description': 'IELTS Academic Writing evaluation with detailed feedback',
            'duration': '60 minutes',
            'parts': ['Task 1: Data Description (20 min)', 'Task 2: Essay Writing (40 min)']
        },
        'general_writing': {
            'title': 'General Training Writing Assessment',
            'description': 'IELTS General Training Writing evaluation with detailed feedback',
            'duration': '60 minutes',
            'parts': ['Task 1: Letter Writing (20 min)', 'Task 2: Essay Writing (40 min)']
        }
    }
    
    details = assessment_details.get(assessment_type)
    if not details:
        abort(404)
    
    return render_template('assessment_details.html', 
                         assessment_type=assessment_type,
                         assessment_id=assessment_id,
                         details=details)