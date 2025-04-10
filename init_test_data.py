from app import app, db
from models import TestStructure

def init_test_structure():
    """Initialize the test structure data in the database."""
    with app.app_context():
        # Clear existing test structure data
        TestStructure.query.delete()
        
        # Test structure data for different IELTS test types
        test_data = [
            {
                "test_type": "academic",
                "description": "For study at undergraduate or postgraduate levels, and for professional registration.",
                "format_details": """The IELTS Academic test has four sections:
- Listening (30 minutes + 10 minutes transfer time)
- Reading (60 minutes) with academic texts
- Writing (60 minutes) with Task 1 requiring description of visual information and Task 2 requiring an essay
- Speaking (11-14 minutes) face-to-face interview"""
            },
            {
                "test_type": "general_training",
                "description": "For work, migration, or training programs in English-speaking environments.",
                "format_details": """The IELTS General Training test has four sections:
- Listening (30 minutes + 10 minutes transfer time)
- Reading (60 minutes) with everyday texts
- Writing (60 minutes) with Task 1 requiring a letter and Task 2 requiring an essay
- Speaking (11-14 minutes) face-to-face interview"""
            },
            {
                "test_type": "ukvi",
                "description": "A Secure English Language Test (SELT) approved by UK Visas and Immigration.",
                "format_details": """The IELTS for UKVI test follows the same format as the Academic or General Training tests but is taken at UKVI approved test centers. It includes:
- Listening (30 minutes + 10 minutes transfer time)
- Reading (60 minutes)
- Writing (60 minutes)
- Speaking (11-14 minutes)"""
            },
            {
                "test_type": "life_skills",
                "description": "Specifically designed for UK visa applications for 'family of a settled person' and 'settlement' categories.",
                "format_details": """IELTS Life Skills only tests speaking and listening abilities:
- Available at levels A1, B1
- Format: Face-to-face speaking and listening test with an examiner and another test taker
- Duration: 16-22 minutes"""
            },
            {
                "test_type": "online",
                "description": "Take the IELTS Academic test remotely from the comfort of your home.",
                "format_details": """The IELTS Online test follows the same format as the in-person Academic test:
- Listening (30 minutes + 10 minutes transfer time)
- Reading (60 minutes)
- Writing (60 minutes)
- Speaking (15-20 minutes) conducted via video call
- Results available in 3-6 days"""
            }
        ]
        
        # Add all test structure data
        for data in test_data:
            test_structure = TestStructure(**data)
            db.session.add(test_structure)
        
        # Commit changes
        db.session.commit()
        print(f"Added {len(test_data)} test structure entries")

if __name__ == "__main__":
    init_test_structure()