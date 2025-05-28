"""
Populate AWS Bedrock Knowledge Base with IELTS Questions and Assessment Criteria
This module extracts questions from your database and formats them for RAG enhancement.
"""

import os
import json
import logging
from datetime import datetime
from app import app, db
from models import SpeakingPrompt, Assessment
from ielts_official_rubrics import get_all_criteria

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBasePopulator:
    """Populate Knowledge Base with authentic IELTS content"""
    
    def __init__(self):
        """Initialize the Knowledge Base populator"""
        self.knowledge_base_documents = []
        logger.info("Knowledge Base Populator initialized")

    def extract_speaking_questions(self):
        """Extract speaking prompts from database for Knowledge Base"""
        try:
            with app.app_context():
                speaking_prompts = SpeakingPrompt.query.all()
                
                speaking_documents = []
                
                # Group prompts by part for better context
                for part_num in [1, 2, 3]:
                    part_prompts = [p for p in speaking_prompts if p.part == part_num]
                    
                    if part_prompts:
                        # Create comprehensive document for each speaking part
                        part_content = f"""
                        IELTS Speaking Part {part_num} Questions and Prompts
                        
                        Official IELTS Speaking Part {part_num} Assessment Context:
                        {self._get_speaking_part_context(part_num)}
                        
                        Authentic Speaking Questions for Part {part_num}:
                        """
                        
                        for i, prompt in enumerate(part_prompts, 1):
                            part_content += f"\n{i}. {prompt.prompt_text}"
                        
                        part_content += f"""
                        
                        Assessment Guidelines for Part {part_num}:
                        - Focus on natural conversation flow
                        - Evaluate fluency, coherence, lexical resource, grammar, pronunciation
                        - Questions should elicit appropriate language level for IELTS assessment
                        - Responses should be evaluated against official IELTS band descriptors
                        """
                        
                        speaking_documents.append({
                            'title': f'IELTS Speaking Part {part_num} Questions',
                            'content': part_content,
                            'type': 'speaking_questions',
                            'part': part_num,
                            'document_id': f'speaking_part_{part_num}_questions'
                        })
                
                logger.info(f"Extracted {len(speaking_documents)} speaking question documents")
                return speaking_documents
                
        except Exception as e:
            logger.error(f"Error extracting speaking questions: {e}")
            return []

    def extract_writing_questions(self):
        """Extract writing assessments from database for Knowledge Base"""
        try:
            with app.app_context():
                writing_assessments = Assessment.query.filter(
                    Assessment.assessment_type.like('%writing%')
                ).all()
                
                writing_documents = []
                
                # Group by assessment type
                academic_writing = [a for a in writing_assessments if 'academic' in a.assessment_type]
                general_writing = [a for a in writing_assessments if 'general' in a.assessment_type]
                
                # Process Academic Writing
                if academic_writing:
                    academic_content = """
                    IELTS Academic Writing Questions and Tasks
                    
                    Official IELTS Academic Writing Assessment Context:
                    Task 1: Describe visual information (graphs, charts, tables, diagrams)
                    Task 2: Present and justify opinions, discuss problems, compare evidence
                    
                    Authentic Academic Writing Questions:
                    """
                    
                    for i, assessment in enumerate(academic_writing, 1):
                        academic_content += f"""
                        
                        Assessment {i}: {assessment.title}
                        Description: {assessment.description or 'Academic writing task'}
                        Questions: {json.dumps(assessment.questions) if assessment.questions else 'Standard academic format'}
                        Assessment Criteria: {json.dumps(assessment.criteria) if assessment.criteria else 'Official IELTS criteria'}
                        """
                    
                    academic_content += """
                    
                    Academic Writing Assessment Guidelines:
                    - Task 1: Focus on accurate data description, clear overview, key features
                    - Task 2: Focus on task response, coherence, lexical resource, grammar
                    - Evaluate against official IELTS band descriptors
                    - Provide specific feedback on each assessment criterion
                    """
                    
                    writing_documents.append({
                        'title': 'IELTS Academic Writing Questions',
                        'content': academic_content,
                        'type': 'writing_questions',
                        'category': 'academic',
                        'document_id': 'academic_writing_questions'
                    })
                
                # Process General Training Writing
                if general_writing:
                    general_content = """
                    IELTS General Training Writing Questions and Tasks
                    
                    Official IELTS General Training Writing Assessment Context:
                    Task 1: Write letters (personal, semi-formal, formal)
                    Task 2: Write essays responding to arguments, problems, opinions
                    
                    Authentic General Training Writing Questions:
                    """
                    
                    for i, assessment in enumerate(general_writing, 1):
                        general_content += f"""
                        
                        Assessment {i}: {assessment.title}
                        Description: {assessment.description or 'General training writing task'}
                        Questions: {json.dumps(assessment.questions) if assessment.questions else 'Standard general format'}
                        Assessment Criteria: {json.dumps(assessment.criteria) if assessment.criteria else 'Official IELTS criteria'}
                        """
                    
                    general_content += """
                    
                    General Training Writing Assessment Guidelines:
                    - Task 1: Focus on appropriate tone, purpose achievement, organization
                    - Task 2: Focus on task response, coherence, lexical resource, grammar  
                    - Evaluate against official IELTS band descriptors
                    - Consider audience and register appropriateness
                    """
                    
                    writing_documents.append({
                        'title': 'IELTS General Training Writing Questions',
                        'content': general_content,
                        'type': 'writing_questions',
                        'category': 'general',
                        'document_id': 'general_writing_questions'
                    })
                
                logger.info(f"Extracted {len(writing_documents)} writing question documents")
                return writing_documents
                
        except Exception as e:
            logger.error(f"Error extracting writing questions: {e}")
            return []

    def create_assessment_criteria_documents(self):
        """Create comprehensive assessment criteria documents"""
        try:
            # Get all official IELTS criteria
            all_criteria = get_all_criteria()
            
            criteria_documents = []
            
            # Writing Criteria Document
            writing_criteria_content = f"""
            Official IELTS Writing Assessment Criteria and Band Descriptors
            
            Complete Official IELTS Writing Assessment Framework:
            
            {all_criteria['writing']['task_2_rubric']}
            
            {all_criteria['writing']['task_1_rubric']}
            
            Assessment Application Guidelines:
            - Use precise band descriptors for scoring
            - Provide specific examples from student responses
            - Reference exact criteria when giving feedback
            - Maintain consistency across all assessments
            - Consider task-specific requirements
            """
            
            criteria_documents.append({
                'title': 'Official IELTS Writing Assessment Criteria',
                'content': writing_criteria_content,
                'type': 'assessment_criteria',
                'skill': 'writing',
                'document_id': 'official_writing_criteria'
            })
            
            # Speaking Criteria Document
            speaking_criteria_content = f"""
            Official IELTS Speaking Assessment Criteria and Band Descriptors
            
            Complete Official IELTS Speaking Assessment Framework:
            
            {all_criteria['speaking']['speaking_rubric']}
            
            Assessment Application Guidelines:
            - Evaluate all four criteria equally (25% each)
            - Consider part-specific expectations
            - Provide evidence-based scoring justification
            - Reference exact band descriptors in feedback
            - Maintain examiner objectivity and consistency
            """
            
            criteria_documents.append({
                'title': 'Official IELTS Speaking Assessment Criteria',
                'content': speaking_criteria_content,
                'type': 'assessment_criteria',
                'skill': 'speaking',
                'document_id': 'official_speaking_criteria'
            })
            
            logger.info(f"Created {len(criteria_documents)} assessment criteria documents")
            return criteria_documents
            
        except Exception as e:
            logger.error(f"Error creating criteria documents: {e}")
            return []

    def generate_comprehensive_knowledge_base(self):
        """Generate complete Knowledge Base content"""
        try:
            logger.info("Generating comprehensive Knowledge Base content...")
            
            # Extract all content
            speaking_docs = self.extract_speaking_questions()
            writing_docs = self.extract_writing_questions()
            criteria_docs = self.create_assessment_criteria_documents()
            
            # Combine all documents
            all_documents = speaking_docs + writing_docs + criteria_docs
            
            # Create master document with cross-references
            master_content = f"""
            IELTS AI Prep Platform Knowledge Base
            Generated: {datetime.now().isoformat()}
            
            This Knowledge Base contains authentic IELTS assessment content for RAG-enhanced evaluations:
            
            CONTENTS:
            1. Official IELTS Assessment Criteria and Band Descriptors
            2. Authentic Speaking Questions (Parts 1, 2, 3)
            3. Authentic Writing Questions (Academic and General Training)
            4. Assessment Guidelines and Best Practices
            
            PURPOSE:
            Enable Nova Sonic and Nova Micro models to provide accurate, 
            authentic IELTS assessments using official criteria and real questions.
            
            USAGE:
            - Reference specific band descriptors for scoring
            - Use authentic questions for context-aware assessment
            - Apply official IELTS standards consistently
            - Provide evidence-based feedback
            
            Total Documents: {len(all_documents)}
            Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            all_documents.insert(0, {
                'title': 'IELTS Knowledge Base Master Index',
                'content': master_content,
                'type': 'master_index',
                'document_id': 'knowledge_base_master'
            })
            
            self.knowledge_base_documents = all_documents
            
            logger.info(f"Generated comprehensive Knowledge Base with {len(all_documents)} documents")
            return all_documents
            
        except Exception as e:
            logger.error(f"Error generating Knowledge Base: {e}")
            return []

    def export_for_aws_upload(self, output_dir="knowledge_base_export"):
        """Export documents for AWS Bedrock Knowledge Base upload"""
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            documents = self.generate_comprehensive_knowledge_base()
            
            # Export each document as a separate file
            exported_files = []
            
            for doc in documents:
                filename = f"{doc['document_id']}.txt"
                filepath = os.path.join(output_dir, filename)
                
                # Create formatted content for AWS
                formatted_content = f"""Title: {doc['title']}
Type: {doc['type']}
Document ID: {doc['document_id']}

{doc['content']}
"""
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                
                exported_files.append(filepath)
            
            # Create manifest file
            manifest = {
                'knowledge_base_name': 'IELTS AI Prep Knowledge Base',
                'created': datetime.now().isoformat(),
                'total_documents': len(documents),
                'files': exported_files,
                'document_types': list(set(doc['type'] for doc in documents))
            }
            
            manifest_path = os.path.join(output_dir, 'manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Exported {len(exported_files)} documents to {output_dir}")
            logger.info(f"Manifest created at {manifest_path}")
            
            return {
                'success': True,
                'export_directory': output_dir,
                'files_exported': len(exported_files),
                'manifest_path': manifest_path
            }
            
        except Exception as e:
            logger.error(f"Error exporting Knowledge Base: {e}")
            return {'success': False, 'error': str(e)}

    def _get_speaking_part_context(self, part_number):
        """Get context description for speaking parts"""
        contexts = {
            1: "Introduction and Interview (4-5 minutes): General questions about familiar topics like home, family, work, studies, and interests.",
            2: "Individual Long Turn (3-4 minutes): Candidate talks about a particular topic for 1-2 minutes after 1 minute preparation.",
            3: "Two-way Discussion (4-5 minutes): Abstract questions connected to Part 2 topic, discussing more complex issues and ideas."
        }
        return contexts.get(part_number, "General speaking assessment")

# Initialize the populator
if __name__ == "__main__":
    populator = KnowledgeBasePopulator()
    result = populator.export_for_aws_upload()
    
    if result['success']:
        print(f"✓ Knowledge Base content exported successfully!")
        print(f"✓ {result['files_exported']} documents created")
        print(f"✓ Files saved to: {result['export_directory']}")
        print(f"✓ Upload these files to AWS Bedrock Knowledge Base for RAG enhancement")
    else:
        print(f"✗ Export failed: {result['error']}")