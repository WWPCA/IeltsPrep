"""
Create General Training Speaking assessment sets.
This script creates the remaining general speaking sets that weren't created before.
"""

from main import app
from models import db, CompletePracticeTest, SpeakingPrompt
import random
import json

def create_general_speaking_sets():
    """Create General Training Speaking assessment sets."""
    with app.app_context():
        # Get Speaking prompts for all parts
        part1_prompts = SpeakingPrompt.query.filter_by(part=1).all()
        part2_prompts = SpeakingPrompt.query.filter_by(part=2).all()
        part3_prompts = SpeakingPrompt.query.filter_by(part=3).all()
        
        # Check if we have enough prompts
        if len(part1_prompts) < 4 or len(part2_prompts) < 4 or len(part3_prompts) < 4:
            print(f"Not enough Speaking prompts (Part1: {len(part1_prompts)}, Part2: {len(part2_prompts)}, Part3: {len(part3_prompts)})")
            return
        
        # Select 4 sets of prompts (or shuffle and take first 4)
        # Use different prompts than academic if possible
        random.shuffle(part1_prompts)
        random.shuffle(part2_prompts)
        random.shuffle(part3_prompts)
        
        part1_selection = part1_prompts[4:8] if len(part1_prompts) >= 8 else part1_prompts[:4]
        part2_selection = part2_prompts[4:8] if len(part2_prompts) >= 8 else part2_prompts[:4]
        part3_selection = part3_prompts[4:8] if len(part3_prompts) >= 8 else part3_prompts[:4]
        
        # Check which sets already exist
        existing_sets = CompletePracticeTest.query.filter_by(
            product_type='general_speaking'
        ).all()
        
        existing_set_numbers = [int(s.title.split()[-1]) for s in existing_sets if s.title.split()[-1].isdigit()]
        
        for i in range(1, 5):
            if i in existing_set_numbers:
                print(f"General Training Speaking Assessment Set {i} already exists. Skipping.")
                continue
            
            # Create a new complete test set
            complete_test = CompletePracticeTest(
                title=f"General Training Speaking Assessment Set {i}",
                description="Complete General Training Speaking assessment with all three parts",
                ielts_test_type='general',
                product_type='general_speaking',
                status='active',
                is_free=False
            )
            
            db.session.add(complete_test)
            db.session.flush()  # Get ID without committing
            
            # Store prompt IDs in the set
            complete_test.tests = json.dumps([
                {"prompt_id": part1_selection[i-1].id, "part": 1},
                {"prompt_id": part2_selection[i-1].id, "part": 2},
                {"prompt_id": part3_selection[i-1].id, "part": 3}
            ])
            
            print(f"Created General Training Speaking Assessment Set {i}")
        
        # Commit changes
        db.session.commit()
        
        print("General Training Speaking assessment sets created successfully.")

if __name__ == "__main__":
    create_general_speaking_sets()