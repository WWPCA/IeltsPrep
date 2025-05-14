"""
Check the counts of all test types in detail.
"""
from app import app
from models import PracticeTest

def check_all_test_counts():
    """Check the counts of all test types in detail."""
    with app.app_context():
        # Academic tests
        print("ACADEMIC TESTS:")
        print("--------------")
        
        academic_reading = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='academic'
        ).count()
        
        academic_writing = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='academic'
        ).count()
        
        # Count Academic Writing by Task
        academic_writing_task1 = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='academic',
            section=1
        ).count()
        
        academic_writing_task2 = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='academic',
            section=2
        ).count()
        
        academic_speaking = PracticeTest.query.filter_by(
            test_type='speaking',
            ielts_test_type='academic'
        ).count()
        
        academic_listening = PracticeTest.query.filter_by(
            test_type='listening',
            ielts_test_type='academic'
        ).count()
        
        print(f"Reading: {academic_reading} tests")
        print(f"Writing: {academic_writing} tests total")
        print(f"  - Task 1: {academic_writing_task1} tests")
        print(f"  - Task 2: {academic_writing_task2} tests")
        print(f"Speaking: {academic_speaking} tests")
        print(f"Listening: {academic_listening} tests")
        
        # General tests
        print("\nGENERAL TRAINING TESTS:")
        print("----------------------")
        
        # Already checked General Reading in detail
        
        general_writing = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='general'
        ).count()
        
        # Count General Writing by Task
        general_writing_task1 = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='general',
            section=1
        ).count()
        
        general_writing_task2 = PracticeTest.query.filter_by(
            test_type='writing',
            ielts_test_type='general',
            section=2
        ).count()
        
        general_speaking = PracticeTest.query.filter_by(
            test_type='speaking',
            ielts_test_type='general'
        ).count()
        
        general_listening = PracticeTest.query.filter_by(
            test_type='listening',
            ielts_test_type='general'
        ).count()
        
        # Rerun the General Reading count by section
        print("Reading by Section:")
        for i in range(1, 8):
            count = PracticeTest.query.filter_by(
                test_type='reading',
                ielts_test_type='general',
                section=i
            ).count()
            
            section_name = {
                1: "Multiple Choice",
                2: "True/False/Not Given",
                3: "Matching Information",
                4: "Matching Features",
                5: "Summary Completion",
                6: "Note Completion",
                7: "Sentence Completion"
            }.get(i, f"Section {i}")
            
            print(f"  - {section_name}: {count} tests")
        
        general_reading_total = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).count()
        
        print(f"Reading: {general_reading_total} tests total")
        print(f"Writing: {general_writing} tests total")
        print(f"  - Task 1 (Letters): {general_writing_task1} tests")
        print(f"  - Task 2 (Essays): {general_writing_task2} tests")
        print(f"Speaking: {general_speaking} tests")
        print(f"Listening: {general_listening} tests")
        
        # Grand totals
        print("\nTOTAL TESTS IN DATABASE:")
        print("-----------------------")
        total_tests = PracticeTest.query.count()
        print(f"Total: {total_tests} tests")

if __name__ == "__main__":
    check_all_test_counts()