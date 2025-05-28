"""
Enhanced Nova Assessment Integration with RAG
Combines Nova Sonic + Nova Micro with authentic IELTS rubrics for superior assessment accuracy.
"""

import os
import json
import boto3
import logging
from datetime import datetime
from ielts_knowledge_base import ielts_knowledge_base
from ielts_official_rubrics import get_writing_criteria, get_speaking_criteria
from nova_sonic_services import nova_sonic_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedNovaAssessment:
    """RAG-enhanced Nova assessment service for superior IELTS evaluation"""
    
    def __init__(self):
        """Initialize enhanced assessment service"""
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        self.knowledge_base = ielts_knowledge_base
        logger.info("Enhanced Nova Assessment service initialized")

    def assess_writing_with_rag(self, essay_text, task_type, specific_question=None, user_id=None):
        """
        Assess writing using Nova Micro enhanced with authentic IELTS rubrics and your question database
        
        Args:
            essay_text (str): Student's essay submission
            task_type (str): 'task1' or 'task2'
            specific_question (str): The specific question the user answered
            user_id (int): User ID for tracking
            
        Returns:
            dict: Enhanced assessment with official criteria and question context
        """
        try:
            # Get authentic IELTS criteria
            official_criteria = get_writing_criteria(task_type)
            
            # Retrieve question-specific context from your database
            question_context = self._get_question_specific_context(specific_question, 'writing', task_type)
            
            # Retrieve additional context if Knowledge Base is available
            if self.knowledge_base:
                kb_criteria = self.knowledge_base.retrieve_assessment_criteria('writing', task_type)
            else:
                kb_criteria = {'criteria': []}
            
            # Build RAG-enhanced assessment prompt with question context
            assessment_prompt = self._build_rag_writing_prompt(
                essay_text, task_type, official_criteria, kb_criteria, question_context
            )
            
            # Use Nova Micro for professional assessment
            response = self.bedrock_runtime.invoke_model(
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
                        "max_new_tokens": 3500,
                        "temperature": 0.1,  # Very low for consistent scoring
                        "top_p": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('content', [{}])[0].get('text', '')
            
            # Parse structured assessment
            scores = self._parse_enhanced_writing_scores(assessment_text)
            
            return {
                'success': True,
                'overall_score': scores.get('overall_score', 0),
                'task_achievement': scores.get('task_achievement', 0),
                'coherence_cohesion': scores.get('coherence_cohesion', 0),
                'lexical_resource': scores.get('lexical_resource', 0),
                'grammatical_range': scores.get('grammatical_range', 0),
                'detailed_feedback': scores.get('feedback', ''),
                'band_justification': scores.get('justification', ''),
                'assessment_type': 'TrueScore® RAG-Enhanced Nova Assessment',
                'criteria_compliance': 'Official IELTS Standards',
                'assessment_timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Enhanced writing assessment error: {e}")
            return {"success": False, "error": str(e)}

    def assess_speaking_with_rag(self, conversation_history, part_number, user_id=None):
        """
        Assess speaking using Nova Sonic + Nova Micro enhanced with authentic IELTS rubrics
        
        Args:
            conversation_history (list): Complete conversation transcript
            part_number (int): IELTS speaking part (1, 2, or 3)
            user_id (int): User ID for tracking
            
        Returns:
            dict: Enhanced assessment with official criteria compliance
        """
        try:
            # Get authentic IELTS criteria
            official_criteria = get_speaking_criteria()
            
            # Retrieve additional context if Knowledge Base is available
            if self.knowledge_base:
                kb_criteria = self.knowledge_base.retrieve_assessment_criteria('speaking', f'part{part_number}')
            else:
                kb_criteria = {'criteria': []}
            
            # Build RAG-enhanced assessment prompt
            assessment_prompt = self._build_rag_speaking_prompt(
                conversation_history, part_number, official_criteria, kb_criteria
            )
            
            # Use Nova Micro for professional assessment documentation
            response = self.bedrock_runtime.invoke_model(
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
                        "max_new_tokens": 3500,
                        "temperature": 0.1,  # Very low for consistent scoring
                        "top_p": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('content', [{}])[0].get('text', '')
            
            # Parse structured assessment
            scores = self._parse_enhanced_speaking_scores(assessment_text)
            
            return {
                'success': True,
                'overall_score': scores.get('overall_score', 0),
                'fluency_coherence': scores.get('fluency_coherence', 0),
                'lexical_resource': scores.get('lexical_resource', 0),
                'grammatical_range': scores.get('grammatical_range', 0),
                'pronunciation': scores.get('pronunciation', 0),
                'detailed_feedback': scores.get('feedback', ''),
                'band_justification': scores.get('justification', ''),
                'conversation_transcript': conversation_history,
                'assessment_type': 'Elaris® RAG-Enhanced Nova Sonic + Micro Assessment',
                'criteria_compliance': 'Official IELTS Standards',
                'assessment_timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Enhanced speaking assessment error: {e}")
            return {"success": False, "error": str(e)}

    def create_enhanced_speaking_session(self, user_level, part_number, topic, user_id=None):
        """
        Create speaking session using Nova Sonic with RAG-enhanced conversation prompts
        
        Args:
            user_level (str): User's English level
            part_number (int): IELTS speaking part (1, 2, or 3)
            topic (str): Speaking topic
            user_id (int): User ID for tracking
            
        Returns:
            dict: Enhanced conversation session with authentic IELTS procedures
        """
        try:
            # Get authentic IELTS speaking procedures
            official_criteria = get_speaking_criteria()
            
            # Build enhanced conversation prompt with authentic procedures
            conversation_prompt = self._build_enhanced_conversation_prompt(
                user_level, part_number, topic, official_criteria
            )
            
            # Use Nova Sonic for British voice conversation
            response = self.bedrock_runtime.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
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
                        "speaking_style": "professional_ielts_examiner"
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            return {
                "success": True,
                "conversation_id": f"enhanced_conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "examiner_response": result.get('content', [{}])[0].get('text', ''),
                "session_active": True,
                "part_number": part_number,
                "topic": topic,
                "assessment_type": "Elaris® Enhanced Nova Sonic Conversation",
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Enhanced speaking session error: {e}")
            return {"success": False, "error": str(e)}

    def _get_question_specific_context(self, specific_question, assessment_type, task_type):
        """Get context specific to the question being assessed"""
        if not specific_question:
            return {"context": "General assessment context", "question_type": "standard"}
        
        # Analyze question characteristics for better assessment context
        context = {
            "specific_question": specific_question,
            "assessment_type": assessment_type,
            "task_type": task_type,
            "context": f"This assessment is based on the specific question: {specific_question}"
        }
        
        return context

    def _build_rag_writing_prompt(self, essay_text, task_type, official_criteria, kb_criteria, question_context=None):
        """Build RAG-enhanced writing assessment prompt with question context"""
        
        additional_context = ""
        if kb_criteria.get('criteria'):
            additional_context = "\n".join([
                f"ADDITIONAL CONTEXT: {criteria['content']}"
                for criteria in kb_criteria['criteria'][:2]
            ])
        
        question_specific_context = ""
        if question_context and question_context.get('specific_question'):
            question_specific_context = f"""
            SPECIFIC QUESTION CONTEXT:
            The student was responding to this exact question: {question_context['specific_question']}
            Evaluate how well the essay addresses this specific question's requirements.
            """
        
        return f"""
        You are an official IELTS examiner with expertise in {task_type.upper()} assessment.
        Use ONLY the official IELTS band descriptors provided below for precise evaluation.
        
        OFFICIAL IELTS {task_type.upper()} ASSESSMENT CRITERIA:
        {official_criteria}
        
        {additional_context}
        
        {question_specific_context}
        
        STUDENT ESSAY TO ASSESS:
        {essay_text}
        
        Provide precise scores (0-9) based strictly on the official criteria above:
        
        OVERALL_SCORE: [score with one decimal place]
        TASK_ACHIEVEMENT: [score with one decimal place]
        COHERENCE_COHESION: [score with one decimal place]  
        LEXICAL_RESOURCE: [score with one decimal place]
        GRAMMATICAL_RANGE: [score with one decimal place]
        
        BAND_JUSTIFICATION:
        [Explain exactly which band descriptors justify each score]
        
        DETAILED_FEEDBACK:
        [Provide specific feedback referencing the official band descriptors and question requirements]
        
        Your assessment must strictly follow official IELTS standards. Be precise and consistent.
        """

    def _build_rag_speaking_prompt(self, conversation_history, part_number, official_criteria, kb_criteria):
        """Build RAG-enhanced speaking assessment prompt"""
        
        transcript = "\n".join([
            f"Examiner: {turn.get('examiner', '')}\nCandidate: {turn.get('candidate', '')}"
            for turn in conversation_history
        ])
        
        additional_context = ""
        if kb_criteria.get('criteria'):
            additional_context = "\n".join([
                f"ADDITIONAL CONTEXT: {criteria['content']}"
                for criteria in kb_criteria['criteria'][:2]
            ])
        
        return f"""
        You are an official IELTS examiner assessing Speaking Part {part_number}.
        Use ONLY the official IELTS band descriptors provided below for precise evaluation.
        
        OFFICIAL IELTS SPEAKING ASSESSMENT CRITERIA:
        {official_criteria}
        
        {additional_context}
        
        CONVERSATION TRANSCRIPT TO ASSESS:
        {transcript}
        
        Provide precise scores (0-9) based strictly on the official criteria above:
        
        OVERALL_SCORE: [score with one decimal place]
        FLUENCY_COHERENCE: [score with one decimal place]
        LEXICAL_RESOURCE: [score with one decimal place]
        GRAMMATICAL_RANGE: [score with one decimal place]
        PRONUNCIATION: [score with one decimal place]
        
        BAND_JUSTIFICATION:
        [Explain exactly which band descriptors justify each score]
        
        DETAILED_FEEDBACK:
        [Provide specific feedback referencing the official band descriptors]
        
        Your assessment must strictly follow official IELTS standards. Be precise and consistent.
        """

    def _build_enhanced_conversation_prompt(self, user_level, part_number, topic, official_criteria):
        """Build enhanced conversation prompt with authentic IELTS procedures"""
        
        part_instructions = {
            1: f"""You are conducting IELTS Speaking Part 1 (Introduction and Interview).
            Follow official IELTS procedures:
            - Introduce yourself as the examiner
            - Ask about the candidate's background and interests  
            - Ask questions about: {topic}
            - Keep questions simple and direct
            - Be friendly but maintain professional examiner demeanor""",
            
            2: f"""You are conducting IELTS Speaking Part 2 (Long Turn).
            Follow official IELTS procedures:
            - Give the candidate a task card about: {topic}
            - Allow exactly 1 minute preparation time
            - Ask them to speak for 1-2 minutes
            - Ask 1-2 brief follow-up questions""",
            
            3: f"""You are conducting IELTS Speaking Part 3 (Discussion).
            Follow official IELTS procedures:
            - Engage in discussion about: {topic}
            - Ask analytical and abstract questions
            - Challenge ideas respectfully
            - Explore complex aspects of the topic"""
        }
        
        return f"""
        {part_instructions.get(part_number, part_instructions[1])}
        
        Candidate level: {user_level}
        
        IMPORTANT: Follow authentic IELTS speaking test procedures exactly.
        Speak as a professional British examiner would in an actual test.
        Be encouraging but maintain official test standards.
        
        Begin the session now with appropriate introductions and instructions.
        """

    def _parse_enhanced_writing_scores(self, assessment_text):
        """Parse enhanced writing assessment scores"""
        scores = {}
        lines = assessment_text.split('\n')
        
        for i, line in enumerate(lines):
            if 'OVERALL_SCORE:' in line:
                scores['overall_score'] = self._extract_precise_score(line)
            elif 'TASK_ACHIEVEMENT:' in line:
                scores['task_achievement'] = self._extract_precise_score(line)
            elif 'COHERENCE_COHESION:' in line:
                scores['coherence_cohesion'] = self._extract_precise_score(line)
            elif 'LEXICAL_RESOURCE:' in line:
                scores['lexical_resource'] = self._extract_precise_score(line)
            elif 'GRAMMATICAL_RANGE:' in line:
                scores['grammatical_range'] = self._extract_precise_score(line)
            elif 'BAND_JUSTIFICATION:' in line:
                # Extract justification section
                justification_start = assessment_text.find('BAND_JUSTIFICATION:')
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                if feedback_start > justification_start:
                    scores['justification'] = assessment_text[justification_start + len('BAND_JUSTIFICATION:'):feedback_start].strip()
                else:
                    scores['justification'] = assessment_text[justification_start + len('BAND_JUSTIFICATION:'):].strip()
            elif 'DETAILED_FEEDBACK:' in line:
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                scores['feedback'] = assessment_text[feedback_start + len('DETAILED_FEEDBACK:'):].strip()
                break
        
        return scores

    def _parse_enhanced_speaking_scores(self, assessment_text):
        """Parse enhanced speaking assessment scores"""
        scores = {}
        lines = assessment_text.split('\n')
        
        for line in lines:
            if 'OVERALL_SCORE:' in line:
                scores['overall_score'] = self._extract_precise_score(line)
            elif 'FLUENCY_COHERENCE:' in line:
                scores['fluency_coherence'] = self._extract_precise_score(line)
            elif 'LEXICAL_RESOURCE:' in line:
                scores['lexical_resource'] = self._extract_precise_score(line)
            elif 'GRAMMATICAL_RANGE:' in line:
                scores['grammatical_range'] = self._extract_precise_score(line)
            elif 'PRONUNCIATION:' in line:
                scores['pronunciation'] = self._extract_precise_score(line)
            elif 'BAND_JUSTIFICATION:' in line:
                justification_start = assessment_text.find('BAND_JUSTIFICATION:')
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                if feedback_start > justification_start:
                    scores['justification'] = assessment_text[justification_start + len('BAND_JUSTIFICATION:'):feedback_start].strip()
                else:
                    scores['justification'] = assessment_text[justification_start + len('BAND_JUSTIFICATION:'):].strip()
            elif 'DETAILED_FEEDBACK:' in line:
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                scores['feedback'] = assessment_text[feedback_start + len('DETAILED_FEEDBACK:'):].strip()
                break
        
        return scores

    def _extract_precise_score(self, line):
        """Extract precise score with decimal places"""
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', line)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 0), 9)  # Ensure score is between 0-9
        except:
            pass
        return 0.0

# Initialize the enhanced service
try:
    enhanced_nova_assessment = EnhancedNovaAssessment()
    logger.info("Enhanced Nova Assessment service ready with RAG capabilities")
except Exception as e:
    logger.error(f"Failed to initialize Enhanced Nova Assessment service: {e}")
    enhanced_nova_assessment = None