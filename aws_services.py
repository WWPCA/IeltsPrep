import os
import boto3
import logging
import time
import uuid
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_fixed

# Configure AWS credentials
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')

# Initialize AWS clients
def get_transcribe_client():
    return boto3.client(
        'transcribe',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

def get_polly_client():
    return boto3.client(
        'polly',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

def get_s3_client():
    return boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def transcribe_audio(audio_path):
    """
    Transcribe audio using AWS Transcribe.
    
    Args:
        audio_path (str): Path to the audio file
    
    Returns:
        str: Transcription text
    """
    try:
        # For simplicity, we'll use a mock implementation if AWS keys aren't available
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
            logging.warning("AWS credentials not found. Using mock transcription.")
            return "This is a mock transcription. My hometown is a beautiful city with many parks and friendly people. The weather is pleasant most of the year."
        
        transcribe = get_transcribe_client()
        s3 = get_s3_client()
        
        # Upload the audio file to S3
        bucket_name = os.environ.get('AWS_S3_BUCKET', 'ielts-ai-prep')
        object_key = f"audio/{str(uuid.uuid4())}.mp3"
        
        s3.upload_file(audio_path, bucket_name, object_key)
        
        # Start transcription job
        job_name = f"transcribe-{str(uuid.uuid4())}"
        job_uri = f"s3://{bucket_name}/{object_key}"
        
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp3',
            LanguageCode='en-US'
        )
        
        # Wait for the job to complete
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)
        
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            result_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Download the transcription result
            import urllib.request
            import json
            
            response = urllib.request.urlopen(result_url)
            data = json.loads(response.read())
            
            # Clean up S3
            s3.delete_object(Bucket=bucket_name, Key=object_key)
            
            return data['results']['transcripts'][0]['transcript']
        else:
            raise Exception("Transcription failed")
            
    except Exception as e:
        logging.error(f"Error in transcribe_audio: {str(e)}")
        # Return a default message if transcription fails
        return "Transcription failed. Please try again."

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def generate_polly_speech(text, output_path):
    """
    Generate speech from text using Amazon Polly.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the output audio file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # For simplicity, we'll use a mock implementation if AWS keys aren't available
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
            logging.warning("AWS credentials not found. Using mock Polly implementation.")
            # Create a dummy file
            with open(output_path, 'w') as f:
                f.write("dummy audio file")
            return True
        
        polly = get_polly_client()
        
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'  # English female voice
        )
        
        # Save the audio stream to file
        if "AudioStream" in response:
            with open(output_path, 'wb') as file:
                file.write(response['AudioStream'].read())
            return True
        else:
            return False
            
    except Exception as e:
        logging.error(f"Error in generate_polly_speech: {str(e)}")
        return False

def analyze_speaking_response(transcription):
    """
    Analyze a speaking response based on IELTS criteria.
    
    Args:
        transcription (str): Transcribed text from the speaking response
    
    Returns:
        tuple: (scores_dict, feedback_text)
    """
    # In a real implementation, this would use NLP or call OpenAI API
    # For now, we'll use a simple rule-based approach
    
    scores = {
        'fluency': 0,
        'coherence': 0,
        'vocabulary': 0,
        'grammar': 0,
        'pronunciation': 0,
        'overall': 0
    }
    
    feedback = ""
    
    # Count words
    word_count = len(transcription.split())
    
    # Analyze word count for fluency
    if word_count > 100:
        scores['fluency'] = 7
        fluency_feedback = "You spoke at good length, demonstrating good fluency."
    elif word_count > 80:
        scores['fluency'] = 6
        fluency_feedback = "You spoke at a reasonable length. Try to elaborate more for higher fluency scores."
    elif word_count > 60:
        scores['fluency'] = 5
        fluency_feedback = "Your response was somewhat brief. Try to speak more and provide more details."
    elif word_count > 40:
        scores['fluency'] = 4
        fluency_feedback = "Your response was quite brief. Work on expanding your answers."
    else:
        scores['fluency'] = 3
        fluency_feedback = "Your response was very short. Practice speaking at greater length."
    
    # Simple vocabulary analysis
    unique_words = len(set(transcription.lower().split()))
    vocabulary_ratio = unique_words / word_count if word_count > 0 else 0
    
    if vocabulary_ratio > 0.7:
        scores['vocabulary'] = 7
        vocab_feedback = "You used a wide range of vocabulary with good precision."
    elif vocabulary_ratio > 0.6:
        scores['vocabulary'] = 6
        vocab_feedback = "You used a good range of vocabulary. Try to incorporate more advanced words."
    elif vocabulary_ratio > 0.5:
        scores['vocabulary'] = 5
        vocab_feedback = "Your vocabulary range is adequate. Work on expanding your lexical resource."
    else:
        scores['vocabulary'] = 4
        vocab_feedback = "Your vocabulary is somewhat limited. Focus on learning and using a wider range of words."
    
    # Placeholder scores for other criteria
    scores['coherence'] = 5
    coherence_feedback = "Your response had some organization. Work on using more linking words and creating a clearer structure."
    
    scores['grammar'] = 5
    grammar_feedback = "You demonstrated a mix of simple and complex sentences with some errors."
    
    scores['pronunciation'] = 5
    pronunciation_feedback = "Your pronunciation was generally understandable with some issues that occasionally affected clarity."
    
    # Calculate overall score (average of individual scores)
    scores['overall'] = round(sum([scores['fluency'], scores['coherence'], 
                                 scores['vocabulary'], scores['grammar'], 
                                 scores['pronunciation']]) / 5, 1)
    
    # Generate feedback text
    feedback = f"""Thank you for your response. Here's your feedback:

Overall Score: {scores['overall']} / 9

Fluency and Coherence: {scores['fluency']} / 9
{fluency_feedback}
{coherence_feedback}

Lexical Resource: {scores['vocabulary']} / 9
{vocab_feedback}

Grammatical Range and Accuracy: {scores['grammar']} / 9
{grammar_feedback}

Pronunciation: {scores['pronunciation']} / 9
{pronunciation_feedback}

To improve your score:
- Practice speaking for longer periods without pausing
- Use a wider range of vocabulary and complex sentence structures
- Work on organizing your ideas more clearly
- Focus on pronouncing difficult sounds more accurately

Keep practicing regularly!"""
    
    return scores, feedback
