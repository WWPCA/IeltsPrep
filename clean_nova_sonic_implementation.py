"""
Clean Nova Sonic Implementation
Removes all legacy speech service conflicts and implements proper Nova Sonic access
"""

import os
import boto3
import json
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CleanNovaSonicService:
    """
    Clean Nova Sonic implementation without legacy conflicts
    """
    
    def __init__(self):
        """Initialize with automatic access detection"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.nova_access = self._test_nova_access()
            self.conversation_state = {}
            logger.info(f"Clean Nova Sonic service initialized - Access: {self.nova_access}")
        except Exception as e:
            logger.error(f"Failed to initialize Clean Nova Sonic service: {e}")
            self.nova_access = False
    
    def _test_nova_access(self):
        """Test Nova Sonic access with minimal request"""
        try:
            test_request = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": "Test"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 10,
                    "temperature": 0.5
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(test_request)
            )
            
            logger.info("Nova Sonic access confirmed")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.warning(f"Nova Sonic access issue: {error_code}")
            
            # Test Nova Lite as fallback
            try:
                response = self.client.invoke_model(
                    modelId='amazon.nova-lite-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(test_request)
                )
                logger.info("Nova Lite access confirmed as fallback")
                self.fallback_model = 'amazon.nova-lite-v1:0'
                return 'lite'
            except Exception:
                logger.error("No Nova models accessible")
                return False
        
        except Exception as e:
            logger.error(f"Nova access test failed: {e}")
            return False
    
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation with proper Nova Sonic implementation
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome response
        """
        try:
            conversation_id = f"clean_maya_{assessment_type}_{part}_{datetime.now().timestamp()}"
            
            # Get authentic IELTS questions
            questions = self._get_authentic_questions(assessment_type, part)
            
            # Build Maya's prompt
            system_prompt = self._build_maya_prompt(assessment_type, part, questions)
            
            # Get Maya's response using available Nova model
            maya_response = self._get_nova_response(system_prompt, use_speech=True)
            
            # Initialize conversation state
            self.conversation_state[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'history': [{'role': 'assistant', 'content': maya_response['text']}],
                'start_time': datetime.now(),
                'speech_enabled': maya_response.get('has_audio', False)
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': maya_response['text'],
                'maya_audio': maya_response.get('audio_data'),
                'speech_enabled': maya_response.get('has_audio', False),
                'model_used': self._get_current_model()
            }
            
        except Exception as e:
            logger.error(f"Failed to start Maya conversation: {e}")
            return {
                'success': False,
                'error': f"Could not start conversation: {str(e)}"
            }
    
    def continue_maya_conversation(self, conversation_id, user_input):
        """
        Continue conversation with Maya
        
        Args:
            conversation_id (str): Active conversation ID
            user_input (str): User's text response
            
        Returns:
            dict: Maya's response
        """
        try:
            if conversation_id not in self.conversation_state:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.conversation_state[conversation_id]
            
            # Add user response to history
            conversation['history'].append({'role': 'user', 'content': user_input})
            
            # Generate Maya's response
            maya_response = self._generate_maya_followup(conversation, user_input)
            
            # Update history
            conversation['history'].append({'role': 'assistant', 'content': maya_response['text']})
            
            return {
                'success': True,
                'maya_text': maya_response['text'],
                'maya_audio': maya_response.get('audio_data'),
                'conversation_continues': True
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_authentic_questions(self, assessment_type, part):
        """Get authentic IELTS questions"""
        # Part 1 questions
        part1_academic = [
            "Let's talk about your studies. What subject are you studying?",
            "Why did you choose this field of study?",
            "What do you find most interesting about your studies?",
            "Do you think your studies will help you in your future career?",
            "Let's move on to talk about your hometown. Where are you from?",
            "What do you like most about your hometown?",
            "Has your hometown changed much since you were a child?",
            "Would you like to live somewhere else in the future?"
        ]
        
        part1_general = [
            "Let's talk about your work. What kind of work do you do?",
            "How long have you been doing this job?",
            "What do you enjoy most about your work?",
            "Do you think you'll continue in this job in the future?",
            "Now let's discuss your free time. What do you like to do in your spare time?",
            "Have your hobbies changed since you were younger?",
            "Do you prefer spending time alone or with others?",
            "What new hobby would you like to try?"
        ]
        
        # Part 2 cue cards
        part2_topics = [
            {
                "topic": "Describe a book that had a significant impact on you",
                "points": ["What the book was about", "When you read it", "Why it was significant", "How it influenced you"]
            },
            {
                "topic": "Describe a place you visited that you found particularly interesting",
                "points": ["Where it was", "When you went there", "What you did there", "Why you found it interesting"]
            }
        ]
        
        # Part 3 discussion questions
        part3_questions = [
            "How important do you think reading is in today's digital age?",
            "What role should governments play in promoting literacy?",
            "Do you think travel broadens people's perspectives? How?",
            "What are the environmental impacts of increased tourism?"
        ]
        
        if part == 1:
            return part1_academic if 'academic' in assessment_type else part1_general
        elif part == 2:
            return part2_topics
        else:
            return part3_questions
    
    def _build_maya_prompt(self, assessment_type, part, questions):
        """Build Maya's system prompt"""
        part_descriptions = {
            1: "Part 1: Personal questions about familiar topics (4-5 minutes)",
            2: "Part 2: Individual long turn with cue card (3-4 minutes)", 
            3: "Part 3: Abstract discussion questions (4-5 minutes)"
        }
        
        return f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment.

ASSESSMENT: {assessment_type.replace('_', ' ').title()}
PART: {part_descriptions.get(part, f'Part {part}')}

INSTRUCTIONS:
- Start immediately with a warm, professional welcome
- Follow authentic IELTS test procedures
- Ask questions naturally, one at a time
- Use British English pronunciation and vocabulary
- Be encouraging but maintain professional standards

QUESTIONS FOR THIS PART:
{json.dumps(questions[:3], indent=2)}

Begin now with your welcome and first question."""
    
    def _get_nova_response(self, prompt, use_speech=False):
        """Get response from Nova model"""
        try:
            messages = [
                {
                    "role": "system", 
                    "content": [{"text": prompt}]
                }
            ]
            
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 200,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            # Add speech configuration if Nova Sonic is available
            if self.nova_access == True and use_speech:
                request_body["additionalModelRequestFields"] = {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
                model_id = 'amazon.nova-sonic-v1:0'
            elif self.nova_access == 'lite':
                model_id = 'amazon.nova-lite-v1:0'
            else:
                # Fallback to OpenAI
                return self._get_openai_response(prompt)
            
            response = self.client.invoke_model(
                modelId=model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            
            # Extract text and audio
            text_content = next((item['text'] for item in content if 'text' in item), "")
            audio_content = next((item['audio'] for item in content if 'audio' in item), None)
            
            return {
                'text': text_content,
                'audio_data': audio_content,
                'has_audio': audio_content is not None
            }
            
        except Exception as e:
            logger.error(f"Nova response failed: {e}")
            return self._get_openai_response(prompt)
    
    def _get_openai_response(self, prompt):
        """Fallback to OpenAI"""
        try:
            import openai
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[{'role': 'system', 'content': prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                'text': response.choices[0].message.content,
                'has_audio': False
            }
            
        except Exception as e:
            logger.error(f"OpenAI fallback failed: {e}")
            return {
                'text': "Hello! I'm Maya, your IELTS examiner. Let's begin your speaking assessment.",
                'has_audio': False
            }
    
    def _generate_maya_followup(self, conversation, user_text):
        """Generate Maya's follow-up response"""
        recent_history = conversation['history'][-4:]
        
        context_prompt = f"""You are Maya, continuing an IELTS speaking assessment.

Assessment: {conversation['assessment_type']} Part {conversation['part']}

Recent conversation:
{json.dumps([{'role': turn['role'], 'content': turn['content']} for turn in recent_history], indent=2)}

The candidate just said: "{user_text}"

Respond naturally as Maya - acknowledge their answer and ask your next appropriate question."""
        
        return self._get_nova_response(context_prompt, use_speech=conversation.get('speech_enabled', False))
    
    def _get_current_model(self):
        """Get currently used model"""
        if self.nova_access == True:
            return 'amazon.nova-sonic-v1:0'
        elif self.nova_access == 'lite':
            return 'amazon.nova-lite-v1:0'
        else:
            return 'openai'

def test_clean_implementation():
    """Test the clean Nova Sonic implementation"""
    print("Testing clean Nova Sonic implementation...")
    
    service = CleanNovaSonicService()
    
    if service.nova_access:
        print(f"✓ Nova access confirmed: {service._get_current_model()}")
        
        # Test conversation start
        result = service.start_maya_conversation('academic_speaking', 1)
        if result['success']:
            print("✓ Maya conversation started successfully")
            print(f"Maya says: {result['maya_text'][:100]}...")
            print(f"Speech enabled: {result['speech_enabled']}")
        else:
            print(f"✗ Conversation start failed: {result['error']}")
    else:
        print("✗ No Nova access available")

if __name__ == "__main__":
    test_clean_implementation()