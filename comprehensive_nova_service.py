"""
Comprehensive Nova Service Integration
Handles both Nova Sonic (speech) and Nova Micro (text) with proper fallback
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class ComprehensiveNovaService:
    """
    Production service managing both Nova Sonic and Nova Micro models
    """
    
    def __init__(self):
        """Initialize comprehensive Nova service"""
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.nova_sonic_available = False
        self.nova_micro_available = True  # Confirmed working
        self.active_conversations = {}
        
        # Test Nova Sonic availability on initialization
        self._test_nova_sonic_access()
        logger.info(f"Nova service initialized - Sonic: {self.nova_sonic_available}, Micro: {self.nova_micro_available}")
    
    def _test_nova_sonic_access(self):
        """Test if Nova Sonic is accessible"""
        try:
            test_request = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": "Test access"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 10,
                    "temperature": 0.5
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(test_request)
            )
            
            self.nova_sonic_available = True
            logger.info("Nova Sonic access confirmed")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ValidationException':
                logger.warning("Nova Sonic requires account access permissions")
            else:
                logger.error(f"Nova Sonic test failed: {error_code}")
            self.nova_sonic_available = False
    
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation with best available model
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome response
        """
        conversation_id = f"maya_{assessment_type}_{part}_{datetime.now().timestamp()}"
        
        # Get authentic IELTS questions
        questions = self._get_authentic_ielts_questions(assessment_type, part)
        
        if self.nova_sonic_available:
            # Use Nova Sonic for full speech-to-speech
            return self._start_conversation_with_sonic(conversation_id, assessment_type, part, questions)
        else:
            # Use Nova Micro for text-based conversation with clear messaging
            return self._start_conversation_with_micro(conversation_id, assessment_type, part, questions)
    
    def _start_conversation_with_sonic(self, conversation_id, assessment_type, part, questions):
        """Start conversation using Nova Sonic"""
        try:
            system_prompt = self._build_maya_prompt(assessment_type, part, questions)
            
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": system_prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 200,
                    "temperature": 0.7,
                    "topP": 0.9
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            
            maya_text = next((item['text'] for item in content if 'text' in item), "")
            maya_audio = next((item['audio'] for item in content if 'audio' in item), None)
            
            # Store conversation state
            self.active_conversations[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'conversation_history': [{'role': 'assistant', 'content': maya_text}],
                'start_time': datetime.now(),
                'current_question_index': 0,
                'model_used': 'nova_sonic'
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': maya_text,
                'maya_audio': maya_audio,
                'speech_enabled': True,
                'model_used': 'amazon.nova-sonic-v1:0'
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic conversation failed: {e}")
            # Fallback to Nova Micro
            return self._start_conversation_with_micro(conversation_id, assessment_type, part, questions)
    
    def _start_conversation_with_micro(self, conversation_id, assessment_type, part, questions):
        """Start conversation using Nova Micro (text-only)"""
        try:
            system_prompt = self._build_maya_prompt(assessment_type, part, questions)
            
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": f"{system_prompt}\n\nBegin the IELTS speaking assessment now."}]
                    }
                ]
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            maya_text = content[0]['text'] if content else "Welcome to your IELTS speaking assessment."
            
            # Store conversation state
            self.active_conversations[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'conversation_history': [{'role': 'assistant', 'content': maya_text}],
                'start_time': datetime.now(),
                'current_question_index': 0,
                'model_used': 'nova_micro'
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': maya_text,
                'maya_audio': None,
                'speech_enabled': False,
                'model_used': 'amazon.nova-micro-v1:0',
                'note': 'Text-based assessment (speech features require Nova Sonic access)'
            }
            
        except Exception as e:
            logger.error(f"Nova Micro conversation failed: {e}")
            return {
                'success': False,
                'error': f"Service unavailable: {str(e)}",
                'requires_assistance': True
            }
    
    def continue_maya_conversation(self, conversation_id, user_input):
        """Continue conversation with appropriate model"""
        if conversation_id not in self.active_conversations:
            return {'success': False, 'error': 'Conversation not found'}
        
        conversation = self.active_conversations[conversation_id]
        model_used = conversation['model_used']
        
        if model_used == 'nova_sonic' and self.nova_sonic_available:
            return self._continue_with_sonic(conversation_id, user_input)
        else:
            return self._continue_with_micro(conversation_id, user_input)
    
    def _continue_with_sonic(self, conversation_id, user_input):
        """Continue conversation with Nova Sonic"""
        try:
            conversation = self.active_conversations[conversation_id]
            conversation['conversation_history'].append({'role': 'user', 'content': user_input})
            
            messages = self._build_conversation_messages(conversation)
            
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 150,
                    "temperature": 0.7,
                    "topP": 0.9
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            
            maya_text = next((item['text'] for item in content if 'text' in item), "")
            maya_audio = next((item['audio'] for item in content if 'audio' in item), None)
            
            conversation['conversation_history'].append({'role': 'assistant', 'content': maya_text})
            
            return {
                'success': True,
                'maya_text': maya_text,
                'maya_audio': maya_audio,
                'conversation_continues': True
            }
            
        except Exception as e:
            logger.error(f"Sonic continuation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _continue_with_micro(self, conversation_id, user_input):
        """Continue conversation with Nova Micro"""
        try:
            conversation = self.active_conversations[conversation_id]
            conversation['conversation_history'].append({'role': 'user', 'content': user_input})
            
            # Build conversation context for Nova Micro
            context = f"You are Maya, IELTS examiner. Continue this {conversation['assessment_type']} Part {conversation['part']} assessment.\n\n"
            
            for turn in conversation['conversation_history'][-4:]:
                role = "Examiner" if turn['role'] == 'assistant' else "Candidate"
                context += f"{role}: {turn['content']}\n"
            
            context += "\nRespond naturally as Maya with the next appropriate question or comment:"
            
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": context}]
                    }
                ]
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            maya_text = content[0]['text'] if content else "Please continue."
            
            conversation['conversation_history'].append({'role': 'assistant', 'content': maya_text})
            
            return {
                'success': True,
                'maya_text': maya_text,
                'maya_audio': None,
                'conversation_continues': True
            }
            
        except Exception as e:
            logger.error(f"Micro continuation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_speech_only(self, text):
        """Generate speech from text using best available model"""
        if self.nova_sonic_available:
            return self._generate_speech_with_sonic(text)
        else:
            return {
                'success': False,
                'error': 'Speech generation requires Nova Sonic access',
                'alternative': 'Text-only interaction available'
            }
    
    def _generate_speech_with_sonic(self, text):
        """Generate speech using Nova Sonic"""
        try:
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": f"Say this clearly: {text}"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 50,
                    "temperature": 0.5
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            audio_data = next((item['audio'] for item in content if 'audio' in item), None)
            
            return {
                'success': True,
                'audio_data': audio_data,
                'model_used': 'amazon.nova-sonic-v1:0'
            }
            
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_authentic_ielts_questions(self, assessment_type, part):
        """Get authentic IELTS questions"""
        if part == 1:
            if 'academic' in assessment_type:
                return [
                    "Let's talk about your studies. What subject are you studying?",
                    "Why did you choose this field of study?", 
                    "What do you find most challenging about your studies?",
                    "How do you think your studies will help you in the future?",
                    "Now let's discuss your hometown. Where are you from?",
                    "What do you like most about your hometown?",
                    "Has your hometown changed much since you were a child?",
                    "Would you recommend your hometown to visitors? Why?"
                ]
            else:
                return [
                    "Let's talk about your work. What kind of work do you do?",
                    "How long have you been doing this job?",
                    "What do you enjoy most about your work?",
                    "What are your plans for the future regarding work?",
                    "Now let's discuss your free time. What do you like to do when you're not working?",
                    "Have your hobbies changed since you were younger?",
                    "Do you prefer spending time alone or with other people?",
                    "Is there a new hobby you would like to try?"
                ]
        elif part == 2:
            return [
                {
                    "topic": "Describe a book that had a significant impact on you",
                    "points": ["What the book was about", "When you read it", "Why it was significant to you", "How it influenced your thinking"]
                }
            ]
        else:
            return [
                "How important do you think reading is in today's digital age?",
                "What role should governments play in promoting literacy?",
                "Do you think people read less now than in the past? Why?"
            ]
    
    def _build_maya_prompt(self, assessment_type, part, questions):
        """Build Maya's system prompt"""
        part_descriptions = {
            1: "Part 1: Personal questions about familiar topics (4-5 minutes)",
            2: "Part 2: Individual long turn with cue card topic (3-4 minutes)", 
            3: "Part 3: Abstract discussion questions related to Part 2 (4-5 minutes)"
        }
        
        return f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment.

ASSESSMENT TYPE: {assessment_type.replace('_', ' ').title()}
CURRENT PART: {part_descriptions.get(part, f'Part {part}')}

EXAMINER INSTRUCTIONS:
- Start immediately with a warm, professional welcome
- Use clear British English
- Follow authentic IELTS test procedures
- Ask questions naturally, one at a time
- Listen carefully and provide appropriate follow-up questions
- Maintain encouraging but professional demeanor

QUESTIONS FOR THIS PART:
{json.dumps(questions[:3], indent=2)}

Begin now with your welcome message and first question. Speak as Maya would in a real IELTS speaking test."""
    
    def _build_conversation_messages(self, conversation):
        """Build conversation messages for Nova models"""
        messages = [
            {
                "role": "system",
                "content": [{"text": f"You are Maya, continuing an IELTS {conversation['assessment_type']} Part {conversation['part']} assessment. Respond naturally to the candidate's answer and ask your next appropriate question."}]
            }
        ]
        
        for turn in conversation['conversation_history'][-4:]:
            messages.append({
                "role": turn['role'],
                "content": [{"text": turn['content']}]
            })
        
        return messages