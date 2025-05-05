"""
Check the current state of the test database and identify gaps.
"""
from app import app, db
from models import PracticeTest, CompletePracticeTest

def check_test_database():
    """Check the current state of the test database and identify gaps."""
    with app.app_context():
        # Count all test types
        print("==== TEST DATABASE ANALYSIS ====")
        
        # Complete Tests
        academic_complete = CompletePracticeTest.query.filter_by(ielts_test_type='academic').count()
        general_complete = CompletePracticeTest.query.filter_by(ielts_test_type='general').count()
        print(f"\nComplete Practice Tests:")
        print(f"Academic: {academic_complete}")
        print(f"General: {general_complete}")
        
        # Reading Tests
        academic_reading = PracticeTest.query.filter_by(test_type='reading', ielts_test_type='academic').count()
        general_reading = PracticeTest.query.filter_by(test_type='reading', ielts_test_type='general').count()
        print(f"\nReading Tests:")
        print(f"Academic: {academic_reading}")
        print(f"General: {general_reading}")
        
        # Listening Tests (same for both academic and general)
        listening_tests = PracticeTest.query.filter_by(test_type='listening').count()
        print(f"\nListening Tests: {listening_tests}")
        
        # Writing Tests - Task 1
        academic_writing_task1 = PracticeTest.query.filter_by(
            test_type='writing', 
            ielts_test_type='academic',
            section=1
        ).count()
        general_writing_task1 = PracticeTest.query.filter_by(
            test_type='writing', 
            ielts_test_type='general',
            section=1
        ).count()
        print(f"\nWriting Tests - Task 1:")
        print(f"Academic: {academic_writing_task1}")
        print(f"General: {general_writing_task1}")
        
        # Writing Tests - Task 2
        academic_writing_task2 = PracticeTest.query.filter_by(
            test_type='writing', 
            ielts_test_type='academic',
            section=2
        ).count()
        general_writing_task2 = PracticeTest.query.filter_by(
            test_type='writing', 
            ielts_test_type='general',
            section=2
        ).count()
        print(f"\nWriting Tests - Task 2:")
        print(f"Academic: {academic_writing_task2}")
        print(f"General: {general_writing_task2}")
        
        # Speaking Tests
        speaking_tests = PracticeTest.query.filter_by(test_type='speaking').count()
        print(f"\nSpeaking Tests: {speaking_tests}")
        
        # Identify gaps
        print("\n==== GAPS IDENTIFIED ====")
        
        if academic_complete < 16:
            print(f"MISSING: {16 - academic_complete} more Academic complete tests needed (target: 16)")
        
        if general_complete < 16:
            print(f"MISSING: {16 - general_complete} more General Training complete tests needed (target: 16)")
            
        if academic_reading < 16:
            print(f"MISSING: {16 - academic_reading} more Academic reading tests needed (target: 16)")
            
        if general_reading < 16:
            print(f"MISSING: {16 - general_reading} more General Training reading tests needed (target: 16)")
            
        if listening_tests < 16:
            print(f"MISSING: {16 - listening_tests} more listening tests needed (target: 16)")
            
        if academic_writing_task1 < 16:
            print(f"MISSING: {16 - academic_writing_task1} more Academic writing Task 1 tests needed (target: 16)")
            
        if general_writing_task1 < 16:
            print(f"MISSING: {16 - general_writing_task1} more General Training writing Task 1 tests needed (target: 16)")
            
        if academic_writing_task2 < 16:
            print(f"MISSING: {16 - academic_writing_task2} more Academic writing Task 2 tests needed (target: 16)")
            
        if general_writing_task2 < 16:
            print(f"MISSING: {16 - general_writing_task2} more General Training writing Task 2 tests needed (target: 16)")
            
        if speaking_tests < 16:
            print(f"MISSING: {16 - speaking_tests} more speaking tests needed (target: 16)")
            
        if not any([
            academic_complete < 16, general_complete < 16,
            academic_reading < 16, general_reading < 16,
            listening_tests < 16,
            academic_writing_task1 < 16, general_writing_task1 < 16,
            academic_writing_task2 < 16, general_writing_task2 < 16,
            speaking_tests < 16
        ]):
            print("No gaps identified! All test types have at least 16 tests.")
        
        # List a few sample questions of each type for review
        print("\n==== SAMPLE TEST QUESTIONS ====")
        
        # Sample Academic Reading
        academic_reading_sample = PracticeTest.query.filter_by(
            test_type='reading', 
            ielts_test_type='academic'
        ).first()
        
        if academic_reading_sample:
            print("\nSample Academic Reading Test:")
            print(f"Title: {academic_reading_sample.title}")
            print(f"Question data type: {type(academic_reading_sample.questions)}")
            if isinstance(academic_reading_sample.questions, list) and academic_reading_sample.questions:
                print(f"Number of question items: {len(academic_reading_sample.questions)}")
            else:
                print("Questions data is not in the expected list format")
        
        # Sample General Reading
        general_reading_sample = PracticeTest.query.filter_by(
            test_type='reading', 
            ielts_test_type='general'
        ).first()
        
        if general_reading_sample:
            print("\nSample General Reading Test:")
            print(f"Title: {general_reading_sample.title}")
            print(f"Question data type: {type(general_reading_sample.questions)}")
            if isinstance(general_reading_sample.questions, list) and general_reading_sample.questions:
                print(f"Number of question items: {len(general_reading_sample.questions)}")
            else:
                print("Questions data is not in the expected list format")

if __name__ == "__main__":
    check_test_database()