"""
Check the speaking prompts in the database.
"""
from app import app, db
from models import SpeakingPrompt

def check_speaking_prompts():
    """Check the availability of speaking prompts in the database."""
    with app.app_context():
        prompt_count = SpeakingPrompt.query.count()
        print(f"Number of speaking prompts available: {prompt_count}")
        
        if prompt_count > 0:
            prompts = SpeakingPrompt.query.all()
            print("\nAvailable speaking prompts:")
            for prompt in prompts:
                print(f"Part {prompt.part}: {prompt.prompt_text[:50]}...")
        else:
            print("No speaking prompts found in the database.")

if __name__ == "__main__":
    check_speaking_prompts()