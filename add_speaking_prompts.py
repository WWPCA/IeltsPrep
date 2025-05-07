"""
Add speaking prompts to the database.
This script adds a variety of speaking prompts for both Academic and General Training.
"""

from main import app
from models import db, SpeakingPrompt

def add_speaking_prompts():
    """Add speaking prompts to cover a range of IELTS topics."""
    with app.app_context():
        # Check existing prompts to avoid duplicates
        existing_prompts = SpeakingPrompt.query.all()
        existing_texts = [p.prompt_text for p in existing_prompts]
        
        # Part 1 prompts - Introduction and interview
        part1_prompts = [
            # Work/Study
            "Tell me about your job. What responsibilities do you have?",
            "What do you like or dislike about your studies?",
            "Would you prefer to work in a large company or a small company? Why?",
            # Home/Accommodation
            "Can you describe the place where you live?",
            "What kind of accommodation do you live in?",
            "What changes would you like to make to your home?",
            # Hometown
            "Describe your hometown. What is it known for?",
            "Is your hometown a good place for tourists to visit? Why or why not?",
            "How has your hometown changed in recent years?",
            # Leisure
            "What activities do you enjoy doing in your free time?",
            "Do you prefer indoor or outdoor activities? Why?",
            "How important is it to have hobbies?",
            # Technology
            "How often do you use computers or technology in your daily life?",
            "What impact does technology have on your work or studies?",
            "Do you think people rely too much on technology nowadays?",
            # Travel
            "What kind of places do you like to visit on vacation?",
            "Do you prefer traveling alone or with other people? Why?",
            "What's the most interesting journey you've ever taken?"
        ]
        
        # Part 2 prompts - Individual long turn
        part2_prompts = [
            # People
            "Describe a person who has had a significant influence on your life. You should say:\nwho this person is\nhow you know them\nwhat they do\nand explain why they have influenced you so much.",
            "Describe a teacher who has influenced you. You should say:\nwhen you met them\nwhat subject they taught\nwhat was special about them\nand explain how they influenced your life.",
            "Describe a friend who is a good leader. You should say:\nwho the person is\nhow you know this person\nwhat leadership qualities they have\nand explain why you think they are a good leader.",
            # Places
            "Describe a public place you like to visit. You should say:\nwhere it is\nwhen you usually go there\nwhat you do there\nand explain why you like this place.",
            "Describe a historic building you have visited. You should say:\nwhere it is\nwhen you visited it\nwhat the building looks like\nand explain why you visited this building.",
            "Describe a place in your country that you would recommend someone visit. You should say:\nwhere it is\nwhat people can do there\nwhen is the best time to visit\nand explain why you would recommend this place.",
            # Objects
            "Describe an important object in your life. You should say:\nwhat it is\nhow long you've had it\nwhere you got it from\nand explain why it's important to you.",
            "Describe a piece of technology that you find useful. You should say:\nwhat it is\nwhat you use it for\nhow often you use it\nand explain why it is so useful to you.",
            "Describe a book that has influenced you. You should say:\nwhat kind of book it is\nwhat it is about\nwhen you first read it\nand explain how it has influenced you.",
            # Experiences
            "Describe a skill you would like to learn. You should say:\nwhat this skill is\nwhy you want to learn it\nhow you would learn it\nand explain how this skill would be useful to you in the future.",
            "Describe a time when you helped someone. You should say:\nwho you helped\nwhat you did\nwhy they needed help\nand explain how you felt about helping this person.",
            "Describe an important decision you have made. You should say:\nwhat the decision was\nwhen you made it\nwhy you made this decision\nand explain how this decision changed your life.",
            # Events
            "Describe a special event you attended. You should say:\nwhat the event was\nwhere and when it was held\nwho was there with you\nand explain why it was special to you.",
            "Describe a tradition in your country. You should say:\nwhat the tradition is\nwhen and how people celebrate it\nhow people prepare for it\nand explain what you like or dislike about this tradition.",
            "Describe a time when you had to work with a group. You should say:\nwhat you were working on\nwho you worked with\nhow long you worked together\nand explain how you felt about this experience."
        ]
        
        # Part 3 prompts - Discussion
        part3_prompts = [
            # Education
            "What changes do you think will happen in education in the future?",
            "Do you think students should be able to choose what they study at school?",
            "How important do you think it is for people to continue learning throughout their lives?",
            # Work
            "What factors should people consider when choosing a career?",
            "Do you think it's better to have one job for life or to change jobs regularly?",
            "How has technology changed the way people work in your country?",
            # Environment
            "What environmental problems does your country face today?",
            "Do you think individuals or governments should be responsible for protecting the environment?",
            "How can we encourage more people to use public transportation instead of cars?",
            # Technology
            "How might technology change the way we live in the future?",
            "Do social media platforms bring people together or push them further apart?",
            "Should there be more regulation of technology and the internet?",
            # Society
            "How has family life changed in your country in recent decades?",
            "What role should governments play in healthcare and social services?",
            "Is it better to live in a city or in the countryside? Why?",
            # Global issues
            "How can countries work together more effectively to solve global problems?",
            "What do you think are the biggest challenges facing young people today?",
            "Do you think international tourism is mostly positive or negative for local communities?"
        ]
        
        # Add prompts to database
        added_count = 0
        
        for prompt_text in part1_prompts:
            if prompt_text not in existing_texts:
                prompt = SpeakingPrompt(
                    part=1,
                    prompt_text=prompt_text
                )
                db.session.add(prompt)
                added_count += 1
        
        for prompt_text in part2_prompts:
            if prompt_text not in existing_texts:
                prompt = SpeakingPrompt(
                    part=2,
                    prompt_text=prompt_text
                )
                db.session.add(prompt)
                added_count += 1
        
        for prompt_text in part3_prompts:
            if prompt_text not in existing_texts:
                prompt = SpeakingPrompt(
                    part=3,
                    prompt_text=prompt_text
                )
                db.session.add(prompt)
                added_count += 1
        
        db.session.commit()
        
        print(f"Added {added_count} new speaking prompts.")
        
        # Print counts by part
        part1_count = SpeakingPrompt.query.filter_by(part=1).count()
        part2_count = SpeakingPrompt.query.filter_by(part=2).count()
        part3_count = SpeakingPrompt.query.filter_by(part=3).count()
        
        print(f"Part 1 Prompts: {part1_count}")
        print(f"Part 2 Prompts: {part2_count}")
        print(f"Part 3 Prompts: {part3_count}")
        print(f"Total Prompts: {part1_count + part2_count + part3_count}")

if __name__ == "__main__":
    add_speaking_prompts()
