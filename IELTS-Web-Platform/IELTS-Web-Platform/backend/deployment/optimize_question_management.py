#!/usr/bin/env python3
"""
Question Management System Optimization for IELTS GenAI Prep
Filters relevant questions (Speaking & Writing only), removes Reading questions,
sets up no-repeat system for multiple purchases, optimizes for platform focus
"""

import json
import os
import shutil
from datetime import datetime
import random

def analyze_current_questions():
    """Analyze current question files and categorize them"""
    print("🔍 Analyzing current question files...")
    
    question_files = {
        'writing_academic': 'assets/Academic Writing Task 2 tests (essays).txt',
        'writing_general': 'assets/General Training Writing Task 2 tests (essays).txt',
        'writing_letters': 'assets/IELTS General Training Writing Task 1 letters.txt',
        'reading_general_mc': 'assets/General Reading Task 1 Multiple Cho.txt',
        'reading_general_tf': 'assets/General Test Reading Task 2 True False  Not Given.txt',
        'reading_context': 'assets/IELTS Reading Context File.txt'
    }
    
    analysis = {
        'relevant_files': [],
        'reading_files_to_remove': [],
        'file_sizes': {},
        'total_questions_estimated': 0
    }
    
    for category, file_path in question_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            analysis['file_sizes'][category] = file_size
            
            if 'reading' in category:
                analysis['reading_files_to_remove'].append(file_path)
                print(f"❌ Will remove: {file_path} ({file_size:,} bytes)")
            else:
                analysis['relevant_files'].append(file_path)
                # Estimate questions based on file size
                estimated_questions = max(1, file_size // 500)  # Rough estimate
                analysis['total_questions_estimated'] += estimated_questions
                print(f"✅ Keep: {file_path} (~{estimated_questions} questions)")
    
    print(f"\n📊 Analysis Summary:")
    print(f"   Relevant files: {len(analysis['relevant_files'])}")
    print(f"   Reading files to remove: {len(analysis['reading_files_to_remove'])}")
    print(f"   Estimated total questions: {analysis['total_questions_estimated']}")
    
    return analysis

def create_optimized_question_structure():
    """Create optimized question management structure"""
    print("🏗️ Creating optimized question structure...")
    
    # Create new question structure
    question_structure = {
        'questions/': {
            'writing/': {
                'academic/': ['task1/', 'task2/'],
                'general/': ['task1/', 'task2/']
            },
            'speaking/': {
                'academic/': ['part1/', 'part2/', 'part3/'],
                'general/': ['part1/', 'part2/', 'part3/']
            }
        },
        'question_management/': {
            'filters/': [],
            'no_repeat/': [],
            'analytics/': []
        }
    }
    
    base_dir = 'optimized-questions'
    os.makedirs(base_dir, exist_ok=True)
    
    def create_dirs(structure, current_path):
        for item, content in structure.items():
            item_path = os.path.join(current_path, item)
            if isinstance(content, dict):
                os.makedirs(item_path, exist_ok=True)
                create_dirs(content, item_path)
            elif isinstance(content, list):
                os.makedirs(item_path, exist_ok=True)
                for subdir in content:
                    if subdir.endswith('/'):
                        os.makedirs(os.path.join(item_path, subdir), exist_ok=True)
    
    create_dirs(question_structure, base_dir)
    print(f"✅ Question structure created in {base_dir}/")
    
    return base_dir

def process_writing_questions(base_dir):
    """Process and organize writing questions"""
    print("✍️ Processing writing questions...")
    
    writing_processors = {
        'academic_task2': {
            'source': 'assets/Academic Writing Task 2 tests (essays).txt',
            'target': f'{base_dir}/questions/writing/academic/task2/questions.json',
            'type': 'academic_writing_task2'
        },
        'general_task2': {
            'source': 'assets/General Training Writing Task 2 tests (essays).txt',
            'target': f'{base_dir}/questions/writing/general/task2/questions.json',
            'type': 'general_writing_task2'
        },
        'general_task1': {
            'source': 'assets/IELTS General Training Writing Task 1 letters.txt',
            'target': f'{base_dir}/questions/writing/general/task1/questions.json',
            'type': 'general_writing_task1'
        }
    }
    
    processed_questions = {}
    
    for category, config in writing_processors.items():
        if os.path.exists(config['source']):
            print(f"📝 Processing {category}...")
            
            with open(config['source'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse questions from text content
            questions = parse_writing_questions(content, config['type'])
            
            # Save as structured JSON
            os.makedirs(os.path.dirname(config['target']), exist_ok=True)
            with open(config['target'], 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            
            processed_questions[category] = len(questions)
            print(f"✅ {category}: {len(questions)} questions processed")
    
    return processed_questions

def parse_writing_questions(content, question_type):
    """Parse writing questions from text content"""
    questions = []
    
    # Split content into potential questions
    lines = content.split('\n')
    current_question = {}
    question_id = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect question patterns
        if len(line) > 50 and ('discuss' in line.lower() or 'write' in line.lower() or 'explain' in line.lower()):
            if current_question:
                current_question['id'] = f"{question_type}_{question_id:03d}"
                questions.append(current_question)
                question_id += 1
            
            current_question = {
                'type': question_type,
                'prompt': line,
                'difficulty': 'intermediate',
                'time_limit': 40 if 'task2' in question_type else 20,
                'word_count_min': 250 if 'task2' in question_type else 150,
                'criteria': get_assessment_criteria(question_type),
                'tags': extract_tags(line)
            }
    
    # Add final question
    if current_question:
        current_question['id'] = f"{question_type}_{question_id:03d}"
        questions.append(current_question)
    
    return questions

def get_assessment_criteria(question_type):
    """Get assessment criteria for question type"""
    if 'task2' in question_type:
        return [
            'Task Achievement',
            'Coherence and Cohesion',
            'Lexical Resource',
            'Grammatical Range and Accuracy'
        ]
    else:  # Task 1
        return [
            'Task Achievement',
            'Coherence and Cohesion',
            'Lexical Resource',
            'Grammatical Range and Accuracy'
        ]

def extract_tags(prompt):
    """Extract relevant tags from question prompt"""
    tags = []
    
    # Common IELTS topics
    topic_keywords = {
        'education': ['education', 'school', 'university', 'learning', 'student'],
        'technology': ['technology', 'computer', 'internet', 'digital', 'online'],
        'environment': ['environment', 'climate', 'pollution', 'nature', 'green'],
        'health': ['health', 'medical', 'fitness', 'diet', 'exercise'],
        'society': ['society', 'community', 'social', 'culture', 'people'],
        'work': ['work', 'job', 'career', 'employment', 'business'],
        'travel': ['travel', 'tourism', 'transport', 'journey', 'vacation'],
        'family': ['family', 'children', 'parents', 'home', 'relationship']
    }
    
    prompt_lower = prompt.lower()
    for topic, keywords in topic_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            tags.append(topic)
    
    return tags[:3]  # Limit to 3 most relevant tags

def create_speaking_questions(base_dir):
    """Create speaking questions structure"""
    print("🎤 Creating speaking questions...")
    
    speaking_questions = {
        'academic': {
            'part1': [
                {
                    'id': 'academic_speaking_part1_001',
                    'type': 'academic_speaking_part1',
                    'topic': 'Studies and Work',
                    'questions': [
                        'What subject are you studying?',
                        'Why did you choose this subject?',
                        'What do you find most interesting about your studies?',
                        'Do you prefer to study alone or with others?'
                    ],
                    'time_limit': 5,
                    'difficulty': 'beginner'
                },
                {
                    'id': 'academic_speaking_part1_002',
                    'type': 'academic_speaking_part1',
                    'topic': 'Hometown',
                    'questions': [
                        'Where do you come from?',
                        'What do you like about your hometown?',
                        'Has your hometown changed much since you were young?',
                        'Would you recommend your hometown to visitors?'
                    ],
                    'time_limit': 5,
                    'difficulty': 'beginner'
                }
            ],
            'part2': [
                {
                    'id': 'academic_speaking_part2_001',
                    'type': 'academic_speaking_part2',
                    'topic': 'Describe a book you recently read',
                    'prompt': 'Describe a book you recently read that you found interesting.',
                    'points_to_cover': [
                        'What the book was about',
                        'When you read it',
                        'Why you chose this book',
                        'Why you found it interesting'
                    ],
                    'time_limit': 2,
                    'preparation_time': 1,
                    'difficulty': 'intermediate'
                }
            ],
            'part3': [
                {
                    'id': 'academic_speaking_part3_001',
                    'type': 'academic_speaking_part3',
                    'topic': 'Reading and Literature',
                    'questions': [
                        'Do you think people read less nowadays compared to the past?',
                        'What are the benefits of reading books versus watching movies?',
                        'How important is it for children to develop reading habits?',
                        'What role do libraries play in modern society?'
                    ],
                    'time_limit': 5,
                    'difficulty': 'advanced'
                }
            ]
        },
        'general': {
            'part1': [
                {
                    'id': 'general_speaking_part1_001',
                    'type': 'general_speaking_part1',
                    'topic': 'Work and Daily Life',
                    'questions': [
                        'What do you do for work?',
                        'Do you enjoy your job?',
                        'What time do you usually start work?',
                        'What do you do in your free time?'
                    ],
                    'time_limit': 5,
                    'difficulty': 'beginner'
                }
            ],
            'part2': [
                {
                    'id': 'general_speaking_part2_001',
                    'type': 'general_speaking_part2',
                    'topic': 'Describe a memorable journey',
                    'prompt': 'Describe a memorable journey you have taken.',
                    'points_to_cover': [
                        'Where you went',
                        'Who you went with',
                        'What you did there',
                        'Why it was memorable'
                    ],
                    'time_limit': 2,
                    'preparation_time': 1,
                    'difficulty': 'intermediate'
                }
            ],
            'part3': [
                {
                    'id': 'general_speaking_part3_001',
                    'type': 'general_speaking_part3',
                    'topic': 'Travel and Transportation',
                    'questions': [
                        'How has travel changed in recent years?',
                        'What are the advantages of different types of transportation?',
                        'Do you think people travel too much nowadays?',
                        'How might travel change in the future?'
                    ],
                    'time_limit': 5,
                    'difficulty': 'advanced'
                }
            ]
        }
    }
    
    # Save speaking questions
    for training_type, parts in speaking_questions.items():
        for part, questions in parts.items():
            target_path = f'{base_dir}/questions/speaking/{training_type}/{part}/questions.json'
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
    
    total_speaking = sum(len(questions) for parts in speaking_questions.values() for questions in parts.values())
    print(f"✅ Created {total_speaking} speaking questions")
    
    return total_speaking

def create_no_repeat_system(base_dir):
    """Create no-repeat system for multiple purchases"""
    print("🔄 Creating no-repeat system...")
    
    no_repeat_system = {
        'user_question_tracking.py': '''#!/usr/bin/env python3
"""
User Question Tracking System - Prevents Question Repetition
Tracks which questions each user has seen to ensure no repeats across purchases
"""

import json
import os
from datetime import datetime, timedelta
import boto3
from typing import List, Dict, Set

class QuestionTracker:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.Table('ielts-user-question-history')
    
    def get_user_seen_questions(self, user_id: str, assessment_type: str) -> Set[str]:
        """Get all questions this user has seen for this assessment type"""
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'assessment_type': assessment_type
                }
            )
            
            if 'Item' in response:
                return set(response['Item'].get('seen_questions', []))
            return set()
            
        except Exception as e:
            print(f"Error getting seen questions: {e}")
            return set()
    
    def mark_questions_seen(self, user_id: str, assessment_type: str, question_ids: List[str]):
        """Mark questions as seen by user"""
        try:
            seen_questions = self.get_user_seen_questions(user_id, assessment_type)
            seen_questions.update(question_ids)
            
            self.table.put_item(
                Item={
                    'user_id': user_id,
                    'assessment_type': assessment_type,
                    'seen_questions': list(seen_questions),
                    'last_updated': datetime.utcnow().isoformat(),
                    'total_seen': len(seen_questions)
                }
            )
            
        except Exception as e:
            print(f"Error marking questions seen: {e}")
    
    def get_fresh_questions(self, user_id: str, assessment_type: str, 
                          all_questions: List[Dict], count: int = 4) -> List[Dict]:
        """Get questions user hasn't seen before"""
        seen_questions = self.get_user_seen_questions(user_id, assessment_type)
        
        # Filter out seen questions
        fresh_questions = [q for q in all_questions if q['id'] not in seen_questions]
        
        # If not enough fresh questions, include some older ones
        if len(fresh_questions) < count:
            # Add back older questions, prioritizing least recently seen
            remaining_needed = count - len(fresh_questions)
            older_questions = [q for q in all_questions if q['id'] in seen_questions]
            fresh_questions.extend(older_questions[:remaining_needed])
        
        # Randomize and return requested count
        import random
        random.shuffle(fresh_questions)
        return fresh_questions[:count]
    
    def reset_user_history(self, user_id: str, assessment_type: str = None):
        """Reset question history for user (admin function)"""
        try:
            if assessment_type:
                self.table.delete_item(
                    Key={
                        'user_id': user_id,
                        'assessment_type': assessment_type
                    }
                )
            else:
                # Reset all assessment types for user
                response = self.table.query(
                    KeyConditionExpression='user_id = :uid',
                    ExpressionAttributeValues={':uid': user_id}
                )
                
                for item in response.get('Items', []):
                    self.table.delete_item(
                        Key={
                            'user_id': item['user_id'],
                            'assessment_type': item['assessment_type']
                        }
                    )
                    
        except Exception as e:
            print(f"Error resetting user history: {e}")

# Usage example:
# tracker = QuestionTracker()
# fresh_questions = tracker.get_fresh_questions('user123', 'academic_writing', all_questions, 4)
# tracker.mark_questions_seen('user123', 'academic_writing', [q['id'] for q in fresh_questions])
''',
        
        'question_filter.py': '''#!/usr/bin/env python3
"""
Question Filtering System - Smart Question Selection
Filters questions based on user level, preferences, and learning progress
"""

import json
import random
from typing import List, Dict, Optional
from datetime import datetime

class QuestionFilter:
    def __init__(self, questions_dir: str):
        self.questions_dir = questions_dir
        self.difficulty_weights = {
            'beginner': 0.4,
            'intermediate': 0.4,
            'advanced': 0.2
        }
    
    def load_questions(self, assessment_type: str) -> List[Dict]:
        """Load questions for specific assessment type"""
        question_files = {
            'academic_writing': 'questions/writing/academic/task2/questions.json',
            'general_writing': 'questions/writing/general/task2/questions.json',
            'academic_speaking': ['questions/speaking/academic/part1/questions.json',
                                'questions/speaking/academic/part2/questions.json',
                                'questions/speaking/academic/part3/questions.json'],
            'general_speaking': ['questions/speaking/general/part1/questions.json',
                               'questions/speaking/general/part2/questions.json',
                               'questions/speaking/general/part3/questions.json']
        }
        
        files = question_files.get(assessment_type, [])
        if isinstance(files, str):
            files = [files]
        
        all_questions = []
        for file_path in files:
            full_path = f"{self.questions_dir}/{file_path}"
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    if isinstance(questions, list):
                        all_questions.extend(questions)
                    else:
                        all_questions.append(questions)
            except FileNotFoundError:
                print(f"Question file not found: {full_path}")
        
        return all_questions
    
    def filter_by_difficulty(self, questions: List[Dict], 
                           user_level: str = 'intermediate') -> List[Dict]:
        """Filter questions by user difficulty level"""
        if user_level == 'beginner':
            return [q for q in questions if q.get('difficulty', 'intermediate') in ['beginner', 'intermediate']]
        elif user_level == 'advanced':
            return [q for q in questions if q.get('difficulty', 'intermediate') in ['intermediate', 'advanced']]
        else:  # intermediate
            return questions  # All levels appropriate
    
    def filter_by_topics(self, questions: List[Dict], 
                        preferred_topics: List[str] = None) -> List[Dict]:
        """Filter questions by user's preferred topics"""
        if not preferred_topics:
            return questions
        
        filtered = []
        for question in questions:
            question_tags = question.get('tags', [])
            if any(topic in question_tags for topic in preferred_topics):
                filtered.append(question)
        
        # If no matches, return all questions
        return filtered if filtered else questions
    
    def balance_question_types(self, questions: List[Dict], 
                             assessment_type: str) -> List[Dict]:
        """Balance different question types for comprehensive assessment"""
        if 'speaking' in assessment_type:
            # Ensure mix of part 1, 2, and 3 questions
            part1 = [q for q in questions if 'part1' in q.get('type', '')]
            part2 = [q for q in questions if 'part2' in q.get('type', '')]
            part3 = [q for q in questions if 'part3' in q.get('type', '')]
            
            balanced = []
            balanced.extend(random.sample(part1, min(2, len(part1))))
            balanced.extend(random.sample(part2, min(1, len(part2))))
            balanced.extend(random.sample(part3, min(1, len(part3))))
            
            return balanced
        
        return questions
    
    def get_optimized_questions(self, assessment_type: str, count: int = 4,
                              user_level: str = 'intermediate',
                              preferred_topics: List[str] = None,
                              seen_questions: List[str] = None) -> List[Dict]:
        """Get optimized question set for user"""
        # Load all questions
        all_questions = self.load_questions(assessment_type)
        
        # Remove seen questions
        if seen_questions:
            all_questions = [q for q in all_questions if q.get('id') not in seen_questions]
        
        # Apply filters
        filtered = self.filter_by_difficulty(all_questions, user_level)
        filtered = self.filter_by_topics(filtered, preferred_topics)
        filtered = self.balance_question_types(filtered, assessment_type)
        
        # Randomize and return requested count
        random.shuffle(filtered)
        return filtered[:count]

# Usage example:
# filter = QuestionFilter('/path/to/questions')
# questions = filter.get_optimized_questions('academic_writing', 4, 'intermediate', ['education', 'technology'])
''',
        
        'purchase_tracking.py': '''#!/usr/bin/env python3
"""
Purchase Tracking System - Links Questions to Purchases
Ensures users get fresh questions with each purchase and tracks usage
"""

import json
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PurchaseTracker:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.purchases_table = self.dynamodb.Table('ielts-user-purchases')
        self.usage_table = self.dynamodb.Table('ielts-assessment-usage')
    
    def record_purchase(self, user_id: str, purchase_id: str, 
                       assessment_type: str, assessments_count: int = 4):
        """Record new purchase and allocate fresh questions"""
        try:
            self.purchases_table.put_item(
                Item={
                    'user_id': user_id,
                    'purchase_id': purchase_id,
                    'assessment_type': assessment_type,
                    'assessments_total': assessments_count,
                    'assessments_used': 0,
                    'purchase_date': datetime.utcnow().isoformat(),
                    'status': 'active',
                    'questions_allocated': []
                }
            )
            
            print(f"Purchase recorded: {purchase_id} for {assessment_type}")
            
        except Exception as e:
            print(f"Error recording purchase: {e}")
    
    def use_assessment(self, user_id: str, purchase_id: str, 
                      question_ids: List[str]) -> bool:
        """Use one assessment from purchase"""
        try:
            # Get current purchase record
            response = self.purchases_table.get_item(
                Key={
                    'user_id': user_id,
                    'purchase_id': purchase_id
                }
            )
            
            if 'Item' not in response:
                return False
            
            purchase = response['Item']
            
            # Check if assessments available
            if purchase['assessments_used'] >= purchase['assessments_total']:
                return False
            
            # Update usage
            self.purchases_table.update_item(
                Key={
                    'user_id': user_id,
                    'purchase_id': purchase_id
                },
                UpdateExpression='SET assessments_used = assessments_used + :inc, questions_allocated = list_append(questions_allocated, :questions)',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':questions': question_ids
                }
            )
            
            # Record usage details
            self.usage_table.put_item(
                Item={
                    'user_id': user_id,
                    'usage_id': f"{purchase_id}_{purchase['assessments_used'] + 1}",
                    'purchase_id': purchase_id,
                    'assessment_type': purchase['assessment_type'],
                    'question_ids': question_ids,
                    'usage_date': datetime.utcnow().isoformat(),
                    'status': 'completed'
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Error using assessment: {e}")
            return False
    
    def get_user_purchases(self, user_id: str) -> List[Dict]:
        """Get all purchases for user"""
        try:
            response = self.purchases_table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"Error getting purchases: {e}")
            return []
    
    def get_available_assessments(self, user_id: str, assessment_type: str) -> int:
        """Get total available assessments for user and type"""
        purchases = self.get_user_purchases(user_id)
        
        total_available = 0
        for purchase in purchases:
            if (purchase['assessment_type'] == assessment_type and 
                purchase['status'] == 'active'):
                remaining = purchase['assessments_total'] - purchase['assessments_used']
                total_available += remaining
        
        return total_available
    
    def get_all_user_questions(self, user_id: str, assessment_type: str) -> List[str]:
        """Get all questions user has seen across all purchases"""
        purchases = self.get_user_purchases(user_id)
        
        all_questions = []
        for purchase in purchases:
            if purchase['assessment_type'] == assessment_type:
                all_questions.extend(purchase.get('questions_allocated', []))
        
        return list(set(all_questions))  # Remove duplicates

# Usage example:
# tracker = PurchaseTracker()
# tracker.record_purchase('user123', 'purchase456', 'academic_writing', 4)
# success = tracker.use_assessment('user123', 'purchase456', ['q1', 'q2', 'q3', 'q4'])
'''
    }
    
    # Create no-repeat system files
    no_repeat_dir = f'{base_dir}/question_management/no_repeat'
    for filename, content in no_repeat_system.items():
        file_path = os.path.join(no_repeat_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Created {len(no_repeat_system)} no-repeat system files")
    
    return len(no_repeat_system)

def remove_reading_questions():
    """Remove reading question files"""
    print("🗑️ Removing reading question files...")
    
    reading_files = [
        'assets/General Reading Task 1 Multiple Cho.txt',
        'assets/General Test Reading Task 2 True False  Not Given.txt',
        'assets/IELTS Reading Context File.txt'
    ]
    
    removed_files = []
    total_size_removed = 0
    
    for file_path in reading_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            total_size_removed += file_size
            
            # Move to backup instead of deleting
            backup_dir = 'removed_reading_questions'
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.move(file_path, backup_path)
            
            removed_files.append(file_path)
            print(f"📦 Moved to backup: {file_path} ({file_size:,} bytes)")
    
    print(f"✅ Removed {len(removed_files)} reading files ({total_size_removed:,} bytes total)")
    print(f"📦 Backup location: removed_reading_questions/")
    
    return removed_files, total_size_removed

def create_question_api(base_dir):
    """Create question management API"""
    print("🔌 Creating question management API...")
    
    api_code = '''#!/usr/bin/env python3
"""
Question Management API for IELTS GenAI Prep
Provides optimized question selection with no-repeat functionality
"""

from flask import Flask, request, jsonify
import json
import os
from question_filter import QuestionFilter
from user_question_tracking import QuestionTracker
from purchase_tracking import PurchaseTracker

app = Flask(__name__)

# Initialize services
question_filter = QuestionFilter('optimized-questions')
question_tracker = QuestionTracker()
purchase_tracker = PurchaseTracker()

@app.route('/api/questions/<assessment_type>', methods=['GET'])
def get_questions(assessment_type):
    """Get optimized questions for assessment type"""
    try:
        user_id = request.args.get('user_id')
        count = int(request.args.get('count', 4))
        user_level = request.args.get('level', 'intermediate')
        preferred_topics = request.args.getlist('topics')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # Check if user has available assessments
        available = purchase_tracker.get_available_assessments(user_id, assessment_type)
        if available <= 0:
            return jsonify({'error': 'No assessments available. Please purchase more.'}), 403
        
        # Get questions user hasn't seen
        seen_questions = question_tracker.get_user_seen_questions(user_id, assessment_type)
        
        # Get optimized question set
        questions = question_filter.get_optimized_questions(
            assessment_type, count, user_level, preferred_topics, list(seen_questions)
        )
        
        if not questions:
            return jsonify({'error': 'No questions available'}), 404
        
        return jsonify({
            'status': 'success',
            'assessment_type': assessment_type,
            'questions': questions,
            'count': len(questions),
            'user_level': user_level,
            'available_assessments': available
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/submit', methods=['POST'])
def submit_assessment():
    """Submit completed assessment and mark questions as used"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        purchase_id = data.get('purchase_id')
        question_ids = data.get('question_ids', [])
        assessment_type = data.get('assessment_type')
        
        if not all([user_id, purchase_id, question_ids, assessment_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use assessment from purchase
        success = purchase_tracker.use_assessment(user_id, purchase_id, question_ids)
        if not success:
            return jsonify({'error': 'Failed to use assessment'}), 400
        
        # Mark questions as seen
        question_tracker.mark_questions_seen(user_id, assessment_type, question_ids)
        
        return jsonify({
            'status': 'success',
            'message': 'Assessment submitted successfully',
            'questions_marked': len(question_ids)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user question and purchase statistics"""
    try:
        purchases = purchase_tracker.get_user_purchases(user_id)
        
        stats = {
            'total_purchases': len(purchases),
            'assessments_by_type': {},
            'questions_seen_by_type': {}
        }
        
        assessment_types = ['academic_writing', 'general_writing', 'academic_speaking', 'general_speaking']
        
        for assessment_type in assessment_types:
            available = purchase_tracker.get_available_assessments(user_id, assessment_type)
            seen_questions = len(question_tracker.get_user_seen_questions(user_id, assessment_type))
            
            stats['assessments_by_type'][assessment_type] = {
                'available': available,
                'total_purchased': sum(p['assessments_total'] for p in purchases if p['assessment_type'] == assessment_type),
                'used': sum(p['assessments_used'] for p in purchases if p['assessment_type'] == assessment_type)
            }
            
            stats['questions_seen_by_type'][assessment_type] = seen_questions
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    api_path = f'{base_dir}/question_management/api.py'
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api_code)
    
    print("✅ Question management API created")
    
    return api_path

def generate_optimization_report(base_dir, processed_questions, removed_files, total_size_removed):
    """Generate optimization report"""
    print("📊 Generating optimization report...")
    
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'optimization_summary': {
            'questions_processed': sum(processed_questions.values()),
            'question_categories': len(processed_questions),
            'reading_files_removed': len(removed_files),
            'storage_saved_bytes': total_size_removed,
            'no_repeat_system_files': 3,
            'api_created': True
        },
        'question_breakdown': processed_questions,
        'removed_files': removed_files,
        'features_implemented': [
            'Speaking & Writing questions only',
            'No-repeat system across purchases',
            'Smart question filtering',
            'User progress tracking',
            'Purchase-based access control',
            'Difficulty-based selection',
            'Topic-based filtering',
            'Question type balancing'
        ],
        'platform_focus': 'TrueScore® Writing + ClearScore® Speaking assessments',
        'status': 'optimized_for_production'
    }
    
    with open('question_optimization_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("=" * 60)
    print("🎉 QUESTION MANAGEMENT SYSTEM OPTIMIZATION COMPLETE")
    print("=" * 60)
    print(f"📁 Optimized structure: {base_dir}/")
    print(f"📝 Questions processed: {sum(processed_questions.values())}")
    print(f"🗑️ Reading files removed: {len(removed_files)}")
    print(f"💾 Storage saved: {total_size_removed:,} bytes")
    print(f"🔄 No-repeat system: Implemented")
    print(f"🎯 Platform focus: Speaking & Writing only")
    
    print(f"\n📋 Features Implemented:")
    for feature in report['features_implemented']:
        print(f"   ✅ {feature}")
    
    print(f"\n📋 Next Steps:")
    print("1. Review optimized question structure")
    print("2. Test question API endpoints")
    print("3. Deploy no-repeat system to AWS")
    print("4. Update mobile apps to use new API")
    print("5. Test purchase-based question allocation")
    
    return report

def main():
    """Main optimization function"""
    print("🚀 IELTS GenAI Prep Question Management Optimization")
    print("=" * 60)
    
    # Analyze current questions
    analysis = analyze_current_questions()
    
    # Create optimized structure
    base_dir = create_optimized_question_structure()
    
    # Process writing questions
    processed_questions = process_writing_questions(base_dir)
    
    # Create speaking questions
    speaking_count = create_speaking_questions(base_dir)
    processed_questions['speaking'] = speaking_count
    
    # Create no-repeat system
    no_repeat_files = create_no_repeat_system(base_dir)
    
    # Remove reading questions
    removed_files, total_size_removed = remove_reading_questions()
    
    # Create question API
    api_path = create_question_api(base_dir)
    
    # Generate report
    report = generate_optimization_report(base_dir, processed_questions, removed_files, total_size_removed)
    
    print(f"\n💾 Optimization report: question_optimization_report.json")
    print(f"🎯 Ready for platform integration!")

if __name__ == '__main__':
    main()