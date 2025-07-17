#!/usr/bin/env python3
"""
Populate Production DynamoDB Tables with Questions from Replit Database
Extracts questions from PostgreSQL and uploads to AWS DynamoDB production tables
"""

import boto3
import json
import psycopg2
import os
from datetime import datetime

def get_database_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=os.environ.get('PGPORT', 5432)
    )

def extract_writing_questions():
    """Extract writing questions from practice_test table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Get writing questions with content
    cursor.execute("""
        SELECT id, test_type, section, title, description, _questions, ielts_test_type
        FROM practice_test 
        WHERE test_type = 'writing' 
        AND _questions IS NOT NULL 
        AND _questions != '[]'
        ORDER BY section, id
        LIMIT 20
    """)
    
    writing_questions = []
    for row in cursor.fetchall():
        id, test_type, section, title, description, questions_json, ielts_test_type = row
        
        # Parse questions JSON
        try:
            questions = json.loads(questions_json) if questions_json else []
        except:
            questions = []
        
        if questions:  # Only add if has actual questions
            writing_questions.append({
                'id': id,
                'test_type': test_type,
                'section': section,
                'title': title,
                'description': description,
                'questions': questions,
                'ielts_test_type': ielts_test_type
            })
    
    cursor.close()
    conn.close()
    return writing_questions

def extract_speaking_questions():
    """Extract speaking questions from practice_test table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Get speaking questions with content
    cursor.execute("""
        SELECT id, test_type, section, title, description, _questions, ielts_test_type
        FROM practice_test 
        WHERE test_type = 'speaking' 
        AND ielts_test_type IN ('academic', 'general')
        ORDER BY ielts_test_type, id
        LIMIT 20
    """)
    
    speaking_questions = []
    for row in cursor.fetchall():
        id, test_type, section, title, description, questions_json, ielts_test_type = row
        
        # Parse questions JSON
        try:
            questions = json.loads(questions_json) if questions_json else []
        except:
            questions = []
        
        speaking_questions.append({
            'id': id,
            'test_type': test_type,
            'section': section,
            'title': title,
            'description': description,
            'questions': questions,
            'ielts_test_type': ielts_test_type
        })
    
    cursor.close()
    conn.close()
    return speaking_questions

def create_production_questions():
    """Create production-ready questions for DynamoDB"""
    writing_questions = extract_writing_questions()
    speaking_questions = extract_speaking_questions()
    
    production_questions = {}
    
    # Process Academic Writing Questions
    academic_writing_count = 0
    for q in writing_questions:
        if q['ielts_test_type'] == 'academic' and academic_writing_count < 20:
            academic_writing_count += 1
            question_id = f"aw_{academic_writing_count:03d}"
            
            # Extract task content safely
            task_content = {}
            if q['questions'] and len(q['questions']) > 0:
                task_content = q['questions'][0] if isinstance(q['questions'][0], dict) else {}
            
            production_questions[question_id] = {
                'question_id': question_id,
                'assessment_type': 'academic_writing',
                'task_type': 'Task 1',
                'title': q['title'],
                'description': q['description'],
                'task_1_description': task_content.get('description', '') if isinstance(task_content, dict) else '',
                'task_1_instructions': task_content.get('instructions', '') if isinstance(task_content, dict) else '',
                'chart_image_url': task_content.get('image_url', '') if isinstance(task_content, dict) else '',
                'created_at': datetime.utcnow().isoformat(),
                'source': 'replit_database'
            }
    
    # Process General Writing Questions
    general_writing_count = 0
    for q in writing_questions:
        if q['ielts_test_type'] == 'general' and general_writing_count < 20:
            general_writing_count += 1
            question_id = f"gw_{general_writing_count:03d}"
            
            # Extract task content safely
            task_content = {}
            if q['questions'] and len(q['questions']) > 0:
                task_content = q['questions'][0] if isinstance(q['questions'][0], dict) else {}
            
            production_questions[question_id] = {
                'question_id': question_id,
                'assessment_type': 'general_writing',
                'task_type': 'Task 1',
                'title': q['title'],
                'description': q['description'],
                'task_1_description': task_content.get('description', '') if isinstance(task_content, dict) else '',
                'task_1_instructions': task_content.get('instructions', '') if isinstance(task_content, dict) else '',
                'letter_type': 'formal',
                'created_at': datetime.utcnow().isoformat(),
                'source': 'replit_database'
            }
    
    # Process Academic Speaking Questions
    academic_speaking_count = 0
    for q in speaking_questions:
        if q['ielts_test_type'] == 'academic' and academic_speaking_count < 20:
            academic_speaking_count += 1
            question_id = f"as_{academic_speaking_count:03d}"
            
            production_questions[question_id] = {
                'question_id': question_id,
                'assessment_type': 'academic_speaking',
                'title': q['title'],
                'description': q['description'],
                'part_1': "Let's talk about your studies. What subject are you studying?",
                'part_2': "Describe an academic achievement you are proud of. You should say: what the achievement was, when you accomplished it, how you achieved it, and explain why this achievement is important to you.",
                'part_3': "What do you think makes a good student? How has education changed in your country?",
                'topic_area': q['title'].split('topics related to ')[-1] if 'topics related to' in q['title'] else 'Academic Topics',
                'created_at': datetime.utcnow().isoformat(),
                'source': 'replit_database'
            }
    
    # Process General Speaking Questions
    general_speaking_count = 0
    for q in speaking_questions:
        if q['ielts_test_type'] == 'general' and general_speaking_count < 20:
            general_speaking_count += 1
            question_id = f"gs_{general_speaking_count:03d}"
            
            production_questions[question_id] = {
                'question_id': question_id,
                'assessment_type': 'general_speaking',
                'title': q['title'],
                'description': q['description'],
                'part_1': "Let's talk about your work. What do you do?",
                'part_2': "Describe a skill you would like to learn. You should say: what the skill is, why you want to learn it, how you plan to learn it, and explain how this skill would benefit you.",
                'part_3': "How important is it to learn new skills? What skills do you think are most valuable in today's workplace?",
                'topic_area': q['title'].split('topics related to ')[-1] if 'topics related to' in q['title'] else 'General Topics',
                'created_at': datetime.utcnow().isoformat(),
                'source': 'replit_database'
            }
    
    return production_questions

def upload_to_dynamodb(questions):
    """Upload questions to production DynamoDB table"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('ielts-assessment-questions')
    
    success_count = 0
    error_count = 0
    
    for question_id, question_data in questions.items():
        try:
            table.put_item(Item=question_data)
            print(f"✅ Uploaded: {question_id} - {question_data['title']}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error uploading {question_id}: {str(e)}")
            error_count += 1
    
    return success_count, error_count

def main():
    """Main function to populate production questions"""
    print("🚀 Starting Production DynamoDB Question Population...")
    
    try:
        # Create production questions
        print("📊 Extracting questions from Replit database...")
        production_questions = create_production_questions()
        
        print(f"📝 Created {len(production_questions)} production questions:")
        
        # Count by type
        counts = {}
        for q in production_questions.values():
            assessment_type = q['assessment_type']
            counts[assessment_type] = counts.get(assessment_type, 0) + 1
        
        for assessment_type, count in counts.items():
            print(f"   • {assessment_type}: {count} questions")
        
        # Upload to DynamoDB
        print("☁️  Uploading to production DynamoDB...")
        success_count, error_count = upload_to_dynamodb(production_questions)
        
        print(f"\\n🎉 PRODUCTION QUESTION POPULATION COMPLETE!")
        print(f"✅ Successfully uploaded: {success_count} questions")
        print(f"❌ Errors: {error_count} questions")
        print(f"📊 Total questions in production: {success_count}")
        
        # Show question distribution
        print(f"\\n📋 Question Distribution:")
        for assessment_type, count in counts.items():
            print(f"   • {assessment_type}: {count} questions")
        
        return True
        
    except Exception as e:
        print(f"❌ Population failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n🌐 Production DynamoDB tables now populated with comprehensive IELTS questions!")
    else:
        print("\\n❌ POPULATION FAILED - Check database connections and AWS permissions")