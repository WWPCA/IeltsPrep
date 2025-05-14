"""
Add General Training Writing Task 2 tests to the IELTS preparation app.
This script adds essay writing tasks for General Training candidates from the provided list.
"""
import json
from datetime import datetime
from app import app, db
from models import PracticeTest

def add_general_writing_task2_tests():
    """Add General Training Writing Task 2 tests."""
    print("Adding General Training Writing Task 2 tests...")
    
    # Dictionary of tests with titles and prompts
    general_task2_tests = [
        {
            "title": "Urban Traffic Solutions",
            "prompt": """Urban areas face increasing traffic problems. Some think building more roads is the answer, while others favor improving public transport.

Who do you believe should be the priority: expanding roads or developing public transport?

Give reasons for your view and include any relevant examples."""
        },
        {
            "title": "Remote Work Benefits and Drawbacks",
            "prompt": """Many companies are now allowing their employees to work from home some or all of the time. This shift has both benefits and drawbacks.

Do you think the advantages of remote work outweigh the disadvantages, or vice versa?

Provide reasons for your opinion and include any relevant examples."""
        },
        {
            "title": "Social Media Impact on Young People",
            "prompt": """The use of social media has become widespread among young people. It offers opportunities for connection but also presents potential risks.

Do you believe the benefits of social media for young people outweigh the risks, or are the risks more significant?

Support your view with reasons and any relevant examples."""
        },
        {
            "title": "Fast Food Benefits and Health Concerns",
            "prompt": """Fast food is a popular choice for many due to its convenience and affordability. However, its impact on health is often debated.

Do you think the advantages of fast food outweigh its disadvantages, or are the health concerns more significant?

Provide reasons for your opinion and include any relevant examples."""
        },
        {
            "title": "International Tourism Impacts",
            "prompt": """International tourism is a significant industry for many countries. It brings economic benefits but can also have negative impacts on local cultures and the environment.

Do you believe the advantages of international tourism outweigh its disadvantages, or are the negative impacts more concerning?

Support your view with reasons and any relevant examples."""
        },
        {
            "title": "Exams vs Continuous Assessment",
            "prompt": """In education, some argue that exams are the most effective way to assess student learning. Others suggest that continuous assessment throughout a course is a better approach.

Which method do you believe is a more effective way to evaluate student progress: exams or continuous assessment?

Give reasons for your opinion and include any relevant examples."""
        },
        {
            "title": "Artificial Intelligence Benefits and Risks",
            "prompt": """The increasing use of artificial intelligence (AI) is transforming many aspects of our lives, from work to entertainment. This technological advancement presents both opportunities and challenges.

Do you believe the potential benefits of AI outweigh the risks, or are the potential dangers more significant?

Support your view with reasons and include any relevant examples."""
        },
        {
            "title": "Online Shopping vs Traditional Retail",
            "prompt": """Many countries are experiencing a rise in the popularity of online shopping. This shift in consumer behavior has implications for traditional brick-and-mortar stores.

Do you believe the advantages of online shopping outweigh the disadvantages for consumers, or are the drawbacks more significant?

Provide reasons for your opinion and include any relevant examples."""
        },
        {
            "title": "Media Influence on Public Opinion",
            "prompt": """The media plays a significant role in shaping public opinion. Some argue that it provides valuable information, while others are concerned about its potential for bias.

Do you believe the positive contributions of the media outweigh its negative influences, or are the negative aspects more concerning?

Support your view with reasons and include any relevant examples."""
        },
        {
            "title": "Individual Freedom vs Government Regulation",
            "prompt": """In many societies, there's a debate about the appropriate balance between individual freedoms and the need for government regulation. Different viewpoints exist on how much intervention is necessary.

In your opinion, should governments prioritize individual freedoms or the need for regulation in society?

Give reasons for your view and include any relevant examples."""
        },
        {
            "title": "Globalization Impacts on Nations",
            "prompt": """The increasing globalization of the world economy has led to greater interconnectedness between nations. This has both created opportunities and presented challenges for individual countries.

Do you believe the advantages of globalization outweigh the disadvantages for individual countries, or are the negative impacts more significant?

Support your view with reasons and include any relevant examples."""
        },
        {
            "title": "Historical Artifacts: Origin vs Accessibility",
            "prompt": """The debate surrounding the ownership and preservation of historical artifacts is ongoing. Some believe they should remain in their country of origin, while others argue for their display in international museums.

In your opinion, is it more important for historical artifacts to be kept in their country of origin or to be accessible to a wider global audience in international museums?

Provide reasons for your view and include any relevant examples."""
        },
        {
            "title": "Waste Management Approaches",
            "prompt": """Many communities are facing decisions about how to manage waste. Some advocate for prioritizing recycling programs, while others believe that investing in waste-to-energy technologies is a better long-term solution.

Which approach do you believe is more effective for managing community waste: expanding recycling initiatives or developing waste-to-energy facilities?

Support your view with reasons and include any relevant examples."""
        },
        {
            "title": "Supporting Local Businesses",
            "prompt": """In many towns and cities, there's ongoing discussion about the best approach to support local businesses. Some favor providing financial grants and subsidies, while others believe in reducing regulations and taxes to foster growth.

Which strategy do you think is more effective for supporting local businesses: direct financial assistance or reducing regulatory burdens?

Provide reasons for your opinion and include any relevant examples."""
        },
        {
            "title": "Internet Access as Public Service",
            "prompt": """Access to reliable and affordable internet is becoming increasingly important. Some argue it should be considered a basic public service, like water or electricity, while others believe it should remain primarily a commercial service.

Do you believe that internet access should be classified as a basic public service or primarily a commercial service?

Give reasons for your opinion and include any relevant examples."""
        },
        {
            "title": "Technology in Education",
            "prompt": """The role of technology in education is a subject of much discussion. Some believe that increased use of digital devices enhances learning, while others worry about potential distractions and a decline in traditional skills.

Do you think the benefits of using technology in education outweigh the drawbacks, or are the potential negative impacts more significant?

Support your view with reasons and include any relevant examples."""
        }
    ]
    
    with app.app_context():
        # Check how many general task 2 tests we already have
        existing_count = PracticeTest.query.filter_by(
            test_type="writing", 
            ielts_test_type="general",
            section=2
        ).count()
        
        print(f"Found {existing_count} existing General Training Writing Task 2 tests")
            
        # Add each test to the database
        added_count = 0
        for idx, test_data in enumerate(general_task2_tests):
            # Skip tests we already have enough of
            if existing_count + added_count >= 16:
                print(f"We already have the required 16 General Training Writing Task 2 tests")
                break
                
            # Check if this test already exists by title
            existing_test = PracticeTest.query.filter_by(
                title=test_data["title"], 
                test_type="writing",
                ielts_test_type="general",
                section=2
            ).first()
            
            if existing_test:
                print(f"Test '{test_data['title']}' already exists, skipping...")
                continue
                
            # Create question structure
            questions = [
                {
                    "task": "Task 2",
                    "description": test_data["prompt"],
                    "instructions": "Write at least 250 words. You should spend about 40 minutes on this task."
                }
            ]
            
            # Create the new test
            new_test = PracticeTest(
                title=test_data["title"],
                description=f"General Training Writing Task 2 - {test_data['title']}",
                test_type="writing",
                ielts_test_type="general",
                section=2,  # Task 2
                _questions=json.dumps(questions),
                _answers=json.dumps(["This is a sample model answer structure. Actual assessment will be done by AI."]),
                is_free=False,
                time_limit=40  # 40 minutes
            )
            
            db.session.add(new_test)
            added_count += 1
            print(f"Added test '{test_data['title']}'")
            
        # Commit the changes
        db.session.commit()
        print(f"Successfully added {added_count} new General Training Writing Task 2 tests")
        print(f"Total General Training Writing Task 2 tests now: {existing_count + added_count}")

if __name__ == "__main__":
    with app.app_context():
        add_general_writing_task2_tests()