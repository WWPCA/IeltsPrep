"""
Add Academic Writing Task 2 tests to the IELTS preparation app.
This script adds essay writing tasks for Academic candidates from the provided list.
"""
import sys
from datetime import datetime
from flask import Flask
from models import db, PracticeTest, TestSection, TestType
from app import app

def add_academic_writing_task2_tests():
    """Add Academic Writing Task 2 tests."""
    print("Adding Academic Writing Task 2 tests...")
    
    # Dictionary of tests with titles and prompts
    academic_task2_tests = [
        {
            "title": "Global Economy and Career Evolution",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The global economy is evolving quickly, and individuals can no longer rely on the same career path or workplace environment throughout their lives.

Discuss the potential reasons for this rapid evolution, and propose strategies to prepare people for their careers in the future.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Aging Population Demographics",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

Many countries are experiencing a significant increase in the proportion of older people in their populations.

Discuss the possible reasons for this demographic shift, and suggest ways in which societies can adapt to this aging population.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Private Vehicles and Environmental Concerns",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

In many parts of the world, the popularity of private vehicles is increasing despite growing concerns about environmental pollution and traffic congestion.

Discuss the possible reasons for the continued preference for private vehicles, and suggest ways in which governments could encourage people to use alternative forms of transport.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Social Media's Impact on Communication",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing availability and influence of social media have fundamentally changed the way people communicate and form relationships.

Discuss the potential benefits and drawbacks of this development, and suggest ways individuals and societies can navigate the impact of social media in the future.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Tourism in Urban Areas",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

Many cities around the world are experiencing increasing pressure from tourism, which can have both positive and negative effects on local communities and environments.

Discuss the potential benefits and drawbacks of mass tourism in urban areas, and suggest ways in which cities can manage tourism more sustainably in the future.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Standardized Testing in Education",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The reliance on standardized testing as the primary method for evaluating student performance and determining educational opportunities is a subject of ongoing debate.

Discuss the potential advantages and disadvantages of standardized testing in education, and suggest alternative methods that could be used to assess student learning and potential.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Fast Food Consumption Trends",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing consumption of fast food and processed meals is a growing trend in many developed nations.

Discuss the possible reasons for the popularity of these types of food, and suggest ways in which individuals and governments could encourage healthier eating habits.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Preservation of Endangered Languages",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The preservation of endangered languages is becoming an increasingly urgent issue in many parts of the world.

Discuss the possible reasons why languages become endangered, and suggest ways in which individuals and governments could work to protect and promote these languages.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Privacy vs. Security in the Digital Age",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The balance between protecting individual privacy and ensuring national security is a complex issue facing governments worldwide in the digital age.

Discuss the potential challenges and benefits of increased surveillance measures, and suggest ways in which societies can strive to find a more equitable balance between these two important considerations.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Globalization and International Travel",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing globalization of the economy has led to a significant rise in international travel for both work and leisure.

Discuss the potential advantages and disadvantages of this increased global mobility, and suggest ways in which individuals and organizations can maximize the benefits while mitigating the drawbacks.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Automation and the Future of Employment",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing automation of tasks in various industries is raising concerns about potential job displacement and the future of employment.

Discuss the possible impacts of widespread automation on the workforce, and suggest ways in which individuals and governments can prepare for and adapt to these changes in the job market.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Online Education vs. Traditional Learning",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The growing popularity of online education has presented both opportunities and challenges for students and educational institutions.

Discuss the potential benefits and drawbacks of online learning compared to traditional face-to-face education, and suggest ways in which online learning can be made more effective in the future.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Global Information Exchange",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing interconnectedness of the world through the internet has led to a significant rise in the sharing of information and ideas across borders.

Discuss the potential advantages and disadvantages of this increased global exchange of information, and suggest ways in which individuals and societies can navigate this digital landscape responsibly and effectively.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Academic Pressure on Young People",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing emphasis on academic achievement and the pressure to succeed in education are affecting young people in many societies.

Discuss the potential causes of this growing pressure on students, and suggest ways in which parents, educators, and societies can create a more balanced and supportive learning environment for young people.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Adoption of Sustainable Practices",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing awareness of environmental issues has led to calls for individuals and businesses to adopt more sustainable practices.

Discuss the possible reasons why the adoption of sustainable practices is not more widespread, and suggest ways in which individuals, businesses, and governments could be encouraged to act more sustainably.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        },
        {
            "title": "Streaming Services and Entertainment Consumption",
            "prompt": """Part 2
You should spend about 40 minutes on this task. Write at least 250 words.

Write about the following topic:

The increasing popularity of streaming services has significantly altered the way people consume entertainment, particularly music and television.

Discuss the potential benefits and drawbacks of this shift towards on-demand entertainment, and suggest ways in which artists and traditional media companies can adapt to this changing landscape.

Give reasons for your answer and include any relevant examples from your own knowledge or experience."""
        }
    ]
    
    with app.app_context():
        # Get the academic test type
        academic_type = TestType.query.filter_by(name="academic").first()
        
        if not academic_type:
            print("Error: Academic test type not found in the database")
            return
            
        # Get the TestSection for Writing Task 2
        writing_section = TestSection.query.filter_by(name="Writing", section_number=2).first()
        
        if not writing_section:
            print("Error: Writing Task 2 section not found in the database")
            return
            
        # Check how many academic task 2 tests we already have
        existing_count = PracticeTest.query.filter_by(
            test_type_id=academic_type.id, 
            section=2,
            test_section_id=writing_section.id
        ).count()
        
        print(f"Found {existing_count} existing Academic Writing Task 2 tests")
            
        # Add each test to the database
        added_count = 0
        for idx, test_data in enumerate(academic_task2_tests):
            # Skip tests we already have enough of
            if existing_count + added_count >= 16:
                print(f"We already have the required 16 Academic Writing Task 2 tests")
                break
                
            # Check if this test already exists by title
            existing_test = PracticeTest.query.filter_by(
                title=test_data["title"], 
                test_type_id=academic_type.id,
                section=2
            ).first()
            
            if existing_test:
                print(f"Test '{test_data['title']}' already exists, skipping...")
                continue
                
            # Create the new test
            new_test = PracticeTest(
                title=test_data["title"],
                description=f"Academic Writing Task 2 - {test_data['title']}",
                content=test_data["prompt"],
                test_type_id=academic_type.id,
                test_section_id=writing_section.id,
                section=2,  # Task 2
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(new_test)
            added_count += 1
            print(f"Added test '{test_data['title']}'")
            
        # Commit the changes
        db.session.commit()
        print(f"Successfully added {added_count} new Academic Writing Task 2 tests")
        print(f"Total Academic Writing Task 2 tests now: {existing_count + added_count}")

if __name__ == "__main__":
    with app.app_context():
        add_academic_writing_task2_tests()