"""
Check the structure of existing tests to understand the format.
"""
import json
from app import app, db
from models import PracticeTest

def print_model_details(model):
    """Print all attributes and details of a model."""
    print(f"\nModel type: {type(model).__name__}")
    print(f"Model ID: {model.id}")
    
    # Get all model attributes
    for key in dir(model):
        # Skip internal attributes and methods
        if key.startswith('_') or callable(getattr(model, key)):
            continue
            
        value = getattr(model, key)
        
        # Pretty-print JSON attributes
        if key.startswith('_') and hasattr(model, key.lstrip('_')):
            # This is likely a JSON field with a property accessor
            continue
        
        if isinstance(value, (dict, list)):
            try:
                print(f"\n{key}:")
                print(json.dumps(value, indent=2))
            except (TypeError, json.JSONDecodeError):
                print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")

def check_test_structure():
    """Check the structure of existing tests."""
    with app.app_context():
        # Get one example of each test type
        academic_reading = PracticeTest.query.filter_by(test_type='reading', ielts_test_type='academic').first()
        general_reading = PracticeTest.query.filter_by(test_type='reading', ielts_test_type='general').first()
        academic_writing_task1 = PracticeTest.query.filter_by(test_type='writing', ielts_test_type='academic', section=1).first()
        general_writing_task1 = PracticeTest.query.filter_by(test_type='writing', ielts_test_type='general', section=1).first()
        
        print("===== ACADEMIC READING TEST =====")
        if academic_reading:
            print_model_details(academic_reading)
        else:
            print("No academic reading test found.")
            
        print("\n\n===== GENERAL READING TEST =====")
        if general_reading:
            print_model_details(general_reading)
        else:
            print("No general reading test found.")
            
        print("\n\n===== ACADEMIC WRITING TASK 1 =====")
        if academic_writing_task1:
            print_model_details(academic_writing_task1)
        else:
            print("No academic writing task 1 found.")
            
        print("\n\n===== GENERAL WRITING TASK 1 =====")
        if general_writing_task1:
            print_model_details(general_writing_task1)
        else:
            print("No general writing task 1 found.")

if __name__ == "__main__":
    check_test_structure()