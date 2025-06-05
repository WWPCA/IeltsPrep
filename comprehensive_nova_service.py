"""
Comprehensive Nova Service
Unified service for all Nova AI interactions including speech-to-speech and writing assessments
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class ComprehensiveNovaService:
    """Unified Nova service for speech and writing assessments"""
    
    def __init__(self):
        self.bedrock_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client for Nova models"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            logger.info("Comprehensive Nova service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Nova service: {e}")
    
    def conduct_speaking_conversation(self, user_message, context, part_number=1):
        """Conduct speaking conversation using Nova Sonic (requires model access)"""
        try:
            if not self.bedrock_client:
                return self._error_response("Nova service unavailable")
            
            # For now, return guidance message until Nova Sonic access is enabled
            return {
                'success': False,
                'error': 'Nova Sonic access required',
                'guidance': 'Request Nova Sonic model access through AWS Bedrock console to enable speech-to-speech conversations',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Speaking conversation error: {e}")
            return self._error_response(f"Conversation error: {str(e)}")
    
    def assess_writing_with_nova(self, essay_text, task_prompt, task_type="task1", assessment_type="academic"):
        """Assess writing using Nova Micro"""
        try:
            if not self.bedrock_client:
                return self._error_response("Nova Micro service unavailable")
            
            system_prompt = self._get_writing_assessment_prompt(task_type, assessment_type)
            user_prompt = f"""
            Task Prompt: {task_prompt}
            
            Student Essay: {essay_text}
            
            Please provide a comprehensive IELTS Writing {task_type.upper()} assessment.
            """
            
            response = self._call_nova_micro(system_prompt, user_prompt)
            
            if response.get('success'):
                return {
                    'success': True,
                    'assessment': response['content'],
                    'task_type': task_type,
                    'assessment_type': assessment_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Nova writing assessment error: {e}")
            return self._error_response(f"Writing assessment error: {str(e)}")
    
    def analyze_speaking_transcript(self, transcript_text, part_number=1, question_type="general"):
        """Analyze speaking transcript using Nova Micro"""
        try:
            if not self.bedrock_client:
                return self._error_response("Nova Micro service unavailable")
            
            system_prompt = self._get_speaking_analysis_prompt(part_number)
            user_prompt = f"""
            Speaking Part {part_number} Transcript: {transcript_text}
            Question Type: {question_type}
            
            Please provide a comprehensive IELTS Speaking assessment based on this transcript.
            """
            
            response = self._call_nova_micro(system_prompt, user_prompt)
            
            if response.get('success'):
                return {
                    'success': True,
                    'analysis': response['content'],
                    'part_number': part_number,
                    'question_type': question_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Speaking transcript analysis error: {e}")
            return self._error_response(f"Transcript analysis error: {str(e)}")
    
    def _call_nova_micro(self, system_prompt, user_prompt):
        """Call Nova Micro model for assessments"""
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
    
    def _get_writing_assessment_prompt(self, task_type, assessment_type):
        """Get system prompt for writing assessment"""
        if task_type == "task1":
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
        
        else:  # task2
            return """You are an expert IELTS Writing examiner. Assess the following Writing Task 2 response according to official IELTS criteria:

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
    
    def _get_speaking_analysis_prompt(self, part_number):
        """Get system prompt for speaking analysis"""
        base_prompt = f"""You are an expert IELTS Speaking examiner. Analyze the following Speaking Part {part_number} response according to official IELTS criteria:

1. Fluency and Coherence (25%): Speech flow, hesitation, logical sequencing
2. Lexical Resource (25%): Vocabulary range, accuracy, and appropriateness  
3. Grammatical Range and Accuracy (25%): Grammar variety and correctness
4. Pronunciation (25%): Individual sounds, word stress, sentence stress, intonation

Provide:
- Overall band score (4.0-9.0)
- Individual criterion scores
- Detailed feedback for each criterion
- Specific examples from the transcript
- Actionable improvement suggestions

Format your response as structured feedback with clear sections."""
        
        if part_number == 1:
            return base_prompt + "\n\nNote: This is Part 1 (Introduction and Interview) - focus on personal topics and basic interaction."
        elif part_number == 2:
            return base_prompt + "\n\nNote: This is Part 2 (Long Turn) - focus on topic development, coherence, and sustained speech."
        else:
            return base_prompt + "\n\nNote: This is Part 3 (Discussion) - focus on abstract thinking, analysis, and complex language."
    
    def _error_response(self, error_message):
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance for easy import
comprehensive_nova_service = ComprehensiveNovaService()

# Convenience functions for backward compatibility
def conduct_speaking_conversation(user_message, context, part_number=1):
    """Conduct speaking conversation"""
    return comprehensive_nova_service.conduct_speaking_conversation(user_message, context, part_number)

def assess_writing_with_nova(essay_text, task_prompt, task_type="task1", assessment_type="academic"):
    """Assess writing with Nova"""
    return comprehensive_nova_service.assess_writing_with_nova(essay_text, task_prompt, task_type, assessment_type)

def analyze_speaking_transcript(transcript_text, part_number=1, question_type="general"):
    """Analyze speaking transcript"""
    return comprehensive_nova_service.analyze_speaking_transcript(transcript_text, part_number, question_type)