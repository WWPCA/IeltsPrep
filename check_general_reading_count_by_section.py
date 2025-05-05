"""
Check the number of General Training Reading tests by section.
"""
from app import app
from models import PracticeTest

def check_general_reading_by_section():
    """Check the number of General Training Reading tests by section."""
    with app.app_context():
        print("General Reading Tests by Section:")
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
            
            print(f"  {section_name}: {count} tests")
        
        total = PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general'
        ).count()
        
        print(f"\nTotal General Reading Tests: {total}")

if __name__ == "__main__":
    check_general_reading_by_section()