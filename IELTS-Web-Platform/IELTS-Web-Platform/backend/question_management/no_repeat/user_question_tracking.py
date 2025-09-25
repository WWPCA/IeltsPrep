#!/usr/bin/env python3
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
