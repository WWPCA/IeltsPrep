"""
Azure Speech Services Integration for IELTS Speaking Assessment
This module provides advanced pronunciation assessment capabilities for Elaris® speaking evaluations.
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional
from api_issues import log_api_error

class AzureSpeechAssessment:
    """
    Azure Speech Services integration for comprehensive IELTS speaking assessment.
    Provides pronunciation scoring, fluency analysis, and prosody evaluation.
    """
    
    def __init__(self):
        self.subscription_key = os.environ.get('AZURE_SPEECH_KEY')
        self.region = os.environ.get('AZURE_SPEECH_REGION', 'eastus')
        self.base_url = f"https://{self.region}.api.cognitive.microsoft.com/speechtotext/v3.1"
        
    def is_configured(self) -> bool:
        """Check if Azure Speech Services is properly configured."""
        return bool(self.subscription_key and self.region)
    
    def assess_pronunciation(self, audio_file_path: str, reference_text: str, 
                           assessment_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Assess pronunciation using Azure Speech Services with detailed IELTS criteria.
        
        Args:
            audio_file_path (str): Path to the audio file
            reference_text (str): Expected text for pronunciation comparison
            assessment_type (str): Type of assessment ('comprehensive', 'pronunciation_only')
            
        Returns:
            Dict containing pronunciation scores and detailed feedback
        """
        
        if not self.is_configured():
            raise ValueError("Azure Speech Services not configured. Please provide AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.")
        
        start_time = time.time()
        
        try:
            # Prepare assessment configuration for IELTS speaking
            assessment_config = {
                "pronunciation": {
                    "gradingSystem": "HundredMark",
                    "granularity": "Phoneme"
                },
                "fluency": {
                    "gradingSystem": "HundredMark"
                },
                "completeness": {
                    "gradingSystem": "HundredMark"
                },
                "prosody": {
                    "gradingSystem": "HundredMark"
                }
            }
            
            # Prepare the request
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Content-Type': 'audio/wav',
                'Accept': 'application/json'
            }
            
            # Add pronunciation assessment parameters
            params = {
                'language': 'en-US',
                'format': 'detailed',
                'profanityAction': 'Masked',
                'pronunciationAssessmentReferenceText': reference_text,
                'pronunciationAssessmentGradingSystem': 'HundredMark',
                'pronunciationAssessmentGranularity': 'Phoneme',
                'pronunciationAssessmentEnableMiscue': 'True',
                'pronunciationAssessmentEnableProsodyAssessment': 'True'
            }
            
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Make the API request
            url = f"{self.base_url}/speechtotext/recognition/conversation/cognitiveservices/v1"
            response = requests.post(url, headers=headers, params=params, data=audio_data)
            
            request_duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return self._process_assessment_result(result)
            else:
                error_msg = f"Azure Speech API error: {response.status_code} - {response.text}"
                log_api_error('azure_speech', 'pronunciation_assessment', 
                            Exception(error_msg), request_duration=request_duration)
                raise Exception(error_msg)
                
        except Exception as e:
            request_duration = time.time() - start_time
            log_api_error('azure_speech', 'pronunciation_assessment', e, 
                        request_duration=request_duration)
            raise
    
    def _process_assessment_result(self, azure_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Azure assessment results into IELTS-compatible scoring.
        
        Args:
            azure_result: Raw result from Azure Speech Services
            
        Returns:
            Processed assessment with IELTS band scores and detailed feedback
        """
        
        try:
            # Extract pronunciation assessment from Azure result
            pronunciation_assessment = azure_result.get('NBest', [{}])[0].get('PronunciationAssessment', {})
            
            # Convert Azure scores (0-100) to IELTS band scores (1-9)
            pronunciation_score = self._convert_to_ielts_band(pronunciation_assessment.get('PronScore', 0))
            fluency_score = self._convert_to_ielts_band(pronunciation_assessment.get('FluencyScore', 0))
            completeness_score = self._convert_to_ielts_band(pronunciation_assessment.get('CompletenessScore', 0))
            prosody_score = self._convert_to_ielts_band(pronunciation_assessment.get('ProsodyScore', 0))
            
            # Calculate overall pronunciation band
            overall_pronunciation = round((pronunciation_score + fluency_score + prosody_score) / 3, 1)
            
            # Extract detailed word-level feedback
            word_details = self._extract_word_level_feedback(azure_result)
            
            # Generate IELTS-specific feedback
            feedback = self._generate_ielts_feedback(
                pronunciation_score, fluency_score, completeness_score, prosody_score, word_details
            )
            
            return {
                'pronunciation_band': overall_pronunciation,
                'detailed_scores': {
                    'pronunciation_accuracy': pronunciation_score,
                    'fluency': fluency_score,
                    'completeness': completeness_score,
                    'prosody': prosody_score
                },
                'word_level_feedback': word_details,
                'ielts_feedback': feedback,
                'raw_azure_scores': pronunciation_assessment
            }
            
        except Exception as e:
            log_api_error('azure_speech', 'result_processing', e)
            raise Exception(f"Failed to process Azure assessment result: {str(e)}")
    
    def _convert_to_ielts_band(self, azure_score: float) -> float:
        """Convert Azure 0-100 score to IELTS 1-9 band score."""
        if azure_score >= 90:
            return 9.0
        elif azure_score >= 80:
            return 8.0 + (azure_score - 80) / 10 * 1.0
        elif azure_score >= 70:
            return 7.0 + (azure_score - 70) / 10 * 1.0
        elif azure_score >= 60:
            return 6.0 + (azure_score - 60) / 10 * 1.0
        elif azure_score >= 50:
            return 5.0 + (azure_score - 50) / 10 * 1.0
        elif azure_score >= 40:
            return 4.0 + (azure_score - 40) / 10 * 1.0
        elif azure_score >= 30:
            return 3.0 + (azure_score - 30) / 10 * 1.0
        elif azure_score >= 20:
            return 2.0 + (azure_score - 20) / 10 * 1.0
        else:
            return 1.0 + azure_score / 20 * 1.0
    
    def _extract_word_level_feedback(self, azure_result: Dict[str, Any]) -> list:
        """Extract detailed word-level pronunciation feedback."""
        word_feedback = []
        
        try:
            words = azure_result.get('NBest', [{}])[0].get('Words', [])
            
            for word in words:
                word_assessment = word.get('PronunciationAssessment', {})
                phonemes = word.get('Phonemes', [])
                
                phoneme_details = []
                for phoneme in phonemes:
                    phoneme_assessment = phoneme.get('PronunciationAssessment', {})
                    phoneme_details.append({
                        'phoneme': phoneme.get('Phoneme', ''),
                        'accuracy_score': phoneme_assessment.get('AccuracyScore', 0)
                    })
                
                word_feedback.append({
                    'word': word.get('Word', ''),
                    'accuracy_score': word_assessment.get('AccuracyScore', 0),
                    'error_type': word_assessment.get('ErrorType', 'None'),
                    'phonemes': phoneme_details
                })
                
        except Exception as e:
            log_api_error('azure_speech', 'word_feedback_extraction', e)
        
        return word_feedback
    
    def _generate_ielts_feedback(self, pronunciation: float, fluency: float, 
                                completeness: float, prosody: float, word_details: list) -> Dict[str, str]:
        """Generate IELTS-specific feedback based on assessment scores."""
        
        feedback = {
            'pronunciation': self._get_pronunciation_feedback(pronunciation, word_details),
            'fluency': self._get_fluency_feedback(fluency),
            'prosody': self._get_prosody_feedback(prosody),
            'overall': self._get_overall_feedback(pronunciation, fluency, prosody)
        }
        
        return feedback
    
    def _get_pronunciation_feedback(self, score: float, word_details: list) -> str:
        """Generate pronunciation-specific feedback."""
        if score >= 8.0:
            return "Excellent pronunciation with clear articulation and minimal errors. Most sounds are produced accurately."
        elif score >= 7.0:
            return "Good pronunciation with generally clear articulation. Some minor pronunciation errors that do not impede understanding."
        elif score >= 6.0:
            return "Generally clear pronunciation with some noticeable errors. Most words are pronounced clearly enough to be understood."
        elif score >= 5.0:
            return "Fair pronunciation with several errors that occasionally affect clarity. Some sounds may be mispronounced."
        else:
            return "Pronunciation needs improvement. Multiple errors affect clarity and understanding. Focus on individual sound production."
    
    def _get_fluency_feedback(self, score: float) -> str:
        """Generate fluency-specific feedback."""
        if score >= 8.0:
            return "Excellent fluency with natural rhythm and appropriate pacing. Speech flows smoothly with minimal hesitation."
        elif score >= 7.0:
            return "Good fluency with generally natural speech rhythm. Some minor hesitations that don't affect overall flow."
        elif score >= 6.0:
            return "Adequate fluency with some unnatural pauses. Speech is generally continuous but may lack natural rhythm."
        elif score >= 5.0:
            return "Fair fluency with noticeable hesitations and pauses. Speech may sound choppy at times."
        else:
            return "Fluency needs improvement. Frequent pauses and hesitations affect the natural flow of speech."
    
    def _get_prosody_feedback(self, score: float) -> str:
        """Generate prosody-specific feedback."""
        if score >= 8.0:
            return "Excellent use of stress, intonation, and rhythm. Speech sounds natural and expressive."
        elif score >= 7.0:
            return "Good prosody with appropriate stress patterns and intonation. Generally natural-sounding speech."
        elif score >= 6.0:
            return "Adequate prosody with some appropriate stress and intonation patterns. May sound slightly monotonous."
        elif score >= 5.0:
            return "Fair prosody with limited variation in stress and intonation. Speech may sound flat or unnatural."
        else:
            return "Prosody needs improvement. Limited use of stress, intonation, and rhythm patterns."
    
    def _get_overall_feedback(self, pronunciation: float, fluency: float, prosody: float) -> str:
        """Generate overall pronunciation feedback."""
        average = (pronunciation + fluency + prosody) / 3
        
        if average >= 8.0:
            return "Outstanding pronunciation skills. You demonstrate excellent control of English sounds, rhythm, and intonation."
        elif average >= 7.0:
            return "Strong pronunciation skills. Your speech is clear and natural with only minor areas for improvement."
        elif average >= 6.0:
            return "Good pronunciation foundation. Continue practicing to improve clarity and natural speech patterns."
        elif average >= 5.0:
            return "Developing pronunciation skills. Focus on individual sound accuracy and speech rhythm."
        else:
            return "Pronunciation requires significant practice. Work on basic sound production and speech clarity."


# Utility functions for integration with existing speaking assessment routes

def assess_pronunciation_with_azure(audio_file_path: str, reference_text: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to assess pronunciation using Azure Speech Services.
    
    Args:
        audio_file_path (str): Path to the audio file
        reference_text (str): Expected text for pronunciation comparison
        
    Returns:
        Assessment results or None if Azure is not configured
    """
    
    azure_service = AzureSpeechAssessment()
    
    if not azure_service.is_configured():
        return None
    
    try:
        return azure_service.assess_pronunciation(audio_file_path, reference_text)
    except Exception as e:
        print(f"Azure pronunciation assessment failed: {str(e)}")
        return None


def is_azure_speech_available() -> bool:
    """Check if Azure Speech Services is properly configured and available."""
    azure_service = AzureSpeechAssessment()
    return azure_service.is_configured()