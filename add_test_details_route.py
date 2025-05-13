from main import app
from routes import *

# Add the test details route function
def test_details_route(test_type, test_id):
    """Show details about a test before starting it"""
    if test_type not in ['listening', 'reading', 'writing']:
        abort(404)
    
    test = PracticeTest.query.get_or_404(test_id)
    
    # All assessments require an assessment package
    if not current_user.has_active_assessment_package():
        flash('This assessment requires an assessment package. Please purchase an assessment package to access GenAI-powered skill evaluations.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already used this assessment during current assessment package period
    if current_user.has_taken_test(test_id, test_type):
        flash('You have already used this assessment during your current assessment package period. Each assessment can only be used once per assessment package.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    return render_template('assessment/details.html', 
                          title=f'IELTS {test_type.capitalize()} Assessment',
                          test=test,
                          test_type=test_type)

# Add the route to the app
app.add_url_rule('/assessment/<test_type>/<int:test_id>/details', 
                 'assessment_details', 
                 test_details_route, 
                 methods=['GET'])

# Print confirmation
print("Added assessment_details route to the application.")