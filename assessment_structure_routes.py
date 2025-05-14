"""
Assessment Structure Routes Module
This module provides routes for displaying the structure of IELTS Assessments.
"""

from main import app
from flask import render_template, redirect, url_for


@app.route('/assessment-structure')
def assessment_structure():
    """Display the assessment structure landing page."""
    return render_template('assessment_structure/index.html', 
                          title='IELTS Assessment Structure')


@app.route('/assessment-structure/academic')
def assessment_structure_academic():
    """Display the Academic assessment structure."""
    return render_template('assessment_structure/academic.html', 
                          title='Academic IELTS Assessment Structure')


@app.route('/assessment-structure/general-training')
def assessment_structure_general_training():
    """Display the General Training assessment structure."""
    return render_template('assessment_structure/general_training.html', 
                          title='General Training IELTS Assessment Structure')


# Add detail route for individual assessment types
@app.route('/assessment-structure/<assessment_type>')
def assessment_structure_detail(assessment_type):
    """Display details for a specific assessment type."""
    if assessment_type == 'academic':
        return assessment_structure_academic()
    elif assessment_type == 'general_training':
        return assessment_structure_general_training()
    else:
        return redirect(url_for('assessment_structure'))

print("Assessment structure routes added successfully.")