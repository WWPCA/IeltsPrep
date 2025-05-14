from app import app, db
from models import PracticeTest
import json

def create_listening_test():
    """Create a sample IELTS listening test following the official IELTS format."""
    with app.app_context():
        # Check if listening test already exists
        existing_test = PracticeTest.query.filter_by(
            test_type='listening',
            title='Section 1: Accommodation Inquiry'
        ).first()
        
        if existing_test:
            print("Sample listening tests already exist.")
            return
        
        # Section 1 - Conversation about accommodation (social/general context)
        section1_test = PracticeTest(
            test_type='listening',
            section=1,
            title='Section 1: Accommodation Inquiry',
            description='A conversation between a student and an accommodation officer about student housing options.',
            questions=json.dumps([
                {
                    "number": "1-5",
                    "instructions": "Complete the form below. Write NO MORE THAN THREE WORDS AND/OR A NUMBER for each answer.",
                    "form_title": "STUDENT ACCOMMODATION REQUEST FORM",
                    "form_fields": [
                        {"field": "Student name", "answer_key": "1"},
                        {"field": "Student ID", "answer_key": "2"},
                        {"field": "Preferred location", "answer_key": "3"},
                        {"field": "Maximum monthly budget", "answer_key": "4"},
                        {"field": "Special requirements", "answer_key": "5"}
                    ]
                },
                {
                    "number": "6-10",
                    "instructions": "Complete the sentences below. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.",
                    "questions": [
                        {"number": "6", "text": "The accommodation office can arrange a _____ of available properties."},
                        {"number": "7", "text": "Students must pay a deposit of _____ to secure accommodation."},
                        {"number": "8", "text": "Contracts typically require _____ notice before leaving."},
                        {"number": "9", "text": "The student housing guidebook is available on the _____."},
                        {"number": "10", "text": "For further questions, students should contact the accommodation team by _____."}
                    ]
                }
            ]),
            answers=json.dumps({
                "1": "Sarah Johnson",
                "2": "BT5940728",
                "3": "near campus",
                "4": "£600",
                "5": "quiet environment",
                "6": "viewing",
                "7": "£300",
                "8": "one month's",
                "9": "university website",
                "10": "email"
            }),
            audio_url='/static/audio/accommodation_inquiry.mp3'
        )
        
        # Section 2 - Monologue in social context (community center tour)
        section2_test = PracticeTest(
            test_type='listening',
            section=2,
            title='Section 2: Community Center Introduction',
            description='A presentation about the facilities and services offered at a new community center.',
            questions=json.dumps([
                {
                    "number": "11-16",
                    "instructions": "Complete the table below. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.",
                    "table_title": "COMMUNITY CENTER FACILITIES",
                    "table_headers": ["Facility", "Location", "Opening Hours", "Special Notes"],
                    "table_rows": [
                        {"facility": "Main Library", "location": "Ground floor", "hours": "_____ 11", "notes": "Includes digital resources"},
                        {"facility": "_____ 12", "location": "First floor", "hours": "10am - 6pm", "notes": "Requires membership"},
                        {"facility": "Café", "location": "_____ 13", "hours": "8am - 5pm", "notes": "Locally sourced food"},
                        {"facility": "Children's Area", "location": "Ground floor", "hours": "10am - _____ 14", "notes": "_____ 15 required"},
                        {"facility": "_____ 16", "location": "Basement", "hours": "By appointment", "notes": "Free for members"}
                    ]
                },
                {
                    "number": "17-20",
                    "instructions": "Choose FOUR answers from the box and write the correct letter, A-G, next to Questions 17-20.",
                    "box_options": [
                        "A. Painting workshops",
                        "B. Language classes",
                        "C. Computer training",
                        "D. Job search assistance",
                        "E. Health checkups",
                        "F. Financial advice",
                        "G. Cooking demonstrations"
                    ],
                    "question_text": "Which FOUR services will be introduced at the community center next month?",
                    "answers": ["17", "18", "19", "20"]
                }
            ]),
            answers=json.dumps({
                "11": "9am to 7pm",
                "12": "Fitness studio",
                "13": "outdoor terrace",
                "14": "4pm",
                "15": "adult supervision",
                "16": "Recording studio",
                "17": "B",
                "18": "C",
                "19": "E",
                "20": "G"
            }),
            audio_url='/static/audio/community_center.mp3'
        )
        
        # Section 3 - Discussion between students about academic topic
        section3_test = PracticeTest(
            test_type='listening',
            section=3,
            title='Section 3: Biodiversity Research Project',
            description='A conversation between two students and their professor about planning a biodiversity research project.',
            questions=json.dumps([
                {
                    "number": "21-26",
                    "instructions": "Choose the correct letter, A, B or C.",
                    "questions": [
                        {
                            "number": "21",
                            "text": "The students decide to focus their research on",
                            "options": {
                                "A": "tropical rainforest ecosystems",
                                "B": "urban wildlife corridors",
                                "C": "coastal marine environments"
                            }
                        },
                        {
                            "number": "22",
                            "text": "According to the professor, the main challenge of the project will be",
                            "options": {
                                "A": "obtaining sufficient funding",
                                "B": "accessing relevant study sites",
                                "C": "collecting reliable data"
                            }
                        },
                        {
                            "number": "23",
                            "text": "The students are advised to contact the local council for",
                            "options": {
                                "A": "research permits",
                                "B": "historical data",
                                "C": "equipment loans"
                            }
                        },
                        {
                            "number": "24",
                            "text": "The female student suggests they should",
                            "options": {
                                "A": "interview conservation experts",
                                "B": "use existing survey methods",
                                "C": "develop a new monitoring technique"
                            }
                        },
                        {
                            "number": "25",
                            "text": "The group agrees that their final report should emphasize",
                            "options": {
                                "A": "economic benefits of biodiversity",
                                "B": "policy recommendations",
                                "C": "comparison with international studies"
                            }
                        },
                        {
                            "number": "26",
                            "text": "The project timeline requires field work to be completed by",
                            "options": {
                                "A": "mid-June",
                                "B": "end of July",
                                "C": "early September"
                            }
                        }
                    ]
                },
                {
                    "number": "27-30",
                    "instructions": "Complete the notes below. Write ONE WORD ONLY for each answer.",
                    "note_title": "PROJECT RESPONSIBILITIES",
                    "notes": [
                        "- David: literature review and _____ 27 design",
                        "- Rachel: species identification and _____ 28 collection",
                        "- Both: analysis of data using _____ 29 modeling",
                        "- Professor will provide specialized _____ 30 for field work"
                    ]
                }
            ]),
            answers=json.dumps({
                "21": "B",
                "22": "C",
                "23": "A",
                "24": "B",
                "25": "B",
                "26": "A",
                "27": "survey",
                "28": "sample",
                "29": "statistical",
                "30": "equipment"
            }),
            audio_url='/static/audio/biodiversity_project.mp3'
        )
        
        # Section 4 - Monologue on academic subject
        section4_test = PracticeTest(
            test_type='listening',
            section=4,
            title='Section 4: Lecture on Urban Planning',
            description='A university lecture about sustainable urban planning principles and future city designs.',
            questions=json.dumps([
                {
                    "number": "31-35",
                    "instructions": "Complete the notes below. Write NO MORE THAN TWO WORDS for each answer.",
                    "note_title": "SUSTAINABLE URBAN PLANNING PRINCIPLES",
                    "notes": [
                        "Integrating _____ 31 spaces throughout urban areas",
                        "Designing mixed-use developments to reduce _____ 32",
                        "Implementing efficient _____ 33 systems",
                        "Creating pedestrian-friendly _____ 34",
                        "Focusing on renewable _____ 35 sources"
                    ]
                },
                {
                    "number": "36-40",
                    "instructions": "Complete the diagram below. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.",
                    "diagram_title": "THE IDEAL FUTURE CITY MODEL",
                    "diagram_parts": [
                        {"label": "City Center Features", "component": "Cultural district with _____ 36 at its heart"},
                        {"label": "Transport Network", "component": "Underground _____ 37 connecting all districts"},
                        {"label": "Residential Areas", "component": "Maximum _____ 38 of 5 stories"},
                        {"label": "Energy Infrastructure", "component": "Solar panels on _____ 39 of buildings"},
                        {"label": "Water Management", "component": "Citywide _____ 40 harvesting system"}
                    ]
                }
            ]),
            answers=json.dumps({
                "31": "green",
                "32": "commuting",
                "33": "public transport",
                "34": "neighborhoods",
                "35": "energy",
                "36": "public square",
                "37": "transit system",
                "38": "height",
                "39": "rooftops",
                "40": "rainwater"
            }),
            audio_url='/static/audio/urban_planning_lecture.mp3'
        )
        
        # Add all tests to the database
        db.session.add(section1_test)
        db.session.add(section2_test)
        db.session.add(section3_test)
        db.session.add(section4_test)
        
        # Commit the changes
        db.session.commit()
        print("Successfully created 4 sample listening tests (Sections 1-4) following the official IELTS format.")

if __name__ == "__main__":
    create_listening_test()