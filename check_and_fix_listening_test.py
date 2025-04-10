import json
from app import app, db
from models import PracticeTest

# Sample IELTS Listening test questions in the correct format
sample_questions = [
    {
        "number": "1-5",
        "instructions": "Complete the form below. Write NO MORE THAN THREE WORDS AND/OR A NUMBER for each answer.",
        "form_title": "STUDENT ACCOMMODATION REQUEST FORM",
        "form_fields": [
            {
                "field": "Name",
                "answer_key": "1"
            },
            {
                "field": "Contact Number",
                "answer_key": "2"
            },
            {
                "field": "Preferred Location",
                "answer_key": "3"
            },
            {
                "field": "Maximum Budget",
                "answer_key": "4"
            },
            {
                "field": "Move-in Date",
                "answer_key": "5"
            }
        ]
    },
    {
        "number": "6-10",
        "instructions": "Complete the table below. Write NO MORE THAN TWO WORDS for each answer.",
        "table_title": "ACCOMMODATION FACILITIES",
        "table_headers": ["Facility", "Location", "Opening Hours", "Notes"],
        "table_rows": [
            {
                "facility": "Laundry Room",
                "location": "Basement",
                "hours": "8:00 AM - 10:00 PM",
                "notes": "Bring ____ 6"
            },
            {
                "facility": "Gym",
                "location": "Third Floor",
                "hours": "____ 7",
                "notes": "Book in advance"
            },
            {
                "facility": "Study Area",
                "location": "____ 8",
                "hours": "24 hours",
                "notes": "Quiet zone"
            },
            {
                "facility": "Cafeteria",
                "location": "Ground Floor",
                "hours": "7:00 AM - 8:00 PM",
                "notes": "____ 9 available"
            },
            {
                "facility": "Recreation Room",
                "location": "Second Floor",
                "hours": "10:00 AM - 11:00 PM",
                "notes": "____ 10 allowed"
            }
        ]
    }
]

# Sample answers in JSON format
sample_answers = {
    "1": "Sarah Johnson",
    "2": "07700 900 123",
    "3": "Agios Nikolaos",
    "4": "£1000",
    "5": "June 15th",
    "6": "own detergent",
    "7": "6:00 AM - 9:00 PM",
    "8": "Fourth Floor",
    "9": "Vegetarian options",
    "10": "No loud music"
}

with app.app_context():
    # Check current listening test
    test = PracticeTest.query.filter_by(test_type='listening').first()
    
    if test:
        print(f"Current test: {test.title}")
        
        try:
            # Try to parse current questions to see if they're valid JSON
            current_questions = json.loads(test.questions)
            print("Current questions are valid JSON format")
            
            # Check if current question format matches our sample format
            if isinstance(current_questions, list) and len(current_questions) > 0 and "number" in current_questions[0]:
                print("Questions are already in the correct format")
            else:
                print("Questions format needs updating")
                # Update test with sample questions
                test.questions = json.dumps(sample_questions)
                test.answers = json.dumps(sample_answers)
                db.session.commit()
                print("Updated questions and answers to match the correct format")
                
        except json.JSONDecodeError:
            print("Current questions are not valid JSON. Updating...")
            # Update test with sample questions
            test.questions = json.dumps(sample_questions)
            test.answers = json.dumps(sample_answers)
            db.session.commit()
            print("Updated questions and answers to match the correct format")
            
        # Update test description to match the conversation in the audio
        test.description = "A conversation between a customer and a travel agent about booking a holiday to Greece."
        test.title = "Booking a Holiday"
        db.session.commit()
        print(f"Updated test description and title")
        
    else:
        print("No listening test found in database")