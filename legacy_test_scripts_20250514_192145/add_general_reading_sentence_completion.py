"""
Add General Training Reading Sentence Completion tests to the IELTS preparation app.
This script adds Sentence Completion tests based on the content provided.
"""
import json
from app import app, db
from models import PracticeTest

def add_general_reading_sentence_completion():
    """Add General Training Reading Sentence Completion tests."""
    
    # Define test sets for section 7 (sentence completion)
    # Using 8 of the 12 new passages provided
    test_sets = [
        {
            "title": "Company Communication Policy",
            "passage": """Effective communication is vital for our company's success. We utilize various channels, including email, intranet, and regular team meetings. Employees are expected to check their email daily and respond promptly to work-related inquiries. For urgent matters, phone calls or in-person communication is preferred.""",
            "sentences": [
                "Effective _____ is vital for success.",
                "We use email and the company _____ .",
                "Employees must check their _____ daily.",
                "_____ calls are for urgent matters.",
                "_____ communication is preferred for urgent issues."
            ],
            "answers": {
                "1": "communication",
                "2": "intranet",
                "3": "email",
                "4": "phone",
                "5": "in-person"
            }
        },
        {
            "title": "Workplace Diversity and Inclusion",
            "passage": """Our company values diversity and is committed to creating an inclusive workplace. We believe that a diverse workforce fosters innovation, creativity, and better decision-making. We strive to ensure that all employees feel respected, valued, and have equal opportunities for growth.""",
            "sentences": [
                "Our company values _____ .",
                "We are committed to an _____ workplace.",
                "A diverse workforce fosters _____ .",
                "All employees should feel _____ .",
                "We ensure _____ opportunities for growth."
            ],
            "answers": {
                "1": "diversity",
                "2": "inclusive",
                "3": "innovation",
                "4": "respected",
                "5": "equal"
            }
        },
        {
            "title": "Company Dress Code",
            "passage": """We maintain a professional dress code to uphold our company's image and create a respectful work environment. Employees are expected to dress appropriately for their roles and interactions with clients or visitors. Specific dress code guidelines may vary depending on the department and work setting.""",
            "sentences": [
                "We maintain a _____ dress code.",
                "The dress code upholds our _____ image.",
                "Employees should dress _____ for their roles.",
                "Guidelines may vary by _____ .",
                "The dress code creates a _____ work environment."
            ],
            "answers": {
                "1": "professional",
                "2": "company's",
                "3": "appropriately",
                "4": "department",
                "5": "respectful"
            }
        },
        {
            "title": "Employee Assistance Program",
            "passage": """We offer an Employee Assistance Program (EAP) to provide confidential support to employees facing personal or work-related challenges. The EAP offers counseling services, resources, and referrals to help employees address a variety of issues, such as stress, financial difficulties, and family matters.""",
            "sentences": [
                "We offer an Employee _____ Program.",
                "The EAP provides _____ support to employees.",
                "It offers _____ services to employees.",
                "The EAP helps with _____ difficulties.",
                "EAP provides resources and _____ ."
            ],
            "answers": {
                "1": "Assistance",
                "2": "confidential",
                "3": "counseling",
                "4": "financial",
                "5": "referrals"
            }
        },
        {
            "title": "Project Management Procedures",
            "passage": """Effective project management is essential for successful project completion. These procedures outline the steps involved in planning, executing, and closing projects, ensuring that projects are delivered on time and within budget. Project managers are responsible for adhering to these procedures and coordinating project activities.""",
            "sentences": [
                "Effective _____ management is essential.",
                "Procedures outline steps in _____ projects.",
                "Projects must be delivered on _____ .",
                "Project managers _____ project activities.",
                "Procedures ensure projects are within _____ ."
            ],
            "answers": {
                "1": "project",
                "2": "planning",
                "3": "time",
                "4": "coordinate",
                "5": "budget"
            }
        },
        {
            "title": "Customer Service Standards",
            "passage": """Providing excellent customer service is crucial for building customer loyalty and maintaining our company's reputation. These standards outline the principles of courteous, efficient, and responsive customer interactions. All employees are expected to adhere to these standards in their dealings with customers.""",
            "sentences": [
                "Excellent customer service builds customer _____ .",
                "Standards outline _____ customer interactions.",
                "Customer service should be _____ .",
                "Customer service should be _____ .",
                "Employees must _____ to customer service standards."
            ],
            "answers": {
                "1": "loyalty",
                "2": "courteous",
                "3": "efficient",
                "4": "responsive",
                "5": "adhere"
            }
        },
        {
            "title": "Data Security Policy",
            "passage": """Protecting sensitive company and customer data is of paramount importance. This policy outlines the measures taken to ensure data security, including access controls, data encryption, and regular security audits. All employees are responsible for handling data securely and adhering to these guidelines.""",
            "sentences": [
                "Protecting sensitive _____ is paramount.",
                "The policy outlines _____ controls.",
                "Data _____ is part of the policy.",
                "Regular _____ audits are conducted.",
                "Employees must handle data _____ ."
            ],
            "answers": {
                "1": "data",
                "2": "access",
                "3": "encryption",
                "4": "security",
                "5": "securely"
            }
        },
        {
            "title": "Health and Safety Regulations",
            "passage": """Our company is committed to maintaining a safe and healthy workplace for all employees. We comply with all applicable health and safety regulations and implement additional measures where necessary. Regular safety training is provided to ensure employees are aware of potential hazards and proper safety procedures.""",
            "sentences": [
                "The company maintains a _____ workplace.",
                "We comply with safety _____ .",
                "_____ training is provided regularly.",
                "Training covers potential _____ .",
                "Employees learn proper safety _____ ."
            ],
            "answers": {
                "1": "safe",
                "2": "regulations",
                "3": "Safety",
                "4": "hazards",
                "5": "procedures"
            }
        }
    ]
    
    # Add test sets for additional reading topics to reach 16 total
    additional_test_sets = [
        {
            "title": "Environmental Sustainability Initiatives",
            "passage": """Our company is committed to environmental sustainability through various initiatives. We have implemented recycling programs, energy-efficient lighting, and paperless workflows. Employees are encouraged to contribute ideas for further reducing our environmental footprint and making our operations more sustainable.""",
            "sentences": [
                "Our company is committed to environmental _____ .",
                "We have implemented _____ programs.",
                "We use energy-efficient _____ .",
                "We promote paperless _____ .",
                "Employees can contribute _____ for sustainability."
            ],
            "answers": {
                "1": "sustainability",
                "2": "recycling",
                "3": "lighting",
                "4": "workflows",
                "5": "ideas"
            }
        },
        {
            "title": "Company Vehicle Policy",
            "passage": """Company vehicles are provided for business purposes only. Drivers must hold a valid license and maintain a clean driving record. All traffic regulations must be followed, and vehicles must be kept clean and well-maintained. Any accidents or damage must be reported immediately to the fleet manager.""",
            "sentences": [
                "Company vehicles are for _____ purposes only.",
                "Drivers need a valid _____ .",
                "Drivers must follow traffic _____ .",
                "Vehicles must be kept _____ .",
                "Accidents must be reported to the fleet _____ ."
            ],
            "answers": {
                "1": "business",
                "2": "license",
                "3": "regulations",
                "4": "clean",
                "5": "manager"
            }
        },
        {
            "title": "Business Travel Expenses",
            "passage": """Our company reimburses reasonable expenses incurred during business travel. This includes accommodation, transportation, and meals. Entertainment expenses require prior approval. All expenses must be documented with receipts and submitted within two weeks of return using the expense claim form.""",
            "sentences": [
                "We reimburse _____ expenses for business travel.",
                "Reimbursed expenses include _____ .",
                "Entertainment expenses need prior _____ .",
                "Expenses must be documented with _____ .",
                "Claims must be submitted within two _____ ."
            ],
            "answers": {
                "1": "reasonable",
                "2": "accommodation",
                "3": "approval",
                "4": "receipts",
                "5": "weeks"
            }
        },
        {
            "title": "Office Equipment Use",
            "passage": """Company equipment is provided for work-related activities. Employees are responsible for proper use and care of assigned equipment. Any damage or malfunction should be reported promptly to the IT department. Personal use of company equipment should be minimal and within acceptable use guidelines.""",
            "sentences": [
                "Equipment is provided for work-related _____ .",
                "Employees must ensure proper _____ of equipment.",
                "Report _____ to the IT department.",
                "Reports should be made _____ .",
                "Personal use should be _____ ."
            ],
            "answers": {
                "1": "activities",
                "2": "care",
                "3": "malfunctions",
                "4": "promptly",
                "5": "minimal"
            }
        },
        {
            "title": "Remote Work Guidelines",
            "passage": """Remote work arrangements allow employees to work from locations outside the office. Employees working remotely must maintain regular communication with their team and supervisor. They are expected to be available during core business hours and complete their work responsibilities as if they were in the office.""",
            "sentences": [
                "Remote work allows employees to work from different _____ .",
                "Remote workers must maintain regular _____ .",
                "Employees should be available during core _____ hours.",
                "Remote workers must complete their _____ responsibilities.",
                "Remote work is treated like in-office _____ ."
            ],
            "answers": {
                "1": "locations",
                "2": "communication",
                "3": "business",
                "4": "work",
                "5": "work"
            }
        },
        {
            "title": "Professional Development Opportunities",
            "passage": """We support the professional growth of our employees through various development opportunities. These include internal training programs, external courses, and conference attendance. Employees are encouraged to create professional development plans with their managers during annual performance reviews.""",
            "sentences": [
                "We support employee professional _____ .",
                "Development includes internal _____ programs.",
                "Employees may attend external _____ .",
                "Employees create development _____ .",
                "Plans are discussed during _____ reviews."
            ],
            "answers": {
                "1": "growth",
                "2": "training",
                "3": "courses",
                "4": "plans",
                "5": "performance"
            }
        },
        {
            "title": "Client Confidentiality Agreement",
            "passage": """All employees must maintain strict confidentiality regarding client information. Client data must be handled securely and shared only with authorized personnel. Discussions about clients should take place in private settings. Any breach of client confidentiality is considered a serious violation of company policy.""",
            "sentences": [
                "Employees must maintain client _____ .",
                "Client data must be handled _____ .",
                "Data should only be shared with _____ personnel.",
                "Client discussions require _____ settings.",
                "Confidentiality breaches are a serious _____ ."
            ],
            "answers": {
                "1": "confidentiality",
                "2": "securely",
                "3": "authorized",
                "4": "private",
                "5": "violation"
            }
        },
        {
            "title": "Energy Conservation Guidelines",
            "passage": """To reduce our environmental impact and operational costs, we have implemented energy conservation guidelines. Employees should turn off lights, computers, and other equipment when not in use. The office temperature is maintained at an energy-efficient level. We continuously monitor our energy usage to identify further conservation opportunities.""",
            "sentences": [
                "Guidelines reduce environmental _____ .",
                "Employees should turn off _____ when not in use.",
                "Office temperature is kept at an efficient _____ .",
                "We monitor energy _____ regularly.",
                "We seek further conservation _____ ."
            ],
            "answers": {
                "1": "impact",
                "2": "equipment",
                "3": "level",
                "4": "usage",
                "5": "opportunities"
            }
        }
    ]
    
    # Combine all test sets
    test_sets.extend(additional_test_sets)
    
    # Add each test to the database
    with app.app_context():
        # Remove existing tests first to avoid duplicates
        PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=7  # Section 7 is for Sentence Completion
        ).delete()
        db.session.commit()
        
        # Add each test set
        for i, test_set in enumerate(test_sets, 1):
            test = PracticeTest(
                title=f"General Training Reading: Sentence Completion {i}",
                description=f"Part 7: {test_set['title']}. Complete the sentences using ONE WORD ONLY from the passage.",
                test_type="reading",
                ielts_test_type="general",
                section=7,  # Section 7 is for Sentence Completion
                _content=test_set["passage"],
                _questions=json.dumps(test_set["sentences"]),
                _answers=json.dumps(test_set["answers"])
            )
            db.session.add(test)
            print(f"Added General Training Reading: Sentence Completion {i}")
        
        db.session.commit()
        print(f"Successfully added {len(test_sets)} General Training Reading Sentence Completion tests.")

if __name__ == "__main__":
    add_general_reading_sentence_completion()