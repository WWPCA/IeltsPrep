from main import app
from models import db, PracticeTest

with app.app_context():
    writing_tests = PracticeTest.query.filter_by(test_type='writing').all()
    
    print('Academic Writing Tests:')
    academic = [t for t in writing_tests if t.ielts_test_type == 'academic']
    print(f'Total: {len(academic)}')
    
    # Get unique formats/types
    academic_types = {}
    for test in academic:
        if test.questions and 'task_type' in test.questions:
            task_type = test.questions['task_type']
            if task_type not in academic_types:
                academic_types[task_type] = 0
            academic_types[task_type] += 1
    
    print('Academic Writing Task Types:')
    for task_type, count in academic_types.items():
        print(f'- {task_type}: {count} tests')
    
    print('\nGeneral Writing Tests:')
    general = [t for t in writing_tests if t.ielts_test_type == 'general']
    print(f'Total: {len(general)}')
    
    # Get unique formats/types
    general_types = {}
    for test in general:
        if test.questions and 'task_type' in test.questions:
            task_type = test.questions['task_type']
            if task_type not in general_types:
                general_types[task_type] = 0
            general_types[task_type] += 1
    
    print('General Writing Task Types:')
    for task_type, count in general_types.items():
        print(f'- {task_type}: {count} tests')
