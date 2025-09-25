#!/usr/bin/env python3
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
