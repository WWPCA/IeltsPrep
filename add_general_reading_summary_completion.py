"""
Add General Training Reading Summary Completion tests to the IELTS preparation app.
This script adds 16 different Summary Completion tests based on the content provided.
"""
import json
from app import app, db
from models import PracticeTest

def add_general_reading_summary_completion():
    """Add General Training Reading Summary Completion tests."""
    
    # Define the 16 test sets
    test_sets = [
        {
            "title": "The Benefits of Volunteering",
            "passage": """Volunteering offers numerous benefits, enriching individuals and communities. Dedicating time to causes provides a sense of purpose and fulfillment. It develops new skills and expands social networks. Volunteering improves well-being and promotes a positive outlook. Volunteers deliver essential services and support vulnerable populations, strengthening social bonds.""",
            "summary": """Volunteering provides a sense of _____. It develops new _____ and expands _____ networks. It improves _____ and promotes a _____ outlook.""",
            "answers": {
                "1": "purpose",
                "2": "skills",
                "3": "social",
                "4": "well-being",
                "5": "positive"
            }
        },
        {
            "title": "The Importance of Reading",
            "passage": """Reading is a fundamental skill that enriches lives. It expands knowledge, improves vocabulary, and enhances critical thinking. Reading provides entertainment, reduces stress, and fosters empathy. Regular reading habits contribute to lifelong learning and personal growth.""",
            "summary": """Reading expands _____ and improves _____. It reduces _____ and fosters _____. Reading contributes to lifelong _____.""",
            "answers": {
                "1": "knowledge",
                "2": "vocabulary",
                "3": "stress",
                "4": "empathy",
                "5": "learning"
            }
        },
        {
            "title": "The History of Coffee",
            "passage": """Coffee originated in Ethiopia and spread globally. Its stimulating effects were recognized early. Coffeehouses became social and cultural hubs. Today, coffee is a popular beverage, enjoyed in diverse forms and traditions.""",
            "summary": """Coffee originated in _____. Its stimulating effects were recognized _____. Coffeehouses became _____ hubs. Coffee is a _____ beverage. It is enjoyed in diverse _____.""",
            "answers": {
                "1": "Ethiopia",
                "2": "early",
                "3": "social",
                "4": "popular",
                "5": "forms"
            }
        },
        {
            "title": "The Impact of Music",
            "passage": """Music profoundly impacts human emotions and well-being. It evokes a wide range of feelings. Music therapy treats various conditions. Listening to music reduces stress, improves mood, and enhances cognitive function.""",
            "summary": """Music impacts human _____. It evokes a wide range of _____. Music therapy treats various _____. Listening to music reduces _____. It improves mood and _____ function.""",
            "answers": {
                "1": "emotions",
                "2": "feelings",
                "3": "conditions",
                "4": "stress",
                "5": "cognitive"
            }
        },
        {
            "title": "The Benefits of Exercise",
            "passage": """Regular exercise is essential for good health. It strengthens the cardiovascular system, improves mood, and controls weight. Exercise reduces the risk of chronic diseases, such as heart disease, diabetes, and cancer.""",
            "summary": """Exercise strengthens the _____ system. It improves _____ and controls _____. Exercise reduces the _____ of chronic diseases. It reduces the risk of _____ and diabetes.""",
            "answers": {
                "1": "cardiovascular",
                "2": "mood",
                "3": "weight",
                "4": "risk",
                "5": "cancer"
            }
        },
        {
            "title": "The Importance of Sleep",
            "passage": """Adequate sleep is crucial for physical and mental well-being. During sleep, the body repairs itself, and the brain consolidates memories. Lack of sleep leads to fatigue, impaired concentration, and increased health risks.""",
            "summary": """Sleep is crucial for _____ and mental well-being. The body _____ itself during sleep. The brain _____ memories during sleep. Lack of sleep leads to _____. It increases _____ risks.""",
            "answers": {
                "1": "physical",
                "2": "repairs",
                "3": "consolidates",
                "4": "fatigue",
                "5": "health"
            }
        },
        {
            "title": "The Role of Technology in Education",
            "passage": """Technology is transforming education, providing new learning tools and resources. Online courses, interactive simulations, and educational apps enhance learning. Technology facilitates collaboration and communication between students and teachers.""",
            "summary": """Technology is _____ education. It provides new learning _____. Online courses _____ learning. Technology facilitates _____ between students. It enhances _____ and communication.""",
            "answers": {
                "1": "transforming",
                "2": "tools",
                "3": "enhance",
                "4": "collaboration",
                "5": "learning"
            }
        },
        {
            "title": "The History of Photography",
            "passage": """Photography has revolutionized how we capture memories. From early daguerreotypes to digital cameras, photography has evolved. It is an art form, a tool for documentation, and a means of communication.""",
            "summary": """Photography has _____ how we capture memories. Early photography used _____. Digital cameras are a modern form of _____. Photography is an _____ form. It is a tool for _____.""",
            "answers": {
                "1": "revolutionized",
                "2": "daguerreotypes",
                "3": "photography",
                "4": "art",
                "5": "documentation"
            }
        },
        {
            "title": "The Impact of Climate Change",
            "passage": """Climate change is a global challenge with far-reaching consequences. Rising temperatures, extreme weather events, and sea-level rise affect ecosystems, economies, and societies. Addressing climate change requires urgent action.""",
            "summary": """Climate change is a _____ challenge. Rising _____ are a consequence. Extreme _____ events are increasing. Sea-level rise affects _____. Climate change requires _____ action.""",
            "answers": {
                "1": "global",
                "2": "temperatures",
                "3": "weather",
                "4": "societies",
                "5": "urgent"
            }
        },
        {
            "title": "The Importance of Water Conservation",
            "passage": """Water is a precious resource essential for life. Conserving water ensures its availability for future generations. Simple actions, such as reducing water usage, and supporting water-efficient practices, help.""",
            "summary": """Water is a _____ resource. Conserving water ensures its _____ for future generations. _____ water usage helps. Supporting water-_____ practices helps. Water is essential for _____.""",
            "answers": {
                "1": "precious",
                "2": "availability",
                "3": "reducing",
                "4": "efficient",
                "5": "life"
            }
        },
        {
            "title": "The Benefits of Travel",
            "passage": """Travel broadens horizons, exposing people to new cultures and creating memories. It enhances personal growth, increases understanding, and promotes tolerance. Travel supports local economies and fosters global connections.""",
            "summary": """Travel _____ horizons. It exposes people to new _____. Travel enhances personal _____. It increases _____ and promotes _____.""",
            "answers": {
                "1": "broadens",
                "2": "cultures",
                "3": "growth",
                "4": "understanding",
                "5": "tolerance"
            }
        },
        {
            "title": "The Impact of Social Media",
            "passage": """Social media has transformed communication and interaction. It connects people globally, facilitates information sharing, and provides platforms for self-expression. It raises concerns about privacy, misinformation, and cyberbullying.""",
            "summary": """Social media has _____ communication. It connects people _____. It facilitates information _____. It provides platforms for self-_____. Social media raises concerns about _____.""",
            "answers": {
                "1": "transformed",
                "2": "globally",
                "3": "sharing",
                "4": "expression",
                "5": "privacy"
            }
        },
        {
            "title": "The Importance of a Healthy Diet",
            "passage": """A healthy diet provides essential nutrients for optimal body function. It includes fruits, vegetables, whole grains, and lean proteins. A balanced diet improves energy, supports immunity, and reduces the risk of chronic diseases.""",
            "summary": """A healthy diet provides _____ nutrients. It includes fruits and _____. A balanced diet improves _____. It supports _____ function. It reduces the _____ of chronic diseases.""",
            "answers": {
                "1": "essential",
                "2": "vegetables",
                "3": "energy",
                "4": "immunity",
                "5": "risk"
            }
        },
        {
            "title": "The Role of Renewable Energy",
            "passage": """Renewable energy sources, like solar and wind power, are increasingly important. They offer a cleaner alternative to fossil fuels, reducing greenhouse gas emissions. Renewable energy helps mitigate climate change.""",
            "summary": """Renewable energy sources are increasingly _____. They offer a _____ alternative. They reduce greenhouse gas _____. Solar and wind power are _____ energy sources. They help mitigate _____ change.""",
            "answers": {
                "1": "important",
                "2": "cleaner",
                "3": "emissions",
                "4": "renewable",
                "5": "climate"
            }
        },
        {
            "title": "The Benefits of Lifelong Learning",
            "passage": """Lifelong learning involves continuous pursuit of knowledge and skills. It enhances personal development, expands career opportunities, and promotes active citizenship. Lifelong learning helps individuals adapt to change.""",
            "summary": """Lifelong learning involves continuous pursuit of _____. It enhances personal _____. It expands _____ opportunities. It promotes _____ citizenship. Lifelong learning helps individuals _____ to change.""",
            "answers": {
                "1": "knowledge",
                "2": "development",
                "3": "career",
                "4": "active",
                "5": "adapt"
            }
        },
        {
            "title": "The Impact of E-commerce",
            "passage": """E-commerce has revolutionized buying and selling. Online shopping offers convenience, wider selection, and competitive prices. It has created new opportunities for businesses to reach global markets.""",
            "summary": """E-commerce has _____ buying and selling. Online shopping offers _____. It offers a _____ selection. E-commerce offers _____ prices. It has created new _____ for businesses.""",
            "answers": {
                "1": "revolutionized",
                "2": "convenience",
                "3": "wider",
                "4": "competitive",
                "5": "opportunities"
            }
        }
    ]
    
    # Add each test to the database
    with app.app_context():
        # Remove existing tests first to avoid duplicates
        PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=5  # Section 5 is for Summary Completion
        ).delete()
        db.session.commit()
        
        # Add each test set
        for i, test_set in enumerate(test_sets, 1):
            test = PracticeTest(
                title=f"General Training Reading: Summary Completion {i}",
                description=f"Part 5: {test_set['title']}. Complete the summary using ONE WORD ONLY from the passage.",
                test_type="reading",
                ielts_test_type="general",
                section=5,  # Section 5 is for Summary Completion
                _content=test_set["passage"],
                _questions=json.dumps([test_set["summary"]]),  # Store the summary text as a question
                _answers=json.dumps(test_set["answers"])
            )
            db.session.add(test)
            print(f"Added General Training Reading: Summary Completion {i}")
        
        db.session.commit()
        print(f"Successfully added {len(test_sets)} General Training Reading Summary Completion tests.")

if __name__ == "__main__":
    add_general_reading_summary_completion()