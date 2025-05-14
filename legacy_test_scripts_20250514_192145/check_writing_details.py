from main import app
from models import db, PracticeTest
import json

def analyze_test_questions(ielts_test_type):
    tests = PracticeTest.query.filter_by(test_type='writing', ielts_test_type=ielts_test_type).all()
    
    task_types = {}
    title_examples = {}
    
    for test in tests:
        try:
            questions = json.loads(test._questions)
            task_type = questions.get('task_type', 'Unknown')
            
            if task_type not in task_types:
                task_types[task_type] = 0
                title_examples[task_type] = []
                
            task_types[task_type] += 1
            
            if len(title_examples[task_type]) < 3:
                title_examples[task_type].append(test.title)
                
        except Exception as e:
            print(f"Error processing test {test.id}: {str(e)}")
    
    return task_types, title_examples

with app.app_context():
    print("Academic Writing Test Types:")
    academic_types, academic_examples = analyze_test_questions('academic')
    
    for task_type, count in academic_types.items():
        print(f"- {task_type}: {count} tests")
        print("  Examples:")
        for example in academic_examples[task_type]:
            print(f"  * {example}")
        print()
    
    print("\nGeneral Writing Test Types:")
    general_types, general_examples = analyze_test_questions('general')
    
    for task_type, count in general_types.items():
        print(f"- {task_type}: {count} tests")
        print("  Examples:")
        for example in general_examples[task_type]:
            print(f"  * {example}")
        print()
