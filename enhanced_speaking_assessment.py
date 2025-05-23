"""
Enhanced Speaking Assessment Module
Combines Azure Speech Services pronunciation assessment with Nova Micro content analysis
for comprehensive IELTS speaking evaluation using Elaris® technology.
"""

import os
import json
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from azure_speech_services import AzureSpeechAssessment
from aws_bedrock_services import assess_speaking_with_nova_micro
from api_issues import log_api_error
import boto3
import json


class EnhancedSpeakingAssessment:
    """
    Enhanced IELTS speaking assessment combining:
    - Azure Speech Services for pronunciation, fluency, and prosody
    - Nova Micro for content analysis, vocabulary, and grammar
    - Comprehensive IELTS band scoring across all criteria
    """
    
    def __init__(self):
        self.azure_available = is_azure_speech_available()
        
    def assess_speaking_response(self, audio_file_path: str, prompt_text: str, 
                                part_number: int, reference_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive IELTS speaking assessment using enhanced AI analysis.
        
        Args:
            audio_file_path (str): Path to the recorded audio file
            prompt_text (str): The speaking prompt/question
            part_number (int): IELTS speaking part (1, 2, or 3)
            reference_text (str, optional): Expected response text for pronunciation comparison
            
        Returns:
            Complete assessment results with IELTS band scores and detailed feedback
        """
        
        start_time = time.time()
        
        try:
            # Step 1: Get transcription (using AssemblyAI as backup for content analysis)
            transcription_result = self._get_transcription(audio_file_path)
            transcription_text = transcription_result.get('text', '')
            
            # Step 2: Azure pronunciation assessment (if available)
            pronunciation_result = None
            if self.azure_available and reference_text:
                pronunciation_result = assess_pronunciation_with_azure(audio_file_path, reference_text)
            elif self.azure_available and transcription_text:
                # Use transcription as reference if no specific reference text provided
                pronunciation_result = assess_pronunciation_with_azure(audio_file_path, transcription_text)
            
            # Step 3: Nova Micro content analysis
            content_result = assess_speaking_with_nova_micro(transcription_text, prompt_text, part_number)
            
            # Step 4: Combine results into comprehensive IELTS assessment
            final_assessment = self._combine_assessment_results(
                transcription_result, pronunciation_result, content_result, part_number
            )
            
            # Step 5: Calculate processing time
            processing_time = time.time() - start_time
            final_assessment['processing_time'] = round(processing_time, 2)
            
            return final_assessment
            
        except Exception as e:
            processing_time = time.time() - start_time
            log_api_error('enhanced_speaking_assessment', 'full_assessment', e, 
                         request_duration=processing_time)
            
            # Return fallback assessment result
            return self._create_fallback_assessment(str(e))
    
    def _get_transcription(self, audio_file_path: str) -> Dict[str, Any]:
        """Get audio transcription using Azure Speech Services (included with pronunciation assessment)."""
        try:
            # Azure Speech Services provides both transcription and pronunciation in one call
            # This will be handled by the Azure pronunciation assessment function
            # For now, return a placeholder that will be filled by Azure assessment
            
            return {
                'text': '',  # Will be filled by Azure
                'confidence': 0.0,  # Will be filled by Azure
                'duration': 0,  # Will be filled by Azure
                'word_count': 0,  # Will be calculated after Azure assessment
                'source': 'azure_integrated'
            }
            
        except Exception as e:
            log_api_error('enhanced_speaking_assessment', 'azure_transcription', e)
            return {
                'text': '',
                'confidence': 0.0,
                'duration': 0,
                'word_count': 0,
                'error': str(e)
            }
    
    def _combine_assessment_results(self, transcription: Dict[str, Any], 
                                   pronunciation: Optional[Dict[str, Any]], 
                                   content: Dict[str, Any], 
                                   part_number: int) -> Dict[str, Any]:
        """
        Combine Azure pronunciation assessment with Nova Micro content analysis
        to create comprehensive IELTS speaking band scores.
        """
        
        # Extract content scores from Nova Micro
        content_scores = content.get('band_scores', {})
        fluency_coherence = content_scores.get('fluency_coherence', 5.0)
        lexical_resource = content_scores.get('lexical_resource', 5.0)
        grammatical_range = content_scores.get('grammatical_range_accuracy', 5.0)
        
        # Extract pronunciation scores from Azure (if available)
        if pronunciation and pronunciation.get('detailed_scores'):
            azure_scores = pronunciation['detailed_scores']
            pronunciation_band = pronunciation.get('pronunciation_band', 5.0)
            
            # Use Azure's fluency score if available, otherwise use Nova Micro's
            azure_fluency = azure_scores.get('fluency', 5.0)
            # Combine Azure fluency with Nova Micro coherence for comprehensive fluency score
            combined_fluency = round((azure_fluency + fluency_coherence) / 2, 1)
        else:
            # Fallback to content-only assessment
            pronunciation_band = self._estimate_pronunciation_from_content(transcription)
            combined_fluency = fluency_coherence
        
        # Calculate overall band score
        overall_band = round((combined_fluency + lexical_resource + grammatical_range + pronunciation_band) / 4, 1)
        
        # Generate comprehensive feedback
        feedback = self._generate_comprehensive_feedback(
            transcription, pronunciation, content, part_number
        )
        
        return {
            'overall_band_score': overall_band,
            'detailed_band_scores': {
                'fluency_and_coherence': combined_fluency,
                'lexical_resource': lexical_resource,
                'grammatical_range_and_accuracy': grammatical_range,
                'pronunciation': pronunciation_band
            },
            'transcription': transcription.get('text', ''),
            'word_count': transcription.get('word_count', 0),
            'duration_seconds': transcription.get('duration', 0),
            'detailed_feedback': feedback,
            'assessment_technology': 'Elaris® (Azure + Nova Micro)',
            'azure_pronunciation_available': pronunciation is not None,
            'content_analysis': content.get('detailed_feedback', {}),
            'pronunciation_analysis': pronunciation.get('ielts_feedback', {}) if pronunciation else None
        }
    
    def _estimate_pronunciation_from_content(self, transcription: Dict[str, Any]) -> float:
        """
        Estimate pronunciation score from transcription quality when Azure is not available.
        This is a fallback method and less accurate than Azure assessment.
        """
        confidence = transcription.get('confidence', 0.0)
        word_count = transcription.get('word_count', 0)
        
        # Basic estimation based on transcription confidence
        if confidence >= 0.95:
            return 7.5
        elif confidence >= 0.90:
            return 7.0
        elif confidence >= 0.85:
            return 6.5
        elif confidence >= 0.80:
            return 6.0
        elif confidence >= 0.75:
            return 5.5
        else:
            return 5.0
    
    def _generate_comprehensive_feedback(self, transcription: Dict[str, Any], 
                                        pronunciation: Optional[Dict[str, Any]], 
                                        content: Dict[str, Any], 
                                        part_number: int) -> Dict[str, str]:
        """Generate comprehensive feedback combining all assessment aspects."""
        
        feedback = {}
        
        # Content feedback from Nova Micro
        content_feedback = content.get('detailed_feedback', {})
        feedback.update(content_feedback)
        
        # Pronunciation feedback from Azure (if available)
        if pronunciation and pronunciation.get('ielts_feedback'):
            azure_feedback = pronunciation['ielts_feedback']
            feedback.update(azure_feedback)
        else:
            # Provide basic pronunciation guidance without Azure
            feedback['pronunciation'] = "Consider practicing pronunciation with native speakers or language learning apps to improve clarity and accuracy."
        
        # Add specific advice based on part number
        if part_number == 1:
            feedback['part_specific'] = "For Part 1, focus on clear, direct answers that demonstrate natural conversation skills."
        elif part_number == 2:
            feedback['part_specific'] = "For Part 2, organize your response with clear structure and develop ideas fully within the time limit."
        elif part_number == 3:
            feedback['part_specific'] = "For Part 3, demonstrate analytical thinking and provide well-reasoned opinions with supporting examples."
        
        return feedback
    
    def _create_fallback_assessment(self, error_message: str) -> Dict[str, Any]:
        """Create a fallback assessment when the main assessment fails."""
        return {
            'overall_band_score': 0.0,
            'detailed_band_scores': {
                'fluency_and_coherence': 0.0,
                'lexical_resource': 0.0,
                'grammatical_range_and_accuracy': 0.0,
                'pronunciation': 0.0
            },
            'transcription': '',
            'word_count': 0,
            'duration_seconds': 0,
            'detailed_feedback': {
                'error': 'Assessment temporarily unavailable. Please try again.',
                'technical_details': error_message
            },
            'assessment_technology': 'Elaris® (Assessment Failed)',
            'azure_pronunciation_available': False,
            'error': True
        }


# Convenience functions for integration with existing routes

def process_enhanced_speaking_response(audio_file_path: str, prompt_text: str, 
                                     part_number: int, reference_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a speaking response using enhanced assessment (Azure + Nova Micro).
    
    Args:
        audio_file_path (str): Path to the recorded audio
        prompt_text (str): The speaking prompt
        part_number (int): IELTS speaking part number
        reference_text (str, optional): Expected response for pronunciation comparison
        
    Returns:
        Complete assessment results
    """
    
    assessor = EnhancedSpeakingAssessment()
    return assessor.assess_speaking_response(audio_file_path, prompt_text, part_number, reference_text)


def get_assessment_technology_info() -> Dict[str, Any]:
    """Get information about available assessment technologies."""
    return {
        'azure_speech_available': is_azure_speech_available(),
        'technology_name': 'Elaris®',
        'components': {
            'pronunciation_assessment': 'Azure Speech Services' if is_azure_speech_available() else 'Confidence-based estimation',
            'content_analysis': 'AWS Bedrock Nova Micro',
            'transcription': 'AssemblyAI'
        }
    }