"""
AWS Services Integration
Provides speaking analysis and pronunciation assessment using AWS services
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class AWSServicesManager:
    """Manager for AWS service integrations"""
    
    def __init__(self):
        self.bedrock_client = None
        self.transcribe_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS service clients"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            
            self.transcribe_client = boto3.client(
                'transcribe',
                region_name='us-east-1'
            )
            
            logger.info("AWS service clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
    
    def analyze_speaking_response(self, transcript_text, question_type="general", part_number=1):
        """Analyze speaking response using AWS Bedrock"""
        try:
            if not self.bedrock_client:
                return self._error_response("AWS Bedrock service unavailable")
            
            system_prompt = self._get_speaking_analysis_prompt(question_type, part_number)
            user_prompt = f"""
            Speaking Response Transcript: {transcript_text}
            
            Please provide a comprehensive IELTS Speaking assessment based on this transcript.
            """
            
            response = self._call_bedrock_model(system_prompt, user_prompt)
            
            if response.get('success'):
                return {
                    'success': True,
                    'analysis': response['content'],
                    'question_type': question_type,
                    'part_number': part_number,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Speaking analysis error: {e}")
            return self._error_response(f"Speaking analysis error: {str(e)}")
    
    def analyze_pronunciation(self, audio_text, reference_text=None):
        """Analyze pronunciation quality from transcript"""
        try:
            # Basic pronunciation analysis based on transcript quality
            analysis = {
                'clarity_score': self._assess_clarity(audio_text),
                'fluency_indicators': self._assess_fluency(audio_text),
                'pronunciation_feedback': self._generate_pronunciation_feedback(audio_text)
            }
            
            return {
                'success': True,
                'pronunciation_analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pronunciation analysis error: {e}")
            return self._error_response(f"Pronunciation analysis error: {str(e)}")
    
    def _call_bedrock_model(self, system_prompt, user_prompt):
        """Call AWS Bedrock model for analysis"""
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
                    "max_new_tokens": 1500,
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
            
            return self._error_response("Invalid response from AWS Bedrock")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS Bedrock client error: {e}")
            return self._error_response(f"AWS Bedrock error: {error_code}")
        
        except Exception as e:
            logger.error(f"Unexpected AWS Bedrock error: {e}")
            return self._error_response(f"AWS service error: {str(e)}")
    
    def _get_speaking_analysis_prompt(self, question_type, part_number):
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
    
    def _assess_clarity(self, text):
        """Assess speech clarity from transcript"""
        # Simple heuristic based on text completeness
        word_count = len(text.split())
        incomplete_markers = text.count('[unclear]') + text.count('[inaudible]') + text.count('...')
        
        if word_count == 0:
            return 0.0
        
        clarity_ratio = 1.0 - (incomplete_markers / word_count)
        return max(0.0, min(1.0, clarity_ratio)) * 100
    
    def _assess_fluency(self, text):
        """Assess fluency indicators from transcript"""
        indicators = {
            'hesitations': text.count('um') + text.count('uh') + text.count('er'),
            'false_starts': text.count('[restart]'),
            'long_pauses': text.count('[pause]'),
            'word_count': len(text.split())
        }
        
        return indicators
    
    def _generate_pronunciation_feedback(self, text):
        """Generate pronunciation feedback"""
        feedback = []
        
        if '[unclear]' in text:
            feedback.append("Some words were unclear - focus on articulation")
        
        if text.count('um') + text.count('uh') > 5:
            feedback.append("Reduce filler words to improve fluency")
        
        if len(text.split()) < 20:
            feedback.append("Provide more detailed responses")
        
        if not feedback:
            feedback.append("Good pronunciation clarity")
        
        return feedback
    
    def _error_response(self, error_message):
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance for easy import
aws_services_manager = AWSServicesManager()

# Convenience functions for backward compatibility
def analyze_speaking_response(transcript_text, question_type="general", part_number=1):
    """Analyze speaking response"""
    return aws_services_manager.analyze_speaking_response(transcript_text, question_type, part_number)

def analyze_pronunciation(audio_text, reference_text=None):
    """Analyze pronunciation quality"""
    return aws_services_manager.analyze_pronunciation(audio_text, reference_text)