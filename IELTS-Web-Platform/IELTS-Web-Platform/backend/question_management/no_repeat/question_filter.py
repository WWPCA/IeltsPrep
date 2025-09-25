#!/usr/bin/env python3
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
