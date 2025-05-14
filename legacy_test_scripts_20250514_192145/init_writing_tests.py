"""
Initialize writing tests for IELTS preparation.
"""

import json
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from models import PracticeTest

# Sample writing prompts
WRITING_TESTS = [
    {
        "test_type": "writing",
        "section": 1,
        "title": "Academic Task 1: Bar Chart - Global Tourism",
        "description": "IELTS Academic Task 1 writing practice with bar chart data.",
        "questions": [
            """The bar chart below shows the number of international tourists in different regions of the world in 2010 and 2020, as well as projections for 2030.

Summarise the information by selecting and reporting the main features, and make comparisons where relevant.

[Bar chart showing international tourist arrivals (in millions) across Europe, Asia-Pacific, Americas, Africa, and Middle East regions for years 2010, 2020, and projected 2030. Europe shows the highest numbers, followed by Asia-Pacific, then Americas, with Africa and Middle East having the lowest but growing numbers.]

Write at least 150 words."""
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by GPT-4o."
        ]
    },
    {
        "test_type": "writing",
        "section": 1,
        "title": "Academic Task 1: Line Graph - Internet Usage",
        "description": "IELTS Academic Task 1 writing practice with line graph data.",
        "questions": [
            """The line graph below shows the percentage of the population using the Internet in four different countries between 2000 and 2020.

Summarise the information by selecting and reporting the main features, and make comparisons where relevant.

[Line graph showing Internet usage percentage in Australia, Canada, Japan, and India from 2000 to 2020. Australia and Canada show rapid growth reaching about 90% by 2020. Japan shows steady growth to about 80%. India shows slow initial growth then accelerates after 2010, reaching about 45% by 2020.]

Write at least 150 words."""
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by GPT-4o."
        ]
    },
    {
        "test_type": "writing",
        "section": 1,
        "title": "General Training Task 1: Formal Letter - Job Application",
        "description": "IELTS General Training Task 1 writing practice with formal letter.",
        "questions": [
            """You would like to apply for a position at an international company.

Write a letter to the human resources manager. In your letter:
- explain which position you are applying for and how you heard about it
- describe your relevant qualifications and experience
- explain why you would be suitable for the job

Write at least 150 words.
You do NOT need to write any addresses.
Begin your letter as follows:
Dear Sir/Madam,"""
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by GPT-4o."
        ]
    },
    {
        "test_type": "writing",
        "section": 2,
        "title": "Task 2: Technology and Society",
        "description": "IELTS Task 2 writing practice essay on technology's impact.",
        "questions": [
            """The development of technology has helped societies build stronger economies but has negative impacts on social interactions among people.

To what extent do you agree or disagree with this statement?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words."""
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by GPT-4o."
        ]
    },
    {
        "test_type": "writing",
        "section": 2,
        "title": "Task 2: Education Systems",
        "description": "IELTS Task 2 writing practice essay on education policy.",
        "questions": [
            """Some people believe that children should be free to choose which subjects they study at school, while others believe children should be required to study certain key subjects until they finish high school.

Discuss both these views and give your own opinion.

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words."""
        ],
        "answers": [
            "This is a sample model answer structure. Actual assessment will be done by GPT-4o."
        ]
    }
]

def init_writing_tests():
    """Initialize the writing tests in the database."""
    with app.app_context():
        try:
            # Check if writing tests already exist
            existing_tests = PracticeTest.query.filter_by(test_type='writing').count()
            if existing_tests > 0:
                print(f"Writing tests already exist in the database ({existing_tests} found). Skipping initialization.")
                return

            # Add the sample writing tests
            for test_data in WRITING_TESTS:
                test = PracticeTest(
                    test_type=test_data["test_type"],
                    section=test_data["section"],
                    title=test_data["title"],
                    description=test_data["description"],
                    questions=test_data["questions"],
                    answers=test_data["answers"]
                )
                db.session.add(test)
            
            db.session.commit()
            print(f"Successfully added {len(WRITING_TESTS)} writing tests to the database.")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error initializing writing tests: {str(e)}")

if __name__ == "__main__":
    init_writing_tests()