"""
Add General Training Reading Note Completion tests to the IELTS preparation app.
This script adds Note Completion tests with individual sentences to complete.
"""
import json
from app import app, db
from models import PracticeTest

def add_general_reading_note_completion():
    """Add General Training Reading Note Completion tests."""
    
    # Define the initial 4 test sets
    test_sets = [
        {
            "title": "Company Travel Policy",
            "passage": """Our company provides a comprehensive travel policy for employees on business trips. All travel arrangements must be made through the designated travel agent to ensure cost-effectiveness and adherence to company guidelines. Employees are expected to submit a detailed travel itinerary and estimated expenses for approval prior to departure. Reimbursement for approved expenses will be processed upon submission of original receipts and a completed expense report.""",
            "sentences": [
                "Travel arrangements must be made through the designated travel _____ .",
                "Employees must submit a detailed travel _____ before departure.",
                "Approved expenses will be _____ upon submission of receipts.",
                "Employees need to submit an _____ report.",
                "The company aims for _____-effectiveness."
            ],
            "answers": {
                "1": "agent",
                "2": "itinerary",
                "3": "reimbursed",
                "4": "expense",
                "5": "cost"
            }
        },
        {
            "title": "Employee Training Programs",
            "passage": """We offer a variety of employee training programs to enhance skills and career development. These programs cover a wide range of topics, including technical skills, leadership development, and communication skills. Employees are encouraged to participate in relevant training programs to improve their performance and advance their careers. Participation in training programs may require supervisor approval.""",
            "sentences": [
                "Training programs enhance skills and career _____ .",
                "Programs cover technical and _____ skills.",
                "Employees are _____ to participate in training.",
                "Participation may require _____ approval.",
                "Training is offered on a wide _____ of topics."
            ],
            "answers": {
                "1": "development",
                "2": "communication",
                "3": "encouraged",
                "4": "supervisor",
                "5": "range"
            }
        },
        {
            "title": "Office Recycling Guidelines",
            "passage": """Our office is committed to environmental sustainability and encourages all employees to participate in our recycling program. Please use the designated bins for paper, plastic, and glass. Ensure that all items are clean and free of food residue before recycling. Recycling helps to conserve resources and reduce waste.""",
            "sentences": [
                "Employees are encouraged to participate in our _____ program.",
                "Use designated bins for paper, plastic, and _____ .",
                "Items should be clean and free of food _____ .",
                "Recycling helps to _____ resources.",
                "We are committed to environmental _____ ."
            ],
            "answers": {
                "1": "recycling",
                "2": "glass",
                "3": "residue",
                "4": "conserve",
                "5": "sustainability"
            }
        },
        {
            "title": "Health and Safety Procedures",
            "passage": """The health and safety of our employees is our top priority. All employees are required to familiarize themselves with the company's health and safety procedures. These procedures include guidelines for workplace safety, emergency protocols, and the use of safety equipment. Regular safety meetings are held to discuss potential hazards and promote a safe working environment.""",
            "sentences": [
                "Employee health and _____ is a top priority.",
                "Employees must familiarize themselves with safety _____ .",
                "Procedures include guidelines for workplace _____ .",
                "Regular _____ meetings are held.",
                "Employees must know about _____ protocols."
            ],
            "answers": {
                "1": "safety",
                "2": "procedures",
                "3": "safety",
                "4": "safety",
                "5": "emergency"
            }
        }
    ]
    
    # Create additional test sets to make 16 total
    additional_test_sets = [
        {
            "title": "Customer Service Guidelines",
            "passage": """Our company is committed to providing excellent customer service. All customer inquiries should be handled promptly and professionally. Staff are expected to maintain a positive attitude and demonstrate patience when dealing with difficult situations. Regular training is provided to enhance customer service skills and ensure consistency across all departments.""",
            "sentences": [
                "Customer inquiries should be handled _____ and professionally.",
                "Staff are expected to maintain a positive _____ .",
                "Staff should demonstrate _____ with difficult situations.",
                "Training is provided on a _____ basis.",
                "Training ensures _____ across departments."
            ],
            "answers": {
                "1": "promptly",
                "2": "attitude",
                "3": "patience",
                "4": "regular",
                "5": "consistency"
            }
        },
        {
            "title": "Company Internet Usage Policy",
            "passage": """The company provides internet access to employees for business purposes. Personal use of the internet is permitted during breaks, provided it does not interfere with job performance or violate company policies. Employees are prohibited from accessing inappropriate content or downloading unauthorized software. Internet usage is monitored to ensure compliance with these guidelines.""",
            "sentences": [
                "Internet access is provided for _____ purposes.",
                "Personal use is permitted during _____ .",
                "Employees must not access inappropriate _____ .",
                "Downloading unauthorized _____ is prohibited.",
                "Internet usage is _____ for compliance."
            ],
            "answers": {
                "1": "business",
                "2": "breaks",
                "3": "content",
                "4": "software",
                "5": "monitored"
            }
        },
        {
            "title": "Office Security Measures",
            "passage": """To maintain a secure workplace, all employees must wear identification badges at all times. Visitors must sign in at reception and be escorted by an employee. Confidential documents should be secured in locked cabinets when not in use. Any security concerns should be reported immediately to the security department.""",
            "sentences": [
                "Employees must wear _____ badges at all times.",
                "Visitors must sign in at _____ .",
                "Visitors require an employee _____ .",
                "Confidential documents should be kept in _____ cabinets.",
                "Security concerns should be reported _____ ."
            ],
            "answers": {
                "1": "identification",
                "2": "reception",
                "3": "escort",
                "4": "locked",
                "5": "immediately"
            }
        },
        {
            "title": "Employee Leave Policy",
            "passage": """All employees are entitled to annual leave in accordance with their employment contract. Leave requests must be submitted at least two weeks in advance for approval. Sick leave requires a medical certificate for absences exceeding three consecutive days. Parental leave is available for eligible employees in accordance with national regulations.""",
            "sentences": [
                "Leave entitlement is specified in the employment _____ .",
                "Leave requests need _____ weeks' advance notice.",
                "Sick leave exceeding three days requires a medical _____ .",
                "Parental leave follows national _____ .",
                "Leave requests require _____ from management."
            ],
            "answers": {
                "1": "contract",
                "2": "two",
                "3": "certificate",
                "4": "regulations",
                "5": "approval"
            }
        },
        {
            "title": "Office Equipment Usage",
            "passage": """Company equipment is provided for business use only. Employees are responsible for the proper care and maintenance of equipment assigned to them. Any damage or malfunction should be reported to the IT department immediately. Equipment must not be removed from the premises without prior authorization.""",
            "sentences": [
                "Equipment is for _____ use only.",
                "Employees must ensure proper _____ of equipment.",
                "Report equipment _____ to IT department.",
                "Reports should be made _____ .",
                "Removing equipment requires prior _____ ."
            ],
            "answers": {
                "1": "business",
                "2": "care",
                "3": "damage",
                "4": "immediately",
                "5": "authorization"
            }
        },
        {
            "title": "Data Protection Guidelines",
            "passage": """Employees must handle all personal and confidential data with utmost care. Passwords should be strong and changed regularly. Sensitive information should not be shared with unauthorized individuals. Any data breach must be reported to the compliance officer without delay to ensure proper handling according to regulations.""",
            "sentences": [
                "Data must be handled with _____ care.",
                "Passwords should be changed _____ .",
                "Sensitive information requires proper _____ .",
                "Data breaches must be reported without _____ .",
                "Data handling follows strict _____ ."
            ],
            "answers": {
                "1": "utmost",
                "2": "regularly",
                "3": "authorization",
                "4": "delay",
                "5": "regulations"
            }
        },
        {
            "title": "Workplace Etiquette",
            "passage": """Maintaining a professional workplace environment requires consideration for colleagues. Keep noise levels to a minimum, especially in open office areas. Personal conversations should be brief and quiet. Shared spaces, including the kitchen and meeting rooms, should be left clean and tidy after use.""",
            "sentences": [
                "Noise levels should be kept to a _____ .",
                "Personal conversations should be _____ and quiet.",
                "The office layout is primarily an _____ concept.",
                "Shared spaces should be left _____ after use.",
                "Kitchen areas are considered _____ spaces."
            ],
            "answers": {
                "1": "minimum",
                "2": "brief",
                "3": "open",
                "4": "clean",
                "5": "shared"
            }
        },
        {
            "title": "Performance Review Process",
            "passage": """Annual performance reviews provide an opportunity for feedback and goal setting. Employees should prepare a self-assessment prior to the review meeting. Managers will provide constructive feedback and identify areas for development. Performance objectives for the coming year will be established collaboratively.""",
            "sentences": [
                "Performance reviews occur on an _____ basis.",
                "Employees should prepare a self-_____ .",
                "Managers provide _____ feedback.",
                "Reviews identify areas for _____ .",
                "Performance objectives are established _____ ."
            ],
            "answers": {
                "1": "annual",
                "2": "assessment",
                "3": "constructive",
                "4": "development",
                "5": "collaboratively"
            }
        },
        {
            "title": "Meeting Room Guidelines",
            "passage": """Meeting rooms must be booked through the online reservation system. Please respect scheduled times to avoid disrupting subsequent meetings. Audiovisual equipment should be tested before important presentations. Food and beverages are permitted, but the room must be cleaned afterward.""",
            "sentences": [
                "Meeting rooms require online _____ .",
                "Scheduled times should be _____ by all users.",
                "Test _____ equipment before presentations.",
                "Food is _____ in meeting rooms.",
                "Rooms must be _____ after use."
            ],
            "answers": {
                "1": "reservation",
                "2": "respected",
                "3": "audiovisual",
                "4": "permitted",
                "5": "cleaned"
            }
        },
        {
            "title": "Business Travel Expenses",
            "passage": """Reasonable expenses incurred during business travel will be reimbursed. This includes accommodation, transportation, and meals. Entertainment expenses require prior approval. Itemized receipts must be submitted with the expense claim form within one week of return from travel.""",
            "sentences": [
                "_____ expenses are eligible for reimbursement.",
                "Expenses include _____ and transportation.",
                "Entertainment expenses need prior _____ .",
                "Receipts should be _____ for all expenses.",
                "Submit claims within one _____ of return."
            ],
            "answers": {
                "1": "Reasonable",
                "2": "accommodation",
                "3": "approval",
                "4": "itemized",
                "5": "week"
            }
        },
        {
            "title": "Flexible Working Arrangements",
            "passage": """Our company recognizes the importance of work-life balance and offers flexible working arrangements where operationally feasible. Options include flexible start and finish times, compressed work weeks, and remote working opportunities. Arrangements must be discussed with and approved by the immediate supervisor.""",
            "sentences": [
                "The company values work-life _____ .",
                "Flexible arrangements must be operationally _____ .",
                "Options include flexible _____ times.",
                "Some employees may work _____ .",
                "Arrangements require supervisor _____ ."
            ],
            "answers": {
                "1": "balance",
                "2": "feasible",
                "3": "start",
                "4": "remotely",
                "5": "approval"
            }
        },
        {
            "title": "Emergency Evacuation Procedures",
            "passage": """In case of emergency, employees should leave the building via the nearest emergency exit. Do not use elevators during an evacuation. Proceed to the designated assembly point and report to your department's fire warden. Regular drills are conducted to ensure familiarity with evacuation procedures.""",
            "sentences": [
                "Use the nearest emergency _____ when evacuating.",
                "Elevators should not be _____ during evacuations.",
                "Proceed to the designated assembly _____ .",
                "Report to your department's fire _____ .",
                "_____ drills help ensure preparedness."
            ],
            "answers": {
                "1": "exit",
                "2": "used",
                "3": "point",
                "4": "warden",
                "5": "Regular"
            }
        }
    ]
    
    # Combine all test sets
    test_sets.extend(additional_test_sets)
    
    # Add more test sets from the new data provided
    additional_test_sets = [
        {
            "title": "Employee Performance Reviews",
            "passage": """Regular performance reviews are conducted to provide feedback and support employee development. These reviews assess performance against established goals and identify areas for improvement. Employees will have the opportunity to discuss their achievements and career aspirations with their supervisors.""",
            "sentences": [
                "Performance reviews provide employee _____ .",
                "Reviews assess performance against set _____ .",
                "Employees discuss _____ with supervisors.",
                "Reviews identify areas for _____ .",
                "Reviews are conducted _____ ."
            ],
            "answers": {
                "1": "feedback",
                "2": "goals",
                "3": "achievements",
                "4": "improvement",
                "5": "regularly"
            }
        },
        {
            "title": "Flexible Work Arrangements",
            "passage": """To support work-life balance, we offer flexible work arrangements, such as telecommuting and flexible hours. These arrangements allow employees to manage their work schedules and personal responsibilities effectively. Eligibility for flexible work arrangements may vary depending on job requirements and departmental needs.""",
            "sentences": [
                "We offer _____ work arrangements.",
                "Telecommuting and flexible hours support _____-life balance.",
                "Employees can manage their work _____ effectively.",
                "Eligibility may depend on job _____ .",
                "Arrangements support _____ responsibilities."
            ],
            "answers": {
                "1": "flexible",
                "2": "work",
                "3": "schedules",
                "4": "requirements",
                "5": "personal"
            }
        },
        {
            "title": "Intellectual Property Policy",
            "passage": """Our company's intellectual property (IP) is a valuable asset. This policy outlines the guidelines for protecting and managing company IP, including patents, trademarks, and copyrights. Employees are responsible for maintaining the confidentiality of company IP and adhering to these guidelines.""",
            "sentences": [
                "Company intellectual _____ is a valuable asset.",
                "The policy outlines _____ for protecting company IP.",
                "Patents and _____ are examples of company IP.",
                "Employees maintain IP _____ .",
                "Employees must _____ to guidelines."
            ],
            "answers": {
                "1": "property",
                "2": "guidelines",
                "3": "trademarks",
                "4": "confidentiality",
                "5": "adhere"
            }
        },
        {
            "title": "Social Media Guidelines",
            "passage": """Our company recognizes the importance of social media for communication and networking. However, employees are expected to use social media responsibly and professionally. These guidelines outline appropriate online behavior and protect the company's reputation.""",
            "sentences": [
                "Employees should use social media _____ .",
                "Guidelines outline appropriate _____ behavior.",
                "Social media is important for _____ and networking.",
                "Guidelines protect the company's _____ .",
                "Employees should act _____ ."
            ],
            "answers": {
                "1": "responsibly",
                "2": "online",
                "3": "communication",
                "4": "reputation",
                "5": "professionally"
            }
        },
        {
            "title": "Sales Commission Structure",
            "passage": """Our company offers a competitive sales commission structure to reward sales performance. Sales representatives earn commissions based on their sales volume and achievement of sales targets. The commission structure is designed to incentivize sales growth and provide opportunities for high earnings.""",
            "sentences": [
                "We offer a _____ sales commission structure.",
                "Commissions are based on sales _____ .",
                "Commissions reward sales _____ .",
                "The structure incentivizes sales _____ .",
                "The structure provides opportunities for high _____ ."
            ],
            "answers": {
                "1": "competitive",
                "2": "volume",
                "3": "performance",
                "4": "growth",
                "5": "earnings"
            }
        }
    ]
    
    # Add the additional sets to our existing test sets
    test_sets.extend(additional_test_sets)
    
    # Add each test to the database
    with app.app_context():
        # Remove existing tests first to avoid duplicates
        PracticeTest.query.filter_by(
            test_type='reading',
            ielts_test_type='general',
            section=6  # Section 6 is for Note Completion
        ).delete()
        db.session.commit()
        
        # Add each test set
        for i, test_set in enumerate(test_sets, 1):
            # Convert sentences to questions format
            questions = test_set["sentences"]
            
            test = PracticeTest(
                title=f"General Training Reading: Note Completion {i}",
                description=f"Part 6: {test_set['title']}. Complete the sentences using ONE WORD ONLY from the passage.",
                test_type="reading",
                ielts_test_type="general",
                section=6,  # Section 6 is for Note Completion
                _content=test_set["passage"],
                _questions=json.dumps(questions),
                _answers=json.dumps(test_set["answers"])
            )
            db.session.add(test)
            print(f"Added General Training Reading: Note Completion {i}")
        
        db.session.commit()
        print(f"Successfully added {len(test_sets)} General Training Reading Note Completion tests.")

if __name__ == "__main__":
    add_general_reading_note_completion()