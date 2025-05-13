from main import app
from routes import *

# Add the test details route function
def test_details_route(test_type, test_id):
    """Show details about a test before starting it"""
    if test_type not in ['listening', 'reading', 'writing', 'speaking']:
        abort(404)
    
    test = None
    try:
        test = PracticeTest.query.get_or_404(test_id)
    except (NameError, AttributeError):
        # This is a fallback if PracticeTest is not defined
        test = Assessment.query.get_or_404(test_id)
    
    # All tests require an assessment package
    if not current_user.has_active_assessment_package():
        flash('This test requires an assessment package. Please purchase an assessment package to access all practice tests.', 'warning')
        return redirect(url_for('assessment_products_page'))
    
    # Check if user has already taken this test during current assessment package period
    has_taken = False
    if hasattr(current_user, 'has_taken_test'):
        has_taken = current_user.has_taken_test(test_id, test_type)
    elif hasattr(current_user, 'has_taken_assessment'):
        has_taken = current_user.has_taken_assessment(test_id, test_type)
    
    if has_taken:
        flash('You have already taken this test during your current assessment package period. Each test can only be taken once per assessment package.', 'warning')
        return redirect(url_for('practice_test_list', test_type=test_type))
    
    return render_template('practice/test_details.html', 
                          title=f'IELTS {test_type.capitalize()} Practice',
                          test=test,
                          test_type=test_type)

# Add the route to the app
app.add_url_rule('/practice/<test_type>/<int:test_id>/details', 
                 'test_details', 
                 test_details_route, 
                 methods=['GET'])

# Print confirmation
print("Added test_details route to the application.")