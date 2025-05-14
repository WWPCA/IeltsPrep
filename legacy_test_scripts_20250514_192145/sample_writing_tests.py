from main import app
from models import db, PracticeTest
import json

with app.app_context():
    # Get some sample academic writing tests
    academic_tests = PracticeTest.query.filter_by(test_type='writing', ielts_test_type='academic').limit(5).all()
    
    print("ACADEMIC WRITING TESTS EXAMPLES:")
    for test in academic_tests:
        print(f"\nTest ID: {test.id}, Title: {test.title}")
        try:
            print(f"Raw Questions: {test._questions[:150]}...")  # Print first 150 chars
        except Exception as e:
            print(f"Error accessing questions: {str(e)}")
    
    # Get some sample general writing tests
    general_tests = PracticeTest.query.filter_by(test_type='writing', ielts_test_type='general').limit(5).all()
    
    print("\n\nGENERAL WRITING TESTS EXAMPLES:")
    for test in general_tests:
        print(f"\nTest ID: {test.id}, Title: {test.title}")
        try:
            print(f"Raw Questions: {test._questions[:150]}...")  # Print first 150 chars
        except Exception as e:
            print(f"Error accessing questions: {str(e)}")
