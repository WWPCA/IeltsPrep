import os
from app import app, db
from models import WritingTest

def add_outdoor_adventure_test():
    """Add a new academic writing test with outdoor adventure activities graph."""
    with app.app_context():
        # Check if test already exists
        test = WritingTest.query.filter_by(
            title='Academic Writing Task 1: Outdoor Adventure Activities Bar Chart'
        ).first()
        
        action = "Creating new" if not test else "Updating existing"
        print(f"{action} 'Outdoor Adventure Activities' writing test...")
        
        if not test:
            test = WritingTest()
        
        # Set test details
        test.test_type = "academic"
        test.title = "Academic Writing Task 1: Outdoor Adventure Activities Bar Chart"
        test.instructions = """The chart below shows the number of adults participating in different outdoor adventure activities in one area, in 2021 and 2031.

Summarise the key trends in adult participation in these outdoor adventure activities over the 10-year period and provide relevant comparisons between the two years."""
        test.time_limit = 20
        test.min_words = 150
        test.max_words = 200
        test.graph_image = "static/images/writing_graphs/outdoor_adventure_activities_2021_2031.png"
        test.answer_type = "essay"
        test.band_descriptors = """
**Task Achievement (25%)**
- Fully satisfies all requirements of the task
- Clearly presents an overview of main trends
- Presents key features with relevant detail
- Uses data appropriately to support analysis

**Coherence and Cohesion (25%)**
- Logically organizes information and ideas
- Clear progression throughout
- Uses cohesive devices effectively
- Uses paragraphing appropriately

**Lexical Resource (25%)**
- Uses a wide range of vocabulary with flexibility and precision
- Uses uncommon items naturally with occasional inaccuracies
- Makes rare spelling and/or word formation errors

**Grammatical Range and Accuracy (25%)**
- Uses a wide range of structures with flexibility and accuracy
- Makes rare grammatical errors
- Demonstrates good control of grammar and punctuation
"""
        test.sample_answer = """The graph compares adult participation in five outdoor adventure activities in an area over a ten-year period from 2021 to 2031.

Overall, rock climbing and mountain biking saw substantial increases in participation over the decade, while kayaking experienced a notable decline. Zip lining remained relatively stable, and paragliding showed modest growth.

Rock climbing demonstrated the most significant growth, increasing from 25,000 participants in 2021 to 35,000 by 2031, representing a 40% rise. Similarly, mountain biking nearly doubled from 15,000 to 28,000 participants. In contrast, kayaking decreased considerably from 30,000 to 25,000 participants during this period.

Zip lining remained essentially unchanged with approximately 20,000 participants in both years. Meanwhile, paragliding showed a moderate increase from 10,000 to 14,000 participants. By 2031, rock climbing had become the most popular activity, whereas in 2021, kayaking had held that position.
"""
        test.assessment_criteria = "This essay will be evaluated on task achievement, coherence and cohesion, lexical resource, and grammatical range and accuracy according to IELTS Writing Task 1 band descriptors."
        
        # Save to database
        if not test.id:
            db.session.add(test)
        db.session.commit()
        
        print("Outdoor Adventure Activities writing test added/updated successfully!")

if __name__ == "__main__":
    add_outdoor_adventure_test()