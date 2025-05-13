from main import app
from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user
from models import Assessment

# Add the assessment details route function
def assessment_details_route(assessment_type, assessment_id):
    """Show details about an assessment before starting it"""
    if assessment_type not in ['listening', 'reading', 'writing']:
        abort(404)
    
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # All assessments require an assessment package
    if not current_user.has_active_assessment_package():
        flash('This assessment requires an assessment package. Please purchase an assessment package to access GenAI-powered skill evaluations.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already used this assessment during current assessment package period
    if current_user.has_taken_assessment(assessment_id, assessment_type):
        flash('You have already used this assessment during your current assessment package period. Each assessment can only be used once per assessment package.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    return render_template('assessment_details.html', 
                          title=f'IELTS {assessment_type.capitalize()} Assessment',
                          assessment=assessment,
                          assessment_type=assessment_type)

# Add the route to the app
app.add_url_rule('/assessment/<assessment_type>/<int:assessment_id>/details', 
                 'assessment_details', 
                 assessment_details_route, 
                 methods=['GET'])

# Print confirmation
print("Added assessment_details route to the application.")