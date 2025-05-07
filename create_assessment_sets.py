"""
Create product assessment sets for IELTS AI Prep.
This script creates four assessment products:
1. Academic Writing
2. Academic Speaking
3. General Training Writing
4. General Training Speaking

Each product includes 4 sets of assessments.
"""

from main import app
from models import db, PracticeTest, CompletePracticeTest, SpeakingPrompt
import random
import json

def create_assessment_sets():
    """Create assessment product sets based on existing content."""
    with app.app_context():
        print("Creating assessment product sets...")
        
        # Create Academic Writing product sets
        create_academic_writing_sets()
        
        # Create Academic Speaking product sets
        create_academic_speaking_sets()
        
        # Create General Training Writing product sets
        create_general_writing_sets()
        
        # Create General Training Speaking product sets
        create_general_speaking_sets()
        
        print("Assessment product sets created successfully.")

def create_academic_writing_sets():
    """Create Academic Writing assessment sets."""
    # Get Academic Writing Task 1 tests
    task1_tests = PracticeTest.query.filter_by(
        test_type='writing',
        ielts_test_type='academic',
        section=1
    ).all()
    
    # Get Academic Writing Task 2 tests
    task2_tests = PracticeTest.query.filter_by(
        test_type='writing',
        ielts_test_type='academic',
        section=2
    ).all()
    
    # Check if we have enough tests
    if len(task1_tests) < 4 or len(task2_tests) < 4:
        print(f"Not enough Academic Writing tests (Task1: {len(task1_tests)}, Task2: {len(task2_tests)})")
        return
    
    # Select 4 sets of Task 1 and Task 2 tests
    task1_selection = task1_tests[:4] if len(task1_tests) >= 4 else task1_tests
    task2_selection = task2_tests[:4] if len(task2_tests) >= 4 else task2_tests
    
    # Create 4 complete test sets
    for i in range(min(4, len(task1_selection), len(task2_selection))):
        # Check if the set already exists
        existing_set = CompletePracticeTest.query.filter_by(
            title=f"Academic Writing Assessment Set {i+1}",
            product_type='academic_writing'
        ).first()
        
        if existing_set:
            print(f"Academic Writing Assessment Set {i+1} already exists. Skipping.")
            continue
        
        # Create a new complete test set
        complete_test = CompletePracticeTest(
            title=f"Academic Writing Assessment Set {i+1}",
            description="Complete Academic Writing assessment with Task 1 and Task 2",
            ielts_test_type='academic',
            product_type='academic_writing',  # Custom type for product
            status='active',
            is_free=False
        )
        
        db.session.add(complete_test)
        db.session.flush()  # Get ID without committing
        
        # Add the tests to the set
        task1_test = task1_selection[i]
        task2_test = task2_selection[i]
        
        complete_test.tests = json.dumps([
            {"test_id": task1_test.id, "test_type": "writing", "part": 1},
            {"test_id": task2_test.id, "test_type": "writing", "part": 2}
        ])
        
        print(f"Created Academic Writing Assessment Set {i+1}")
    
    # Commit changes
    db.session.commit()

def create_academic_speaking_sets():
    """Create Academic Speaking assessment sets."""
    # Get Speaking prompts for all parts
    part1_prompts = SpeakingPrompt.query.filter_by(part=1).all()
    part2_prompts = SpeakingPrompt.query.filter_by(part=2).all()
    part3_prompts = SpeakingPrompt.query.filter_by(part=3).all()
    
    # Check if we have enough prompts
    if len(part1_prompts) < 4 or len(part2_prompts) < 4 or len(part3_prompts) < 4:
        print(f"Not enough Speaking prompts (Part1: {len(part1_prompts)}, Part2: {len(part2_prompts)}, Part3: {len(part3_prompts)})")
        return
    
    # Select 4 sets of prompts (or shuffle and take first 4)
    random.shuffle(part1_prompts)
    random.shuffle(part2_prompts)
    random.shuffle(part3_prompts)
    
    part1_selection = part1_prompts[:4]
    part2_selection = part2_prompts[:4]
    part3_selection = part3_prompts[:4]
    
    # Create 4 complete speaking assessment sets
    for i in range(4):
        # Check if the set already exists
        existing_set = CompletePracticeTest.query.filter_by(
            title=f"Academic Speaking Assessment Set {i+1}",
            product_type='academic_speaking'
        ).first()
        
        if existing_set:
            print(f"Academic Speaking Assessment Set {i+1} already exists. Skipping.")
            continue
        
        # Create a new complete test set
        complete_test = CompletePracticeTest(
            title=f"Academic Speaking Assessment Set {i+1}",
            description="Complete Academic Speaking assessment with all three parts",
            ielts_test_type='academic',
            product_type='academic_speaking',  # Custom type for product
            status='active',
            is_free=False
        )
        
        db.session.add(complete_test)
        db.session.flush()  # Get ID without committing
        
        # Store prompt IDs in the set
        complete_test.tests = json.dumps([
            {"prompt_id": part1_selection[i].id, "part": 1},
            {"prompt_id": part2_selection[i].id, "part": 2},
            {"prompt_id": part3_selection[i].id, "part": 3}
        ])
        
        print(f"Created Academic Speaking Assessment Set {i+1}")
    
    # Commit changes
    db.session.commit()

def create_general_writing_sets():
    """Create General Training Writing assessment sets."""
    # Get General Writing Task 1 tests
    task1_tests = PracticeTest.query.filter_by(
        test_type='writing',
        ielts_test_type='general',
        section=1
    ).all()
    
    # Get General Writing Task 2 tests
    task2_tests = PracticeTest.query.filter_by(
        test_type='writing',
        ielts_test_type='general',
        section=2
    ).all()
    
    # Check if we have enough tests
    if len(task1_tests) < 4 or len(task2_tests) < 4:
        print(f"Not enough General Writing tests (Task1: {len(task1_tests)}, Task2: {len(task2_tests)})")
        return
    
    # Select 4 sets of Task 1 and Task 2 tests
    task1_selection = task1_tests[:4] if len(task1_tests) >= 4 else task1_tests
    task2_selection = task2_tests[:4] if len(task2_tests) >= 4 else task2_tests
    
    # Create 4 complete test sets
    for i in range(min(4, len(task1_selection), len(task2_selection))):
        # Check if the set already exists
        existing_set = CompletePracticeTest.query.filter_by(
            title=f"General Training Writing Assessment Set {i+1}",
            product_type='general_writing'
        ).first()
        
        if existing_set:
            print(f"General Training Writing Assessment Set {i+1} already exists. Skipping.")
            continue
        
        # Create a new complete test set
        complete_test = CompletePracticeTest(
            title=f"General Training Writing Assessment Set {i+1}",
            description="Complete General Training Writing assessment with Task 1 and Task 2",
            ielts_test_type='general',
            product_type='general_writing',  # Custom type for product
            status='active',
            is_free=False
        )
        
        db.session.add(complete_test)
        db.session.flush()  # Get ID without committing
        
        # Add the tests to the set
        task1_test = task1_selection[i]
        task2_test = task2_selection[i]
        
        complete_test.tests = json.dumps([
            {"test_id": task1_test.id, "test_type": "writing", "part": 1},
            {"test_id": task2_test.id, "test_type": "writing", "part": 2}
        ])
        
        print(f"Created General Training Writing Assessment Set {i+1}")
    
    # Commit changes
    db.session.commit()

def create_general_speaking_sets():
    """Create General Training Speaking assessment sets."""
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
    
    # Create 4 complete speaking assessment sets
    for i in range(4):
        # Check if the set already exists
        existing_set = CompletePracticeTest.query.filter_by(
            title=f"General Training Speaking Assessment Set {i+1}",
            product_type='general_speaking'
        ).first()
        
        if existing_set:
            print(f"General Training Speaking Assessment Set {i+1} already exists. Skipping.")
            continue
        
        # Create a new complete test set
        complete_test = CompletePracticeTest(
            title=f"General Training Speaking Assessment Set {i+1}",
            description="Complete General Training Speaking assessment with all three parts",
            ielts_test_type='general',
            product_type='general_speaking',  # Custom type for product
            status='active',
            is_free=False
        )
        
        db.session.add(complete_test)
        db.session.flush()  # Get ID without committing
        
        # Store prompt IDs in the set
        complete_test.tests = json.dumps([
            {"prompt_id": part1_selection[i].id, "part": 1},
            {"prompt_id": part2_selection[i].id, "part": 2},
            {"prompt_id": part3_selection[i].id, "part": 3}
        ])
        
        print(f"Created General Training Speaking Assessment Set {i+1}")
    
    # Commit changes
    db.session.commit()

if __name__ == "__main__":
    create_assessment_sets()