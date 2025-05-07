"""
Export test data to JSON files for backup.
This script exports all test content from the database to JSON files.
"""

import os
import json
from main import app
from models import db, PracticeTest, SpeakingPrompt, CompletePracticeTest

def backup_database():
    """Export all test data to JSON files for backup."""
    
    backup_dir = "database_backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    with app.app_context():
        # 1. Export Reading Tests
        reading_tests = PracticeTest.query.filter(PracticeTest.test_type.like('%reading%')).all()
        reading_data = []
        for test in reading_tests:
            reading_data.append({
                'id': test.id,
                'test_type': test.test_type,
                'title': test.title,
                'description': test.description,
                'content': test.content,
                'answers': test.answers,
                'instructions': test.instructions,
                'difficulty': test.difficulty,
                'time_limit': test.time_limit,
                'is_premium': test.is_premium,
                'section': test.section if hasattr(test, 'section') else None
            })
        
        with open(os.path.join(backup_dir, 'reading_tests.json'), 'w') as f:
            json.dump(reading_data, f, indent=2)
        
        print(f"Exported {len(reading_data)} reading tests")
        
        # 2. Export Writing Tests
        writing_tests = PracticeTest.query.filter(PracticeTest.test_type.like('%writing%')).all()
        writing_data = []
        for test in writing_tests:
            writing_data.append({
                'id': test.id,
                'test_type': test.test_type,
                'title': test.title,
                'description': test.description,
                'content': test.content,
                'answers': test.answers,
                'instructions': test.instructions,
                'difficulty': test.difficulty,
                'time_limit': test.time_limit,
                'is_premium': test.is_premium
            })
        
        with open(os.path.join(backup_dir, 'writing_tests.json'), 'w') as f:
            json.dump(writing_data, f, indent=2)
        
        print(f"Exported {len(writing_data)} writing tests")
        
        # 3. Export Speaking Prompts
        speaking_prompts = SpeakingPrompt.query.all()
        speaking_data = []
        for prompt in speaking_prompts:
            speaking_data.append({
                'id': prompt.id,
                'test_type': prompt.test_type,
                'part': prompt.part,
                'prompt_text': prompt.prompt_text,
                'topic': prompt.topic,
                'follow_up_questions': prompt.follow_up_questions,
                'difficulty': prompt.difficulty,
                'is_premium': prompt.is_premium
            })
        
        with open(os.path.join(backup_dir, 'speaking_prompts.json'), 'w') as f:
            json.dump(speaking_data, f, indent=2)
        
        print(f"Exported {len(speaking_data)} speaking prompts")
        
        # 4. Export Listening Tests
        listening_tests = PracticeTest.query.filter(PracticeTest.test_type.like('%listening%')).all()
        listening_data = []
        for test in listening_tests:
            listening_data.append({
                'id': test.id,
                'test_type': test.test_type,
                'title': test.title,
                'description': test.description,
                'content': test.content,
                'answers': test.answers,
                'instructions': test.instructions,
                'difficulty': test.difficulty,
                'time_limit': test.time_limit,
                'is_premium': test.is_premium,
                'audio_url': test.audio_url if hasattr(test, 'audio_url') else None,
                'transcript': test.transcript if hasattr(test, 'transcript') else None
            })
        
        with open(os.path.join(backup_dir, 'listening_tests.json'), 'w') as f:
            json.dump(listening_data, f, indent=2)
        
        print(f"Exported {len(listening_data)} listening tests")
        
        # 5. Export Complete Tests and Assessment Sets
        complete_tests = CompletePracticeTest.query.all()
        complete_data = []
        assessment_data = []
        
        for test in complete_tests:
            test_data = {
                'id': test.id,
                'title': test.title,
                'description': test.description,
                'test_type': test.test_type,
                'is_premium': test.is_premium,
                'reading_id': test.reading_id,
                'writing_id': test.writing_id,
                'listening_id': test.listening_id,
                'speaking_ids': test.speaking_ids,
                'test_number': test.test_number
            }
            
            # Check if this is an assessment set
            if hasattr(test, 'product_type') and test.product_type:
                test_data['product_type'] = test.product_type
                test_data['status'] = test.status if hasattr(test, 'status') else 'active'
                test_data['_tests'] = test._tests if hasattr(test, '_tests') else None
                assessment_data.append(test_data)
            else:
                complete_data.append(test_data)
        
        with open(os.path.join(backup_dir, 'complete_tests.json'), 'w') as f:
            json.dump(complete_data, f, indent=2)
        
        with open(os.path.join(backup_dir, 'assessment_sets.json'), 'w') as f:
            json.dump(assessment_data, f, indent=2)
        
        print(f"Exported {len(complete_data)} complete tests")
        print(f"Exported {len(assessment_data)} assessment sets")
    
    print(f"\nAll test data exported to the '{backup_dir}' directory")

if __name__ == "__main__":
    backup_database()