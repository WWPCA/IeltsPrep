"""
Nova Writing Assessment Service
Provides AI-powered writing assessment using Amazon Nova Micro model
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class NovaWritingAssessment:
    """Nova Micro-powered writing assessment service"""
    
    def __init__(self):
        self.bedrock_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            logger.info("Nova Micro client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Micro client: {e}")
    
    def assess_writing_task1(self, essay_text, task_prompt, assessment_type="academic"):
        """Assess IELTS Writing Task 1 using Nova Micro"""
        try:
            if not self.bedrock_client:
                return self._error_response("Nova Micro service unavailable")
            
            system_prompt = self._get_task1_system_prompt(assessment_type)
            user_prompt = f"""
            Task Prompt: {task_prompt}
            
            Student Essay: {essay_text}
            
            Please provide a comprehensive IELTS Writing Task 1 assessment.
            """
            
            response = self._call_nova_micro(system_prompt, user_prompt)
            
            if response.get('success'):
                return {
                    'success': True,
                    'assessment': response['content'],
                    'task_type': 'task1',
                    'assessment_type': assessment_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Nova Micro Task 1 assessment error: {e}")
            return self._error_response(f"Assessment processing error: {str(e)}")
    
    def assess_writing_task2(self, essay_text, task_prompt, assessment_type="academic"):
        """Assess IELTS Writing Task 2 using Nova Micro"""
        try:
            if not self.bedrock_client:
                return self._error_response("Nova Micro service unavailable")
            
            system_prompt = self._get_task2_system_prompt(assessment_type)
            user_prompt = f"""
            Task Prompt: {task_prompt}
            
            Student Essay: {essay_text}
            
            Please provide a comprehensive IELTS Writing Task 2 assessment.
            """
            
            response = self._call_nova_micro(system_prompt, user_prompt)
            
            if response.get('success'):
                return {
                    'success': True,
                    'assessment': response['content'],
                    'task_type': 'task2',
                    'assessment_type': assessment_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Nova Micro Task 2 assessment error: {e}")
            return self._error_response(f"Assessment processing error: {str(e)}")
    
    def assess_complete_writing_test(self, task1_text, task1_prompt, task2_text, task2_prompt, assessment_type="academic"):
        """Assess complete IELTS Writing test (both tasks) using Nova Micro"""
        try:
            # Assess both tasks
            task1_result = self.assess_writing_task1(task1_text, task1_prompt, assessment_type)
            task2_result = self.assess_writing_task2(task2_text, task2_prompt, assessment_type)
            
            if task1_result.get('success') and task2_result.get('success'):
                return {
                    'success': True,
                    'task1_assessment': task1_result['assessment'],
                    'task2_assessment': task2_result['assessment'],
                    'assessment_type': assessment_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Return error if either task failed
            errors = []
            if not task1_result.get('success'):
                errors.append(f"Task 1: {task1_result.get('error', 'Unknown error')}")
            if not task2_result.get('success'):
                errors.append(f"Task 2: {task2_result.get('error', 'Unknown error')}")
            
            return self._error_response(f"Assessment failed: {'; '.join(errors)}")
            
        except Exception as e:
            logger.error(f"Nova Micro complete test assessment error: {e}")
            return self._error_response(f"Complete test assessment error: {str(e)}")
    
    def _call_nova_micro(self, system_prompt, user_prompt):
        """Call Nova Micro model for assessment"""
        try:
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 2000,
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            response = self.bedrock_client.converse(
                modelId="amazon.nova-micro-v1:0",
                messages=request_body["messages"],
                inferenceConfig=request_body["inferenceConfig"]
            )
            
            if response.get('output') and response['output'].get('message'):
                content = response['output']['message']['content'][0]['text']
                return {
                    'success': True,
                    'content': content
                }
            
            return self._error_response("Invalid response from Nova Micro")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                logger.error("Nova Micro access denied - check IAM permissions")
                return self._error_response("Nova Micro access denied - please check permissions")
            elif error_code == 'ValidationException':
                logger.error(f"Nova Micro validation error: {e}")
                return self._error_response("Invalid request format")
            else:
                logger.error(f"Nova Micro client error: {e}")
                return self._error_response(f"Nova Micro service error: {error_code}")
        
        except BotoCoreError as e:
            logger.error(f"Nova Micro connection error: {e}")
            return self._error_response("Nova Micro connection failed")
        
        except Exception as e:
            logger.error(f"Unexpected Nova Micro error: {e}")
            return self._error_response(f"Unexpected assessment error: {str(e)}")
    
    def _get_task1_system_prompt(self, assessment_type):
        """Get system prompt for Task 1 assessment"""
        base_prompt = """You are an expert IELTS Writing examiner. Assess the following Writing Task 1 response according to official IELTS criteria:

1. Task Achievement (25%): How well the response fulfills the task requirements
2. Coherence and Cohesion (25%): Organization and logical flow
3. Lexical Resource (25%): Vocabulary range and accuracy
4. Grammatical Range and Accuracy (25%): Grammar variety and correctness

Provide:
- Overall band score (0.5-9.0)
- Individual criterion scores
- Detailed feedback for each criterion
- Specific examples from the text
- Actionable improvement suggestions

Format your response as structured feedback with clear sections."""
        
        if assessment_type == "general":
            return base_prompt + "\n\nNote: This is General Training Task 1 (letter writing). Focus on appropriate tone, format, and purpose fulfillment."
        
        return base_prompt + "\n\nNote: This is Academic Task 1 (data description). Focus on data interpretation, trends, and academic language."
    
    def _get_task2_system_prompt(self, assessment_type):
        """Get system prompt for Task 2 assessment"""
        base_prompt = """You are an expert IELTS Writing examiner. Assess the following Writing Task 2 response according to official IELTS criteria:

1. Task Response (25%): How well the response addresses the task and develops ideas
2. Coherence and Cohesion (25%): Organization, paragraphing, and logical progression
3. Lexical Resource (25%): Vocabulary range, precision, and appropriateness
4. Grammatical Range and Accuracy (25%): Sentence variety and grammatical control

Provide:
- Overall band score (0.5-9.0)
- Individual criterion scores
- Detailed feedback for each criterion
- Specific examples from the text
- Actionable improvement suggestions

Format your response as structured feedback with clear sections."""
        
        return base_prompt
    
    def _error_response(self, error_message):
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance for easy import
nova_writing_service = NovaWritingAssessment()

# Convenience functions for backward compatibility
def assess_writing_task1(essay_text, task_prompt, assessment_type="academic"):
    """Assess Writing Task 1"""
    return nova_writing_service.assess_writing_task1(essay_text, task_prompt, assessment_type)

def assess_writing_task2(essay_text, task_prompt, assessment_type="academic"):
    """Assess Writing Task 2"""
    return nova_writing_service.assess_writing_task2(essay_text, task_prompt, assessment_type)

def assess_complete_writing_test(task1_text, task1_prompt, task2_text, task2_prompt, assessment_type="academic"):
    """Assess complete Writing test"""
    return nova_writing_service.assess_complete_writing_test(
        task1_text, task1_prompt, task2_text, task2_prompt, assessment_type
    )