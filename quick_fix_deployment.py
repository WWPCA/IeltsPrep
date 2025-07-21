#!/usr/bin/env python3
"""
Quick Fix for Production Error - Fix syntax issues
"""

import zipfile
import os
from datetime import datetime

def create_fixed_production_package():
    """Create a fixed version without syntax errors"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"fixed_unique_questions_{timestamp}.zip"
    
    print(f"🛠️ CREATING FIXED PRODUCTION PACKAGE")
    
    # Read current aws_mock_config.py
    with open('aws_mock_config.py', 'r') as f:
        content = f.read()
    
    # Add the missing import and functions correctly
    fixed_content = content.replace(
        '# Global instance for use throughout the application',
        '''
    def _get_question_bank(self, assessment_type: str):
        """Get question bank for specific assessment type"""
        questions_table = self.dynamodb_tables.get('ielts-assessment-questions')
        if not questions_table:
            return []
        
        # Get all questions for this assessment type
        all_questions = list(questions_table.items.values())
        filtered_questions = [q for q in all_questions if q.get('assessment_type') == assessment_type]
        
        return filtered_questions if filtered_questions else []
    
    def get_unique_assessment_question(self, user_email: str, assessment_type: str):
        """Get a unique assessment question that user hasn't seen before"""
        user = self.users_table.get_item(user_email)
        if not user:
            return None
        
        # Get user's completed assessments to avoid repetition
        completed_assessments = user.get('completed_assessments', [])
        used_questions = [a.get('question_id') for a in completed_assessments if a.get('assessment_type') == assessment_type]
        
        # Get question bank for this assessment type
        question_bank = self._get_question_bank(assessment_type)
        available_questions = [q for q in question_bank if q['question_id'] not in used_questions]
        
        if not available_questions:
            # If all questions used, allow reuse after completing all 4 attempts
            available_questions = question_bank
        
        # Return random question from available pool
        import random
        return random.choice(available_questions) if available_questions else None
    
    def mark_question_as_used(self, user_email: str, assessment_type: str, question_id: str):
        """Mark question as used by user to prevent repetition"""
        user = self.users_table.get_item(user_email)
        if not user:
            return False
        
        if 'completed_assessments' not in user:
            user['completed_assessments'] = []
        
        # Add this assessment to completed list
        assessment_record = {
            'question_id': question_id,
            'assessment_type': assessment_type,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        user['completed_assessments'].append(assessment_record)
        return self.users_table.put_item(user)

# Global instance for use throughout the application'''
    )
    
    # Write fixed version
    with open('aws_mock_config_fixed.py', 'w') as f:
        f.write(fixed_content)
    
    # Create fixed package
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add current app.py
        zipf.write('app.py', 'app.py')
        
        # Add fixed aws_mock_config.py
        zipf.write('aws_mock_config_fixed.py', 'aws_mock_config.py')
        
        # Add templates
        template_files = [
            'templates/login.html',
            'templates/privacy_policy.html',
            'templates/terms_of_service.html',
            'templates/profile.html'
        ]
        
        for template in template_files:
            if os.path.exists(template):
                zipf.write(template, template)
    
    # Cleanup
    os.remove('aws_mock_config_fixed.py')
    
    file_size = os.path.getsize(package_name) / 1024
    print(f"✅ FIXED PACKAGE CREATED: {package_name} ({file_size:.1f} KB)")
    
    return package_name

if __name__ == "__main__":
    package_name = create_fixed_production_package()
    print(f"🎯 Ready to deploy: {package_name}")