"""
Nova Sonic Integration for IELTS Conversational Speaking Assessment
This module provides real-time conversational assessment using Amazon Nova Sonic
for authentic British voice conversation and IELTS assessment with official criteria.
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

# Export the main service class with the expected name

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

    def assess_browser_transcript(self, transcript, conversation_history, part_number):
        """
        Assess user speech from browser-generated transcript using Nova Sonic
        
        Args:
            transcript (str): User's speech converted to text by browser
            conversation_history (list): Previous conversation messages
            part_number (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Assessment and next examiner response
        """
        try:
            # Create context-aware assessment prompt
            conversation_context = "\n".join([
                f"{msg['speaker']}: {msg['message']}" 
                for msg in conversation_history[-5:]  # Last 5 exchanges for context
            ])
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "system",
                            "content": f"""You are Maya, a professional IELTS examiner using ClearScore technology. 

CONTEXT: This is Part {part_number} of the IELTS Speaking test.
RECENT CONVERSATION:
{conversation_context}

USER'S LATEST RESPONSE: "{transcript}"

Provide:
1. A natural examiner response to continue the conversation
2. Real-time assessment notes on: fluency, vocabulary, grammar, pronunciation (based on text patterns)
3. If appropriate, transition to next question or part

Respond as a professional but friendly British examiner. Keep responses conversational and natural."""
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 500,
                        "temperature": 0.7
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            if 'content' in result and result['content']:
                examiner_response = result['content'][0]['text']
                
                return {
                    "success": True,
                    "response": examiner_response,
                    "assessment_notes": f"Processed transcript: {len(transcript)} characters",
                    "next_part": part_number
                }
            else:
                logger.warning("No content in Nova Sonic response")
                return {"success": False, "error": "No response generated"}
                
        except ClientError as e:
            logger.error(f"Nova Sonic assessment error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected assessment error: {e}")
            return {"success": False, "error": str(e)}

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
                modelId='amazon.nova-sonic-v1:0',  # Using Nova Sonic for conversational speech
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": conversation_prompt
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 2000,
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    "additionalModelRequestFields": {
                        "voice": "british_female",
                        "speaking_style": "professional_examiner"
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            return {
                "success": True,
                "conversation_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "examiner_response": result.get('content', [{}])[0].get('text', ''),
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
                modelId='amazon.nova-sonic-v1:0',  # Nova Sonic for continued conversation
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": context
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 1500,
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    "additionalModelRequestFields": {
                        "voice": "british_female",
                        "speaking_style": "professional_examiner"
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            return {
                "success": True,
                "examiner_response": result.get('content', [{}])[0].get('text', ''),
                "assessment_notes": self._extract_assessment_notes(result),
                "continue_conversation": True
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation error: {e}")
            return {"success": False, "error": str(e)}

    def finalize_conversation_assessment(self, conversation_history, part_number):
        """
        Generate final assessment for the conversational session
        Uses Nova Micro for professional assessment documentation
        
        Args:
            conversation_history (list): Complete conversation transcript
            part_number (int): IELTS speaking part number
            
        Returns:
            dict: Final assessment with scores and feedback
        """
        try:
            assessment_prompt = self._build_final_assessment_prompt(conversation_history, part_number)
            
            # Use Nova Micro for professional assessment documentation
            response = self.client.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": assessment_prompt
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 2500,
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('content', [{}])[0].get('text', '')
            
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
                "assessment_type": "Nova Sonic + Nova Micro Professional Assessment"
            }
            
        except Exception as e:
            logger.error(f"Final assessment error: {e}")
            return {"success": False, "error": str(e)}

    def assess_conversation_final(self, conversation_history, assessment_type='Academic Speaking'):
        """
        Provide final assessment and scoring for the complete conversation
        
        Args:
            conversation_history (list): Complete conversation between examiner and candidate
            assessment_type (str): Type of assessment (Academic Speaking, General Speaking)
            
        Returns:
            dict: Final scores and detailed feedback
        """
        try:
            # Build final assessment prompt
            assessment_prompt = self._build_final_assessment_prompt(conversation_history, assessment_type)
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": assessment_prompt
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 2000,
                        "temperature": 0.3,
                        "top_p": 0.8
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('content', [{}])[0].get('text', '')
            
            # Parse assessment scores
            scores = self._parse_assessment_scores(assessment_text)
            
            return {
                "success": True,
                "overall_score": scores.get('overall_score', 6.0),
                "fluency_coherence": scores.get('fluency_coherence', 6.0),
                "lexical_resource": scores.get('lexical_resource', 6.0),
                "grammatical_range": scores.get('grammatical_range', 6.0),
                "pronunciation": scores.get('pronunciation', 6.0),
                "detailed_feedback": assessment_text,
                "strengths": scores.get('strengths', []),
                "improvements": scores.get('improvements', [])
            }
            
        except Exception as e:
            logger.error(f"Final conversation assessment error: {e}")
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

    def generate_speech(self, text, voice='british_female', style='professional_examiner'):
        """
        Generate speech audio using Nova Sonic for Elaris® British voice
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice type (british_female for Elaris®)
            style (str): Speaking style (professional_examiner)
            
        Returns:
            dict: Speech generation result with audio data
        """
        try:
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": f"Generate natural speech for: {text}"
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 1000,
                        "temperature": 0.3
                    },
                    "additionalModelRequestFields": {
                        "voice": voice,
                        "speaking_style": style,
                        "output_format": "audio/wav"
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            if 'audio_data' in result:
                return {
                    "success": True,
                    "audio_data": result['audio_data'],
                    "audio_url": f"data:audio/wav;base64,{result['audio_data']}"
                }
            else:
                logger.warning("No audio data in Nova Sonic response")
                return {"success": False, "error": "No audio generated"}
                
        except ClientError as e:
            logger.error(f"Nova Sonic speech generation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected speech generation error: {e}")
            return {"success": False, "error": str(e)}

# Initialize the service
try:
    nova_sonic_service = NovaSonicService()
    logger.info("Nova Sonic service ready for conversational assessments")
except Exception as e:
    logger.error(f"Failed to initialize Nova Sonic service: {e}")
    nova_sonic_service = None

# Export the service with expected name for compatibility
NovaService = NovaSonicService