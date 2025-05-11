"""
AssemblyAI Integration for IELTS Speaking Assessment
This module provides functions to transcribe speech using AssemblyAI and evaluate it with GPT-4o
"""

import os
import json
import time
import requests
from openai import OpenAI
from assessment_criteria.speaking_criteria import SPEAKING_BAND_DESCRIPTORS, SPEAKING_ASSESSMENT_CRITERIA

# Initialize API Clients
ASSEMBLY_API_KEY = os.environ.get("ASSEMBLYAI_IELTS_API")
OPENAI_API_KEY = os.environ.get("OPENAI_IELTS_Assessment_Key")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

headers = {
    "authorization": ASSEMBLY_API_KEY,
    "content-type": "application/json"
}

def upload_file_to_assemblyai(audio_file_path):
    """
    Upload an audio file to AssemblyAI for transcription.
    
    Args:
        audio_file_path (str): Path to the audio file to be transcribed
        
    Returns:
        str: Upload URL for the audio file
    """
    print(f"Uploading file: {audio_file_path}")
    
    with open(audio_file_path, "rb") as f:
        response = requests.post("https://api.assemblyai.com/v2/upload",
                                headers=headers,
                                data=f)
    
    if response.status_code == 200:
        return response.json()["upload_url"]
    else:
        raise Exception(f"Error uploading file: {response.text}")

def transcribe_with_assemblyai(audio_url, speaker_labels=True):
    """
    Transcribe audio using AssemblyAI.
    
    Args:
        audio_url (str): URL of the audio file to transcribe
        speaker_labels (bool): Whether to identify different speakers
        
    Returns:
        dict: Transcription result
    """
    # Create transcription request
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json_data = {
        "audio_url": audio_url,
        "speaker_labels": speaker_labels
    }
    
    # Submit the transcription request
    response = requests.post(endpoint, json=json_data, headers=headers)
    transcript_id = response.json()['id']
    
    # Poll for the transcription result
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    
    while True:
        transcription_result = requests.get(polling_endpoint, headers=headers).json()
        
        if transcription_result['status'] == 'completed':
            return transcription_result
        elif transcription_result['status'] == 'error':
            raise Exception(f"Transcription failed: {transcription_result['error']}")
            
        time.sleep(3)

def assess_speaking_with_gpt4o(transcription, prompt_text, part_number):
    """
    Assess an IELTS speaking response using GPT-4o.
    
    Args:
        transcription (str): Transcribed text of the speaking response
        prompt_text (str): The original speaking prompt
        part_number (int): IELTS speaking part number (1, 2, or 3)
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Create system prompt with IELTS criteria
    criteria_descriptions = "\n".join([f"- {criterion['name']}: {criterion['description']}" 
                                      for criterion in SPEAKING_ASSESSMENT_CRITERIA])
    
    # Format band descriptors for easier reference by the model
    band_descriptors_text = ""
    for band in range(9, 3, -1):  # Include bands 9 down to 4
        band_descriptors_text += f"\nBand {band}:\n"
        for criterion, descriptor in SPEAKING_BAND_DESCRIPTORS[band].items():
            band_descriptors_text += f"- {criterion}: {descriptor}\n"
    
    # Customize instructions based on speaking part
    part_specific_instructions = ""
    if part_number == 1:
        part_specific_instructions = """
        This is Part 1 of the IELTS Speaking test which focuses on general questions about familiar topics.
        Evaluate how well the candidate responds to basic personal questions and their ability to elaborate.
        """
    elif part_number == 2:
        part_specific_instructions = """
        This is Part 2 of the IELTS Speaking test where the candidate gives a longer monologue on a specific topic.
        Focus on their ability to speak at length, organize their ideas coherently, and develop a topic fully.
        """
    elif part_number == 3:
        part_specific_instructions = """
        This is Part 3 of the IELTS Speaking test which involves more abstract discussion related to the Part 2 topic.
        Evaluate the candidate's ability to discuss complex ideas, express and justify opinions, and speculate about issues.
        """
    
    system_prompt = f"""
    You are an expert IELTS Speaking examiner tasked with assessing a candidate's response to a Speaking prompt.
    
    Assessment Criteria:
    {criteria_descriptions}
    
    IELTS Band Descriptors (Selected bands):
    {band_descriptors_text}
    
    {part_specific_instructions}
    
    Provide a fair, detailed assessment for each criterion. Score each criterion from 0 to 9.
    
    Return your assessment in the following JSON format:
    {{
        "scores": {{
            "Fluency and Coherence": number,
            "Lexical Resource": number,
            "Grammatical Range and Accuracy": number,
            "Pronunciation": number
        }},
        "overall_band": number,
        "criterion_feedback": {{
            "Fluency and Coherence": "detailed feedback",
            "Lexical Resource": "detailed feedback",
            "Grammatical Range and Accuracy": "detailed feedback",
            "Pronunciation": "detailed feedback"
        }},
        "strengths": ["strength1", "strength2", "strength3"],
        "areas_for_improvement": ["area1", "area2", "area3"],
        "overall_feedback": "summary feedback paragraph"
    }}
    """
    
    # Format user message with the candidate's response
    user_message = f"""
    Speaking Prompt: {prompt_text}
    
    Candidate's Response (Transcription):
    {transcription}
    
    Please provide a detailed IELTS assessment of this speaking response.
    """
    
    # Call OpenAI API
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the assessment result
        assessment = json.loads(response.choices[0].message.content)
        return assessment
        
    except Exception as e:
        print(f"Error during GPT-4o assessment: {str(e)}")
        return {
            "error": str(e),
            "scores": {
                "Fluency and Coherence": 0,
                "Lexical Resource": 0,
                "Grammatical Range and Accuracy": 0,
                "Pronunciation": 0
            },
            "overall_band": 0,
            "overall_feedback": "An error occurred during the assessment."
        }

def process_speaking_response(audio_file_path, prompt_text, part_number):
    """
    Process a complete IELTS speaking response from audio file to assessment.
    The audio is processed temporarily and not stored permanently for privacy protection.
    
    Args:
        audio_file_path (str): Path to the audio file containing the speaking response
        prompt_text (str): The original speaking prompt
        part_number (int): IELTS speaking part number (1, 2, or 3)
        
    Returns:
        dict: Complete assessment results
    """
    try:
        # Step 1: Upload the audio file
        if audio_file_path.startswith('http'):
            audio_url = audio_file_path  # If it's already a URL, use it directly
        else:
            audio_url = upload_file_to_assemblyai(audio_file_path)
        
        # Step 2: Get the transcription
        transcription_result = transcribe_with_assemblyai(audio_url)
        transcription_text = transcription_result['text']
        
        # Step 3: Assess the transcription
        assessment = assess_speaking_with_gpt4o(transcription_text, prompt_text, part_number)
        
        # Step 4: Add the transcription to the result
        assessment['transcription'] = transcription_text
        
        # Note: We don't include the audio URL in the returned assessment
        # to ensure privacy protection - audio is only used temporarily
        
        return assessment
        
    except Exception as e:
        print(f"Error processing speaking response: {str(e)}")
        return {
            "error": str(e),
            "transcription": "",
            "scores": {
                "Fluency and Coherence": 0,
                "Lexical Resource": 0,
                "Grammatical Range and Accuracy": 0,
                "Pronunciation": 0
            },
            "overall_band": 0,
            "overall_feedback": "An error occurred during processing."
        }

def assess_existing_transcription(transcription_text, prompt_text, part_number):
    """
    Assess an existing transcription of an IELTS speaking response.
    
    Args:
        transcription_text (str): Transcribed text of the speaking response
        prompt_text (str): The original speaking prompt
        part_number (int): IELTS speaking part number (1, 2, or 3)
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Directly call the assessment function with the transcription
    assessment = assess_speaking_with_gpt4o(transcription_text, prompt_text, part_number)
    assessment['transcription'] = transcription_text
    return assessment