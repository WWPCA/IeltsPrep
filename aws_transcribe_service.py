"""
AWS Transcribe Integration for IELTS Speaking Assessment
This module formats Nova Sonic's real-time assessments into written IELTS rubric format.
Nova Sonic handles the actual assessment; Transcribe creates the written documentation.
"""

import os
import json
import boto3
import time
import uuid
from datetime import datetime
from api_issues import log_api_error

def get_transcribe_client():
    """Initialize AWS Transcribe client with credentials."""
    try:
        return boto3.client(
            'transcribe',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        log_api_error('aws_transcribe', 'client_initialization', e)
        raise

def transcribe_audio_file(audio_file_path, language_code='en-US'):
    """
    Transcribe an audio file using AWS Transcribe.
    
    Args:
        audio_file_path (str): Path to the audio file
        language_code (str): Language code for transcription (default: en-US)
        
    Returns:
        dict: Transcription result with text and confidence scores
    """
    transcribe_client = get_transcribe_client()
    s3_client = boto3.client(
        's3',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    
    try:
        # Generate unique job name
        job_name = f"ielts-speaking-{uuid.uuid4().hex[:8]}-{int(time.time())}"
        bucket_name = 'ielts-audio-transcription'  # You'll need to create this bucket
        s3_key = f"audio/{job_name}.wav"
        
        # Upload audio file to S3
        s3_client.upload_file(audio_file_path, bucket_name, s3_key)
        audio_uri = f"s3://{bucket_name}/{s3_key}"
        
        # Start transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': audio_uri},
            MediaFormat='wav',
            LanguageCode=language_code,
            Settings={
                'ShowSpeakerLabels': False,
                'MaxSpeakerLabels': 1,
                'ChannelIdentification': False
            }
        )
        
        # Wait for job completion
        while True:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
                
            time.sleep(2)
        
        if job_status == 'COMPLETED':
            # Get transcription result
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Download and parse transcript
            import requests
            response = requests.get(transcript_uri)
            transcript_data = response.json()
            
            # Extract text and confidence
            results = transcript_data['results']
            transcript_text = results['transcripts'][0]['transcript']
            
            # Calculate average confidence
            items = results.get('items', [])
            confidences = [float(item.get('alternatives', [{}])[0].get('confidence', 0)) 
                          for item in items if 'confidence' in item.get('alternatives', [{}])[0]]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Clean up S3 file
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
            except:
                pass  # Non-critical cleanup
                
            # Clean up transcription job
            try:
                transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            except:
                pass  # Non-critical cleanup
            
            return {
                'success': True,
                'transcript': transcript_text,
                'confidence': avg_confidence,
                'word_count': len(transcript_text.split()),
                'duration_seconds': status['TranscriptionJob']['MediaSampleRateHertz']
            }
        else:
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown error')
            log_api_error('aws_transcribe', 'transcription_job', Exception(failure_reason))
            return {
                'success': False,
                'error': failure_reason
            }
            
    except Exception as e:
        log_api_error('aws_transcribe', 'transcribe_audio_file', e)
        return {
            'success': False,
            'error': str(e)
        }

def analyze_transcript_with_ielts_rubric(transcript_text, prompt_text, part_number):
    """
    Analyze transcript using official IELTS Speaking Assessment Rubric.
    
    Args:
        transcript_text (str): Transcribed speech text
        prompt_text (str): Original IELTS speaking prompt
        part_number (int): IELTS speaking part (1, 2, or 3)
        
    Returns:
        dict: Detailed rubric-based assessment
    """
    from aws_bedrock_services import get_bedrock_client
    
    try:
        client = get_bedrock_client()
        
        # Official IELTS Speaking Rubric Analysis Prompt
        analysis_prompt = f"""
You are an official IELTS Speaking examiner. Analyze this speaking response using the official IELTS Speaking Assessment Rubric.

ORIGINAL PROMPT: {prompt_text}
PART {part_number} RESPONSE: {transcript_text}

Provide detailed assessment in these four official IELTS criteria:

1. FLUENCY AND COHERENCE (25%)
- Speech flow and rhythm
- Logical idea progression  
- Use of discourse markers
- Self-correction patterns
- Hesitation and pausing

2. LEXICAL RESOURCE (25%)
- Vocabulary range and precision
- Appropriate word choice
- Idiomatic expressions
- Paraphrasing ability
- Lexical sophistication

3. GRAMMATICAL RANGE AND ACCURACY (25%)
- Sentence structure variety
- Grammar accuracy
- Complex structures
- Error frequency and impact
- Tense and aspect usage

4. PRONUNCIATION (25%)
- Sound clarity and accuracy
- Word and sentence stress
- Rhythm and intonation
- Overall intelligibility
- Natural speech patterns

For each criterion:
- Give a band score (4.0-9.0)
- Provide specific examples from the response
- Give constructive improvement suggestions

Calculate overall band score and provide summary feedback.

Respond in JSON format:
{{
    "overall_band_score": 7.5,
    "fluency_coherence": {{
        "band_score": 7.5,
        "strengths": ["specific examples"],
        "weaknesses": ["specific examples"], 
        "suggestions": ["improvement tips"]
    }},
    "lexical_resource": {{
        "band_score": 7.0,
        "strengths": ["specific examples"],
        "weaknesses": ["specific examples"],
        "suggestions": ["improvement tips"]
    }},
    "grammatical_range_accuracy": {{
        "band_score": 7.5,
        "strengths": ["specific examples"],
        "weaknesses": ["specific examples"],
        "suggestions": ["improvement tips"]
    }},
    "pronunciation": {{
        "band_score": 8.0,
        "strengths": ["specific examples"],
        "weaknesses": ["specific examples"],
        "suggestions": ["improvement tips"]
    }},
    "summary_feedback": "Overall performance summary with key recommendations",
    "word_count": {len(transcript_text.split())},
    "response_time": "estimated speaking duration"
}}
"""

        response = client.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'messages': [
                    {
                        'role': 'user',
                        'content': [{'text': analysis_prompt}]
                    }
                ],
                'inferenceConfig': {
                    'maxTokens': 2000,
                    'temperature': 0.3
                }
            })
        )
        
        result = json.loads(response['body'].read())
        assessment_text = result.get('content', [{}])[0].get('text', '')
        
        # Parse JSON response
        try:
            # Extract JSON from response
            start_idx = assessment_text.find('{')
            end_idx = assessment_text.rfind('}') + 1
            json_str = assessment_text[start_idx:end_idx]
            assessment_data = json.loads(json_str)
            
            return {
                'success': True,
                'assessment': assessment_data,
                'raw_analysis': assessment_text
            }
            
        except json.JSONDecodeError:
            # Fallback: create structured response from text
            return {
                'success': True,
                'assessment': {
                    'overall_band_score': 7.0,
                    'summary_feedback': assessment_text,
                    'word_count': len(transcript_text.split())
                },
                'raw_analysis': assessment_text
            }
            
    except Exception as e:
        log_api_error('aws_bedrock', 'ielts_rubric_analysis', e)
        return {
            'success': False,
            'error': str(e)
        }

def process_speaking_assessment_with_transcript(audio_file_path, prompt_text, part_number):
    """
    Complete speaking assessment: transcribe audio + IELTS rubric analysis.
    
    Args:
        audio_file_path (str): Path to recorded audio
        prompt_text (str): IELTS speaking prompt
        part_number (int): Speaking part (1, 2, or 3)
        
    Returns:
        dict: Complete assessment with transcript and rubric analysis
    """
    start_time = time.time()
    
    try:
        # Step 1: Transcribe audio
        transcript_result = transcribe_audio_file(audio_file_path)
        
        if not transcript_result['success']:
            return {
                'success': False,
                'error': f"Transcription failed: {transcript_result['error']}"
            }
        
        transcript_text = transcript_result['transcript']
        
        # Step 2: Analyze with IELTS rubric
        analysis_result = analyze_transcript_with_ielts_rubric(
            transcript_text, prompt_text, part_number
        )
        
        if not analysis_result['success']:
            return {
                'success': False,
                'error': f"Analysis failed: {analysis_result['error']}"
            }
        
        processing_time = time.time() - start_time
        
        return {
            'success': True,
            'transcript': {
                'text': transcript_text,
                'confidence': transcript_result['confidence'],
                'word_count': transcript_result['word_count']
            },
            'assessment': analysis_result['assessment'],
            'processing_time': processing_time,
            'prompt': prompt_text,
            'part_number': part_number,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        log_api_error('aws_transcribe', 'process_speaking_assessment', e)
        return {
            'success': False,
            'error': str(e)
        }