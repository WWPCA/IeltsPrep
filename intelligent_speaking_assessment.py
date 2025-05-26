"""
Intelligent Speaking Assessment System
This module integrates Nova Sonic with your specific assessment questions
and provides context-aware IELTS speaking evaluation.
"""

import json
import logging
from datetime import datetime
from nova_sonic_services import nova_sonic_service
from models import db, SpeakingPrompt
from flask_login import current_user

logger = logging.getLogger(__name__)

class IntelligentSpeakingAssessment:
    """Context-aware speaking assessment using your assessment questions"""
    
    def __init__(self):
        self.nova_service = nova_sonic_service
        
    def start_assessment_conversation(self, assessment_id, test_type='academic'):
        """
        Start a conversational assessment using your specific question sets
        
        Args:
            assessment_id (int): ID of the CompletePracticeTest
            test_type (str): 'academic' or 'general'
            
        Returns:
            dict: Conversation session with context-aware questions
        """
        try:
            # Get the specific assessment set
            assessment = CompletePracticeTest.query.get(assessment_id)
            if not assessment:
                return {"success": False, "error": "Assessment not found"}
            
            # Parse the assessment questions
            test_data = json.loads(assessment.tests) if assessment.tests else []
            if not test_data:
                return {"success": False, "error": "No questions found in assessment"}
            
            # Get the Part 1 question to start with
            part1_question = self._get_question_by_part(test_data, 1)
            if not part1_question:
                return {"success": False, "error": "Part 1 question not found"}
            
            # Create context-aware conversation prompt
            conversation_prompt = self._build_contextual_prompt(
                part1_question, test_type, assessment.title
            )
            
            # Start the Nova conversation with full context
            result = self.nova_service.create_speaking_conversation(
                user_level=self._determine_user_level(),
                part_number=1,
                topic=part1_question.get('topic', 'General conversation')
            )
            
            if result.get('success'):
                # Store conversation context in session
                conversation_context = {
                    "assessment_id": assessment_id,
                    "test_type": test_type,
                    "assessment_title": assessment.title,
                    "questions": test_data,
                    "current_part": 1,
                    "conversation_history": [],
                    "start_time": datetime.utcnow().isoformat()
                }
                
                result["context"] = conversation_context
                result["specific_question"] = part1_question
                result["assessment_info"] = {
                    "title": assessment.title,
                    "type": test_type,
                    "total_parts": len(test_data)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error starting intelligent assessment: {e}")
            return {"success": False, "error": str(e)}
    
    def continue_contextual_conversation(self, conversation_context, user_response):
        """
        Continue conversation with awareness of specific assessment questions
        
        Args:
            conversation_context (dict): Current conversation state
            user_response (str): User's spoken response
            
        Returns:
            dict: AI examiner response with context awareness
        """
        try:
            current_part = conversation_context.get('current_part', 1)
            questions = conversation_context.get('questions', [])
            
            # Get current question details
            current_question = self._get_question_by_part(questions, current_part)
            
            # Build conversation history
            conversation_history = conversation_context.get('conversation_history', [])
            
            # Add user response to history
            conversation_history.append({
                "speaker": "candidate",
                "response": user_response,
                "part": current_part,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Create intelligent context for Nova
            intelligent_context = self._build_intelligent_context(
                conversation_history, current_question, current_part,
                conversation_context.get('test_type', 'academic')
            )
            
            # Get Nova response with full context
            result = self.nova_service.continue_conversation(
                conversation_context.get('conversation_id', ''),
                user_response,
                conversation_history
            )
            
            if result.get('success'):
                # Add examiner response to history
                conversation_history.append({
                    "speaker": "examiner",
                    "response": result.get('examiner_response', ''),
                    "part": current_part,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Update conversation context
                conversation_context['conversation_history'] = conversation_history
                
                # Determine if we should move to next part
                should_advance = self._should_advance_to_next_part(
                    conversation_history, current_part
                )
                
                if should_advance and current_part < 3:
                    conversation_context['current_part'] = current_part + 1
                    next_question = self._get_question_by_part(questions, current_part + 1)
                    result['next_part_question'] = next_question
                    result['part_transition'] = True
                
                result['conversation_context'] = conversation_context
            
            return result
            
        except Exception as e:
            logger.error(f"Error continuing contextual conversation: {e}")
            return {"success": False, "error": str(e)}
    
    def finalize_intelligent_assessment(self, conversation_context):
        """
        Generate final assessment with awareness of specific questions and criteria
        
        Args:
            conversation_context (dict): Complete conversation state
            
        Returns:
            dict: Comprehensive assessment with IELTS scores
        """
        try:
            conversation_history = conversation_context.get('conversation_history', [])
            assessment_id = conversation_context.get('assessment_id')
            test_type = conversation_context.get('test_type', 'academic')
            
            # Create intelligent assessment prompt with question context
            assessment_prompt = self._build_intelligent_assessment_prompt(
                conversation_history, 
                conversation_context.get('questions', []),
                test_type
            )
            
            # Get final assessment from Nova
            result = self.nova_service.finalize_conversation_assessment(
                conversation_history, 3  # Complete all parts
            )
            
            if result.get('success'):
                # Save assessment to database
                self._save_assessment_results(
                    conversation_context, result, current_user.id
                )
                
                # Add contextual feedback
                result['assessment_context'] = {
                    "assessment_title": conversation_context.get('assessment_title', ''),
                    "test_type": test_type,
                    "questions_covered": len(conversation_context.get('questions', [])),
                    "total_speaking_time": self._calculate_speaking_time(conversation_history)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error finalizing intelligent assessment: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_question_by_part(self, questions, part_number):
        """Get question details for specific part"""
        for question in questions:
            if question.get('part') == part_number:
                prompt_id = question.get('prompt_id')
                if prompt_id:
                    prompt = SpeakingPrompt.query.get(prompt_id)
                    if prompt:
                        return {
                            "id": prompt.id,
                            "part": prompt.part,
                            "prompt": prompt.prompt_text,
                            "topic": getattr(prompt, 'topic', 'General'),
                            "difficulty": getattr(prompt, 'difficulty', 'intermediate')
                        }
        return None
    
    def _build_contextual_prompt(self, question, test_type, assessment_title):
        """Build context-aware conversation prompt"""
        return f"""
        You are conducting an IELTS {test_type.title()} Speaking Assessment: "{assessment_title}"
        
        This is Part {question['part']} - Topic: {question['topic']}
        
        Specific question to ask: {question['prompt']}
        
        Instructions:
        - Follow official IELTS speaking test procedures
        - Be encouraging and professional
        - Ask follow-up questions naturally
        - Assess: fluency, vocabulary, grammar, pronunciation
        - Keep responses conversational, not written
        
        Start the assessment now with the specific question provided.
        """
    
    def _build_intelligent_context(self, history, current_question, part, test_type):
        """Build intelligent context for Nova with question awareness"""
        context = f"IELTS {test_type.title()} Speaking Assessment - Part {part}\n\n"
        
        if current_question:
            context += f"Current topic: {current_question['topic']}\n"
            context += f"Focus question: {current_question['prompt']}\n\n"
        
        context += "Conversation so far:\n"
        for turn in history[-6:]:  # Last 6 turns for context
            speaker = turn['speaker'].title()
            response = turn['response']
            context += f"{speaker}: {response}\n"
        
        context += "\nContinue as IELTS examiner. Ask natural follow-up questions and assess language use."
        return context
    
    def _build_intelligent_assessment_prompt(self, history, questions, test_type):
        """Build assessment prompt with question context"""
        transcript = ""
        for turn in history:
            speaker = turn['speaker'].title()
            response = turn['response']
            transcript += f"{speaker}: {response}\n"
        
        question_context = "Questions covered:\n"
        for i, q in enumerate(questions, 1):
            prompt = SpeakingPrompt.query.get(q.get('prompt_id'))
            if prompt:
                question_context += f"Part {i}: {prompt.topic} - {prompt.prompt}\n"
        
        return f"""
        Assess this IELTS {test_type.title()} Speaking performance using official band descriptors.
        
        {question_context}
        
        COMPLETE CONVERSATION:
        {transcript}
        
        Provide detailed assessment:
        
        OVERALL_SCORE: [0-9 band score]
        FLUENCY_COHERENCE: [0-9 score]
        LEXICAL_RESOURCE: [0-9 score]
        GRAMMATICAL_RANGE: [0-9 score]
        PRONUNCIATION: [0-9 score]
        
        DETAILED_FEEDBACK:
        [Specific feedback on performance, strengths, and improvement areas]
        
        Focus on how well the candidate addressed each specific question and demonstrated IELTS criteria.
        """
    
    def _determine_user_level(self):
        """Determine user's approximate level"""
        if current_user.is_authenticated:
            # Could analyze user's previous scores
            return "intermediate"
        return "intermediate"
    
    def _should_advance_to_next_part(self, history, current_part):
        """Determine if conversation should advance to next part"""
        # Simple logic - advance after sufficient interaction
        part_responses = [turn for turn in history if turn.get('part') == current_part and turn.get('speaker') == 'candidate']
        return len(part_responses) >= 2  # After 2 candidate responses
    
    def _calculate_speaking_time(self, history):
        """Calculate approximate speaking time"""
        candidate_responses = [turn for turn in history if turn.get('speaker') == 'candidate']
        # Rough estimate: 150 words per minute average speaking speed
        total_words = sum(len(turn['response'].split()) for turn in candidate_responses)
        return f"{total_words // 150} minutes {(total_words % 150) // 2.5:.0f} seconds"
    
    def _save_assessment_results(self, context, results, user_id):
        """Save assessment results to database"""
        try:
            # Create UserTestAttempt record
            test_attempt = UserTestAttempt(
                user_id=user_id,
                test_id=context.get('assessment_id'),
                test_type='speaking',
                ielts_test_type=context.get('test_type', 'academic'),
                attempt_date=datetime.utcnow(),
                overall_score=results.get('overall_score', 0),
                fluency_coherence=results.get('fluency_coherence', 0),
                lexical_resource=results.get('lexical_resource', 0),
                grammatical_range=results.get('grammatical_range', 0),
                pronunciation=results.get('pronunciation', 0),
                detailed_feedback=results.get('detailed_feedback', ''),
                transcript_text=json.dumps(context.get('conversation_history', [])),
                assessment_type="Conversational AI Assessment"
            )
            
            db.session.add(test_attempt)
            db.session.commit()
            
            logger.info(f"Saved conversational assessment for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving assessment results: {e}")
            db.session.rollback()

# Initialize the intelligent assessment service
intelligent_speaking_service = IntelligentSpeakingAssessment()