"""
Check the content of speaking test questions in the database.
"""
from app import app
from models import PracticeTest
import json

def check_speaking_test_questions():
    """Check the content of speaking test questions."""
    with app.app_context():
        # Get a sample of speaking tests
        academic_tests = PracticeTest.query.filter_by(
            test_type='speaking',
            ielts_test_type='academic'
        ).limit(2).all()
        
        general_tests = PracticeTest.query.filter_by(
            test_type='speaking',
            ielts_test_type='general'
        ).limit(2).all()
        
        # Display sample questions from each test type
        print("Sample Academic Speaking Test Questions:")
        for i, test in enumerate(academic_tests):
            print(f"\nTest: {test.title} (ID: {test.id})")
            try:
                questions = json.loads(test._questions)
                for j, q in enumerate(questions):
                    print(f"  Question {j+1}: {q.get('task', '')} - {q.get('description', '')[:100]}...")
            except:
                print("  Error: Could not parse questions")
        
        print("\nSample General Training Speaking Test Questions:")
        for i, test in enumerate(general_tests):
            print(f"\nTest: {test.title} (ID: {test.id})")
            try:
                questions = json.loads(test._questions)
                for j, q in enumerate(questions):
                    print(f"  Question {j+1}: {q.get('task', '')} - {q.get('description', '')[:100]}...")
            except:
                print("  Error: Could not parse questions")
        
        # Check for files that might contain speaking test data
        print("\nChecking for files containing speaking test data:")
        import os
        speaking_files = []
        for file in os.listdir('.'):
            if 'speak' in file.lower() and os.path.isfile(file):
                speaking_files.append(file)
        
        print(f"Found {len(speaking_files)} files that might contain speaking test data:")
        for file in speaking_files:
            print(f"- {file}")
            
        # Check for specific context files that might have been used
        context_files = [
            'IELTS Speaking Context File.xlsx',
            'IELTS Speaking Context File-CSV.csv',
            'ielts_speaking_Context_File.pdf'
        ]
        
        print("\nChecking for specific context files:")
        for file in context_files:
            if os.path.exists(f"attached_assets/{file}"):
                print(f"- Found: attached_assets/{file}")
            else:
                print(f"- Not found: attached_assets/{file}")

if __name__ == "__main__":
    check_speaking_test_questions()