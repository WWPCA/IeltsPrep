"""
Check Speaking tests in the database.
"""
from main import app
from models import PracticeTest, db, SpeakingPrompt

def check_speaking_tests():
    """Check the Speaking tests in the database."""
    with app.app_context():
        # Query all speaking tests
        speaking_tests = PracticeTest.query.filter_by(
            test_type='speaking'
        ).order_by(PracticeTest.id).all()
        
        # Count by test type
        academic_tests = [t for t in speaking_tests if t.ielts_test_type == 'academic']
        general_tests = [t for t in speaking_tests if t.ielts_test_type == 'general']
        
        print(f"Total Speaking Tests: {len(speaking_tests)}")
        print(f"Academic Speaking Tests: {len(academic_tests)}")
        print(f"General Speaking Tests: {len(general_tests)}")
        
        # Show sample of each
        print("\nSample Academic Speaking Tests:")
        for test in academic_tests[:5]:
            print(f"ID: {test.id}, Title: {test.title}, Section: {test.section}")
            
        print("\nSample General Speaking Tests:")
        for test in general_tests[:5]:
            print(f"ID: {test.id}, Title: {test.title}, Section: {test.section}")
            
        # Check speaking prompts
        speaking_prompts = SpeakingPrompt.query.all()
        print(f"\nTotal Speaking Prompts: {len(speaking_prompts)}")
        
        # Count prompts by part
        part1_prompts = SpeakingPrompt.query.filter_by(part=1).count()
        part2_prompts = SpeakingPrompt.query.filter_by(part=2).count()
        part3_prompts = SpeakingPrompt.query.filter_by(part=3).count()
        
        print(f"Part 1 Prompts: {part1_prompts}")
        print(f"Part 2 Prompts: {part2_prompts}")
        print(f"Part 3 Prompts: {part3_prompts}")
        
        # Show samples of each prompt type
        print("\nSample Part 1 Prompts:")
        part1_examples = SpeakingPrompt.query.filter_by(part=1).limit(3).all()
        for prompt in part1_examples:
            # Limit text to avoid long output
            text_sample = prompt.prompt_text[:100] + "..." if len(prompt.prompt_text) > 100 else prompt.prompt_text
            print(f"ID: {prompt.id}, Text: {text_sample}")
            
        print("\nSample Part 2 Prompts:")
        part2_examples = SpeakingPrompt.query.filter_by(part=2).limit(3).all()
        for prompt in part2_examples:
            text_sample = prompt.prompt_text[:100] + "..." if len(prompt.prompt_text) > 100 else prompt.prompt_text
            print(f"ID: {prompt.id}, Text: {text_sample}")
            
        print("\nSample Part 3 Prompts:")
        part3_examples = SpeakingPrompt.query.filter_by(part=3).limit(3).all()
        for prompt in part3_examples:
            text_sample = prompt.prompt_text[:100] + "..." if len(prompt.prompt_text) > 100 else prompt.prompt_text
            print(f"ID: {prompt.id}, Text: {text_sample}")

if __name__ == "__main__":
    check_speaking_tests()
