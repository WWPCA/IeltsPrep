"""
List all speaking prompts in the database.
"""
from main import app
from models import SpeakingPrompt

def list_all_speaking_prompts():
    """List all speaking prompts in the database."""
    with app.app_context():
        # Get all prompts
        prompts = SpeakingPrompt.query.order_by(SpeakingPrompt.part, SpeakingPrompt.id).all()
        
        print(f"Total Speaking Prompts: {len(prompts)}")
        
        print("\nALL SPEAKING PROMPTS:")
        for prompt in prompts:
            print(f"ID: {prompt.id}, Part: {prompt.part}")
            print(f"Text: {prompt.prompt_text}")
            print("-" * 50)

if __name__ == "__main__":
    list_all_speaking_prompts()
