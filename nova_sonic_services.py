"""
Nova Sonic Integration for IELTS Conversational Speaking Assessment
This module provides real-time conversational assessment using Amazon Nova Sonic
for lifelike IELTS speaking practice sessions.
"""

import os
import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovaSonicService:
    """Service for Nova Sonic conversational assessments"""
    
    def __init__(self):
        """Initialize Nova Sonic service with AWS credentials"""
        try:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1',  # Nova Sonic is available in us-east-1
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            logger.info("Nova Sonic service initialized successfully")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found for Nova Sonic")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic: {e}")
            raise

    def create_speaking_conversation(self, user_level, part_number, topic):
        """
        Create a conversational speaking session with Nova Sonic
        
        Args:
            user_level (str): User's English level (beginner, intermediate, advanced)
            part_number (int): IELTS speaking part (1, 2, or 3)
            topic (str): Speaking topic for the session
            
        Returns:
            dict: Conversation session details
        """
        try:
            # Configure Nova Sonic for conversational assessment
            conversation_prompt = self._build_conversation_prompt(user_level, part_number, topic)
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',  # Nova Sonic model ID
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "prompt": conversation_prompt,
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "conversation_mode": True,
                    "speaking_assessment": True
                })
            )
            
            result = json.loads(response['body'].read())
            
            return {
                "success": True,
                "conversation_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "examiner_response": result.get('completion', ''),
                "session_active": True,
                "part_number": part_number,
                "topic": topic
            }
            
        except ClientError as e:
            logger.error(f"Nova Sonic conversation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected Nova Sonic error: {e}")
            return {"success": False, "error": str(e)}

    def continue_conversation(self, conversation_id, user_response, conversation_history):
        """
        Continue an ongoing conversation with Nova Sonic
        
        Args:
            conversation_id (str): Active conversation ID
            user_response (str): User's spoken response (transcribed)
            conversation_history (list): Previous conversation turns
            
        Returns:
            dict: Examiner's response and assessment
        """
        try:
            # Build conversation context
            context = self._build_conversation_context(conversation_history, user_response)
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "prompt": context,
                    "max_tokens": 1500,
                    "temperature": 0.7,
                    "conversation_mode": True,
                    "continue_assessment": True
                })
            )
            
            result = json.loads(response['body'].read())
            
            return {
                "success": True,
                "examiner_response": result.get('completion', ''),
                "assessment_notes": self._extract_assessment_notes(result),
                "continue_conversation": True
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation error: {e}")
            return {"success": False, "error": str(e)}

    def finalize_conversation_assessment(self, conversation_history, part_number):
        """
        Generate final assessment for the conversational session
        
        Args:
            conversation_history (list): Complete conversation transcript
            part_number (int): IELTS speaking part number
            
        Returns:
            dict: Final assessment with scores and feedback
        """
        try:
            assessment_prompt = self._build_final_assessment_prompt(conversation_history, part_number)
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "prompt": assessment_prompt,
                    "max_tokens": 2500,
                    "temperature": 0.3,  # Lower temperature for consistent scoring
                    "assessment_mode": True
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('completion', '')
            
            # Parse the structured assessment
            scores = self._parse_assessment_scores(assessment_text)
            
            return {
                "success": True,
                "overall_score": scores.get('overall_score', 0),
                "fluency_coherence": scores.get('fluency_coherence', 0),
                "lexical_resource": scores.get('lexical_resource', 0),
                "grammatical_range": scores.get('grammatical_range', 0),
                "pronunciation": scores.get('pronunciation', 0),
                "detailed_feedback": scores.get('feedback', ''),
                "conversation_transcript": conversation_history,
                "assessment_type": "Nova Sonic Conversational"
            }
            
        except Exception as e:
            logger.error(f"Final assessment error: {e}")
            return {"success": False, "error": str(e)}

    def _build_conversation_prompt(self, user_level, part_number, topic):
        """Build the initial conversation prompt for Nova Sonic"""
        
        part_instructions = {
            1: f"""You are an IELTS examiner conducting Part 1 (Introduction and Interview).
            Ask questions about the candidate's background, interests, and the topic: {topic}.
            Keep questions simple and direct. Be friendly but professional.""",
            
            2: f"""You are an IELTS examiner conducting Part 2 (Long Turn).
            Give the candidate a task card about: {topic}.
            Allow them to speak for 1-2 minutes, then ask 1-2 follow-up questions.""",
            
            3: f"""You are an IELTS examiner conducting Part 3 (Discussion).
            Engage in a discussion about: {topic}.
            Ask analytical and abstract questions. Challenge their ideas respectfully."""
        }
        
        return f"""
        {part_instructions.get(part_number, part_instructions[1])}
        
        The candidate's level appears to be: {user_level}
        
        Start the conversation now. Be natural, encouraging, and follow IELTS speaking test procedures.
        Respond as if you're speaking aloud - keep it conversational, not written.
        """

    def _build_conversation_context(self, history, new_response):
        """Build context for continuing the conversation"""
        context = "IELTS Speaking Assessment Conversation:\n\n"
        
        for turn in history:
            context += f"Examiner: {turn.get('examiner', '')}\n"
            context += f"Candidate: {turn.get('candidate', '')}\n\n"
        
        context += f"Candidate's latest response: {new_response}\n\n"
        context += "Continue as the IELTS examiner. Respond naturally and assess their language use."
        
        return context

    def _build_final_assessment_prompt(self, conversation_history, part_number):
        """Build prompt for final assessment"""
        transcript = "\n".join([
            f"Examiner: {turn.get('examiner', '')}\nCandidate: {turn.get('candidate', '')}"
            for turn in conversation_history
        ])
        
        return f"""
        Assess this IELTS Speaking Part {part_number} conversation using the official IELTS band descriptors.
        
        CONVERSATION TRANSCRIPT:
        {transcript}
        
        Provide scores (0-9) for each criterion and detailed feedback:
        
        OVERALL_SCORE: [score]
        FLUENCY_COHERENCE: [score]
        LEXICAL_RESOURCE: [score]
        GRAMMATICAL_RANGE: [score]
        PRONUNCIATION: [score]
        
        DETAILED_FEEDBACK:
        [Provide specific feedback on strengths and areas for improvement]
        
        Focus on: naturalness, vocabulary range, grammar accuracy, fluency, and pronunciation.
        """

    def _parse_assessment_scores(self, assessment_text):
        """Parse scores from assessment text"""
        scores = {}
        lines = assessment_text.split('\n')
        
        for line in lines:
            if 'OVERALL_SCORE:' in line:
                scores['overall_score'] = self._extract_score(line)
            elif 'FLUENCY_COHERENCE:' in line:
                scores['fluency_coherence'] = self._extract_score(line)
            elif 'LEXICAL_RESOURCE:' in line:
                scores['lexical_resource'] = self._extract_score(line)
            elif 'GRAMMATICAL_RANGE:' in line:
                scores['grammatical_range'] = self._extract_score(line)
            elif 'PRONUNCIATION:' in line:
                scores['pronunciation'] = self._extract_score(line)
            elif 'DETAILED_FEEDBACK:' in line:
                # Extract everything after this line as feedback
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                scores['feedback'] = assessment_text[feedback_start + len('DETAILED_FEEDBACK:'):].strip()
                break
        
        return scores

    def _extract_score(self, line):
        """Extract numeric score from a line"""
        try:
            # Look for numbers in the line
            import re
            numbers = re.findall(r'\d+\.?\d*', line)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 0), 9)  # Ensure score is between 0-9
        except:
            pass
        return 0

    def _extract_assessment_notes(self, result):
        """Extract assessment notes from ongoing conversation"""
        # This could be enhanced to extract real-time assessment notes
        return "Assessment in progress..."

# Initialize the service
try:
    nova_sonic_service = NovaSonicService()
    logger.info("Nova Sonic service ready for conversational assessments")
except Exception as e:
    logger.error(f"Failed to initialize Nova Sonic service: {e}")
    nova_sonic_service = None