"""
IELTS Knowledge Base Integration with AWS Bedrock
This module provides RAG (Retrieval-Augmented Generation) capabilities
for enhanced IELTS assessment accuracy using official rubrics and criteria.
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

class IELTSKnowledgeBase:
    """RAG-enhanced IELTS assessment using AWS Bedrock Knowledge Bases"""
    
    def __init__(self):
        """Initialize IELTS Knowledge Base service"""
        try:
            self.bedrock_agent = boto3.client(
                'bedrock-agent-runtime',
                region_name='us-east-1',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            
            # Knowledge Base ID will be set after creation
            self.knowledge_base_id = None
            logger.info("IELTS Knowledge Base service initialized successfully")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found for Knowledge Base")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Base: {e}")
            raise

    def retrieve_assessment_criteria(self, assessment_type, skill_area):
        """
        Retrieve relevant IELTS assessment criteria from Knowledge Base
        
        Args:
            assessment_type (str): 'writing' or 'speaking'
            skill_area (str): Specific skill being assessed
            
        Returns:
            dict: Retrieved criteria and rubrics
        """
        try:
            if not self.knowledge_base_id:
                logger.warning("Knowledge Base not configured, using default criteria")
                return self._get_default_criteria(assessment_type, skill_area)
            
            query = f"IELTS {assessment_type} assessment criteria for {skill_area} band descriptors scoring rubric"
            
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5,
                        'overrideSearchType': 'HYBRID'
                    }
                }
            )
            
            # Process retrieved documents
            criteria = []
            for result in response.get('retrievalResults', []):
                criteria.append({
                    'content': result.get('content', {}).get('text', ''),
                    'source': result.get('location', {}).get('s3Location', {}).get('uri', ''),
                    'confidence': result.get('score', 0)
                })
            
            return {
                'success': True,
                'criteria': criteria,
                'assessment_type': assessment_type,
                'skill_area': skill_area
            }
            
        except Exception as e:
            logger.error(f"Knowledge Base retrieval error: {e}")
            return self._get_default_criteria(assessment_type, skill_area)

    def enhance_writing_assessment(self, essay_text, task_type, criteria_context=None):
        """
        Enhance writing assessment using RAG-retrieved criteria
        
        Args:
            essay_text (str): Student's essay
            task_type (str): 'task1' or 'task2'
            criteria_context (dict): Retrieved assessment criteria
            
        Returns:
            dict: Enhanced assessment with official criteria
        """
        try:
            # Retrieve relevant criteria if not provided
            if not criteria_context:
                criteria_context = self.retrieve_assessment_criteria('writing', task_type)
            
            # Build enhanced prompt with RAG context
            assessment_prompt = self._build_enhanced_writing_prompt(
                essay_text, task_type, criteria_context
            )
            
            # Use Nova Micro with RAG-enhanced context
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
                        "max_new_tokens": 3000,
                        "temperature": 0.2,
                        "top_p": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('content', [{}])[0].get('text', '')
            
            # Parse structured assessment
            scores = self._parse_writing_scores(assessment_text)
            
            return {
                'success': True,
                'overall_score': scores.get('overall_score', 0),
                'task_achievement': scores.get('task_achievement', 0),
                'coherence_cohesion': scores.get('coherence_cohesion', 0),
                'lexical_resource': scores.get('lexical_resource', 0),
                'grammatical_range': scores.get('grammatical_range', 0),
                'detailed_feedback': scores.get('feedback', ''),
                'assessment_type': 'RAG-Enhanced Nova Micro Writing Assessment',
                'criteria_sources': [c.get('source', '') for c in criteria_context.get('criteria', [])]
            }
            
        except Exception as e:
            logger.error(f"Enhanced writing assessment error: {e}")
            return {"success": False, "error": str(e)}

    def enhance_speaking_assessment(self, conversation_history, part_number, criteria_context=None):
        """
        Enhance speaking assessment using RAG-retrieved criteria
        
        Args:
            conversation_history (list): Complete conversation transcript
            part_number (int): IELTS speaking part (1, 2, or 3)
            criteria_context (dict): Retrieved assessment criteria
            
        Returns:
            dict: Enhanced assessment with official criteria
        """
        try:
            # Retrieve relevant criteria if not provided
            if not criteria_context:
                criteria_context = self.retrieve_assessment_criteria('speaking', f'part{part_number}')
            
            # Build enhanced prompt with RAG context
            assessment_prompt = self._build_enhanced_speaking_prompt(
                conversation_history, part_number, criteria_context
            )
            
            # Use Nova Micro with RAG-enhanced context for professional documentation
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
                        "max_new_tokens": 3000,
                        "temperature": 0.2,
                        "top_p": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            assessment_text = result.get('content', [{}])[0].get('text', '')
            
            # Parse structured assessment
            scores = self._parse_speaking_scores(assessment_text)
            
            return {
                'success': True,
                'overall_score': scores.get('overall_score', 0),
                'fluency_coherence': scores.get('fluency_coherence', 0),
                'lexical_resource': scores.get('lexical_resource', 0),
                'grammatical_range': scores.get('grammatical_range', 0),
                'pronunciation': scores.get('pronunciation', 0),
                'detailed_feedback': scores.get('feedback', ''),
                'conversation_transcript': conversation_history,
                'assessment_type': 'RAG-Enhanced Nova Sonic + Nova Micro Assessment',
                'criteria_sources': [c.get('source', '') for c in criteria_context.get('criteria', [])]
            }
            
        except Exception as e:
            logger.error(f"Enhanced speaking assessment error: {e}")
            return {"success": False, "error": str(e)}

    def _build_enhanced_writing_prompt(self, essay_text, task_type, criteria_context):
        """Build enhanced writing assessment prompt with RAG context"""
        
        criteria_text = "\n".join([
            f"OFFICIAL CRITERIA: {criteria['content']}"
            for criteria in criteria_context.get('criteria', [])[:3]  # Use top 3 most relevant
        ])
        
        return f"""
        You are an expert IELTS examiner assessing a {task_type.upper()} writing task.
        Use the official IELTS assessment criteria provided below for accurate evaluation.
        
        OFFICIAL IELTS ASSESSMENT CRITERIA:
        {criteria_text}
        
        STUDENT ESSAY TO ASSESS:
        {essay_text}
        
        Provide scores (0-9) for each criterion based on the official criteria above:
        
        OVERALL_SCORE: [score]
        TASK_ACHIEVEMENT: [score]
        COHERENCE_COHESION: [score]
        LEXICAL_RESOURCE: [score]
        GRAMMATICAL_RANGE: [score]
        
        DETAILED_FEEDBACK:
        [Provide specific feedback referencing the official criteria and band descriptors]
        
        Ensure your assessment strictly follows the official IELTS band descriptors provided above.
        """

    def _build_enhanced_speaking_prompt(self, conversation_history, part_number, criteria_context):
        """Build enhanced speaking assessment prompt with RAG context"""
        
        criteria_text = "\n".join([
            f"OFFICIAL CRITERIA: {criteria['content']}"
            for criteria in criteria_context.get('criteria', [])[:3]  # Use top 3 most relevant
        ])
        
        transcript = "\n".join([
            f"Examiner: {turn.get('examiner', '')}\nCandidate: {turn.get('candidate', '')}"
            for turn in conversation_history
        ])
        
        return f"""
        You are an expert IELTS examiner assessing Speaking Part {part_number}.
        Use the official IELTS assessment criteria provided below for accurate evaluation.
        
        OFFICIAL IELTS ASSESSMENT CRITERIA:
        {criteria_text}
        
        CONVERSATION TRANSCRIPT TO ASSESS:
        {transcript}
        
        Provide scores (0-9) for each criterion based on the official criteria above:
        
        OVERALL_SCORE: [score]
        FLUENCY_COHERENCE: [score]
        LEXICAL_RESOURCE: [score]
        GRAMMATICAL_RANGE: [score]
        PRONUNCIATION: [score]
        
        DETAILED_FEEDBACK:
        [Provide specific feedback referencing the official criteria and band descriptors]
        
        Ensure your assessment strictly follows the official IELTS band descriptors provided above.
        """

    def _parse_writing_scores(self, assessment_text):
        """Parse writing assessment scores"""
        scores = {}
        lines = assessment_text.split('\n')
        
        for line in lines:
            if 'OVERALL_SCORE:' in line:
                scores['overall_score'] = self._extract_score(line)
            elif 'TASK_ACHIEVEMENT:' in line:
                scores['task_achievement'] = self._extract_score(line)
            elif 'COHERENCE_COHESION:' in line:
                scores['coherence_cohesion'] = self._extract_score(line)
            elif 'LEXICAL_RESOURCE:' in line:
                scores['lexical_resource'] = self._extract_score(line)
            elif 'GRAMMATICAL_RANGE:' in line:
                scores['grammatical_range'] = self._extract_score(line)
            elif 'DETAILED_FEEDBACK:' in line:
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                scores['feedback'] = assessment_text[feedback_start + len('DETAILED_FEEDBACK:'):].strip()
                break
        
        return scores

    def _parse_speaking_scores(self, assessment_text):
        """Parse speaking assessment scores"""
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
                feedback_start = assessment_text.find('DETAILED_FEEDBACK:')
                scores['feedback'] = assessment_text[feedback_start + len('DETAILED_FEEDBACK:'):].strip()
                break
        
        return scores

    def _extract_score(self, line):
        """Extract numeric score from a line"""
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', line)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 0), 9)  # Ensure score is between 0-9
        except:
            pass
        return 0

    def _get_default_criteria(self, assessment_type, skill_area):
        """Provide default IELTS criteria when Knowledge Base is not available"""
        default_criteria = {
            'writing': {
                'task1': [
                    {
                        'content': 'Task Achievement: Address all parts of the task, present clear overview, highlight key features accurately',
                        'source': 'default_ielts_criteria',
                        'confidence': 0.8
                    }
                ],
                'task2': [
                    {
                        'content': 'Task Response: Address all parts of the task, present relevant ideas with clear position throughout',
                        'source': 'default_ielts_criteria', 
                        'confidence': 0.8
                    }
                ]
            },
            'speaking': {
                'part1': [
                    {
                        'content': 'Fluency and Coherence: Speak at length without noticeable effort, use range of connectives appropriately',
                        'source': 'default_ielts_criteria',
                        'confidence': 0.8
                    }
                ]
            }
        }
        
        criteria = default_criteria.get(assessment_type, {}).get(skill_area, [])
        
        return {
            'success': True,
            'criteria': criteria,
            'assessment_type': assessment_type,
            'skill_area': skill_area,
            'using_defaults': True
        }

# Initialize the service
try:
    ielts_knowledge_base = IELTSKnowledgeBase()
    logger.info("IELTS Knowledge Base service ready for RAG-enhanced assessments")
except Exception as e:
    logger.error(f"Failed to initialize IELTS Knowledge Base service: {e}")
    ielts_knowledge_base = None