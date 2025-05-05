"""
AWS Bedrock services for IELTS assessment using Nova Micro models.
This module provides functions to evaluate IELTS writing and speaking responses
using Amazon's Nova Micro foundation model.
"""
import os
import json
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def get_bedrock_client():
    """
    Get an AWS Bedrock client using the default AWS credentials.
    
    Returns:
        boto3.client: AWS Bedrock runtime client
    """
    try:
        # Use the default AWS credentials that we've already set up and tested
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            # No need to specify access key and secret - will use the default credentials
        )
        return bedrock_runtime
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {str(e)}")
        raise

def evaluate_writing_with_nova_micro(essay_text, prompt_text, essay_type, ielts_test_type="academic"):
    """
    Evaluate an IELTS writing response using AWS Nova Micro.
    
    Args:
        essay_text (str): The student's essay text to evaluate
        prompt_text (str): The original writing prompt
        essay_type (str): "task1" or "task2" to indicate the essay type
        ielts_test_type (str): "academic" or "general" to indicate the test type
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Import writing criteria and context
    from assessment_criteria.writing_criteria import get_writing_assessment_criteria
    from assessment_criteria.context_loader import get_ielts_context_for_assessment
    
    # Get both the criteria and enhanced context
    criteria = get_writing_assessment_criteria(essay_type)
    task_number = 1 if essay_type == "task1" else 2
    context = get_ielts_context_for_assessment("writing", ielts_test_type, task_number)
    
    # Determine if this is a letter task (General Training Task 1)
    is_letter_task = ielts_test_type.lower() == "general" and essay_type == "task1"
    response_type = "letter" if is_letter_task else "essay"
    
    # Create system prompt with assessment instructions and context
    system_message = (
        f"You are an expert IELTS examiner evaluating a {ielts_test_type.capitalize()} {essay_type} writing {response_type}. "
        f"Assess the following {response_type} based on the official IELTS criteria below. "
        f"The original prompt was: '{prompt_text}'"
        f"\n\nIELTS Writing Assessment Criteria:\n{json.dumps(criteria, indent=2)}"
        f"\n\nAssessment Guidance:\n{context['assessment_guidance']}"
        f"\n\nIELTS Band Descriptors:\n{json.dumps(context['band_descriptors'], indent=2)}"
        f"\n\nProvide detailed feedback and assign a band score from 0-9 (with .5 increments) for each criterion. "
        f"Also provide an overall band score based on the average of the individual criteria scores. "
        f"Format your response as JSON with this structure: "
        f"{{\"criteria_scores\": {{criterion1: score, criterion2: score, ...}}, "
        f"\"overall_score\": float, "
        f"\"detailed_feedback\": {{criterion1: feedback, criterion2: feedback, ...}}, "
        f"\"summary_feedback\": string}}"
    )

    # Create user message with the essay
    user_message = f"Essay to evaluate:\n\n{essay_text}"
    
    try:
        client = get_bedrock_client()
        
        # Prepare the request for Nova Micro
        request_body = {
            "inferenceConfig": {
                "max_new_tokens": 2000,
                "temperature": 0.2,  # Low temperature for more consistent evaluations
                "top_p": 0.9
            },
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "text": system_message
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": user_message
                        }
                    ]
                }
            ]
        }
        
        # Make the API call
        response = client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        model_output = response_body.get('output', {})
        
        # Extract the response text from Nova Micro
        response_text = model_output.get('text', '')
        
        # Parse the JSON response from the model
        try:
            # Try to extract JSON from the response text
            # First, find the JSON part in case there's surrounding text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                assessment_result = json.loads(json_str)
            else:
                # If no JSON found, handle as error
                raise ValueError("No valid JSON found in model response")
                
            return assessment_result
            
        except (json.JSONDecodeError, ValueError) as json_err:
            logger.error(f"Failed to parse assessment result: {str(json_err)}")
            logger.error(f"Raw response: {response_text}")
            # Return a fallback structured response
            return {
                "criteria_scores": {},
                "overall_score": 0,
                "detailed_feedback": {
                    "error": f"Failed to parse assessment result: {str(json_err)}"
                },
                "summary_feedback": "An error occurred during assessment."
            }
            
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"AWS Bedrock error: {error_code} - {error_message}")
        raise
    except Exception as e:
        logger.error(f"Error evaluating writing with Nova Micro: {str(e)}")
        raise

def assess_speaking_with_nova_micro(transcription, prompt_text, part_number):
    """
    Assess an IELTS speaking response using AWS Nova Micro.
    
    Args:
        transcription (str): Transcribed text of the speaking response
        prompt_text (str): The original speaking prompt
        part_number (int): IELTS speaking part number (1, 2, or 3)
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Import speaking criteria
    from assessment_criteria.speaking_criteria import get_speaking_assessment_criteria
    
    criteria = get_speaking_assessment_criteria()
    
    # Create system prompt with assessment instructions
    system_message = (
        f"You are an expert IELTS examiner evaluating a Part {part_number} speaking response. "
        f"Assess the following transcribed speech based on the official IELTS speaking criteria below. "
        f"The original prompt was: '{prompt_text}'"
        f"\n\nIELTS Speaking Assessment Criteria:\n{json.dumps(criteria, indent=2)}"
        f"\n\nProvide detailed feedback and assign a band score from 0-9 (with .5 increments) for each criterion. "
        f"Also provide an overall band score based on the average of the individual criteria scores. "
        f"Format your response as JSON with this structure: "
        f"{{\"criteria_scores\": {{criterion1: score, criterion2: score, ...}}, "
        f"\"overall_score\": float, "
        f"\"detailed_feedback\": {{criterion1: feedback, criterion2: feedback, ...}}, "
        f"\"summary_feedback\": string}}"
    )

    # Create user message with the transcription
    user_message = f"Speaking response transcription to evaluate:\n\n{transcription}"
    
    try:
        client = get_bedrock_client()
        
        # Prepare the request for Nova Micro
        request_body = {
            "inferenceConfig": {
                "max_new_tokens": 2000,
                "temperature": 0.2,  # Low temperature for more consistent evaluations
                "top_p": 0.9
            },
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "text": system_message
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": user_message
                        }
                    ]
                }
            ]
        }
        
        # Make the API call
        response = client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        model_output = response_body.get('output', {})
        
        # Extract the response text from Nova Micro
        response_text = model_output.get('text', '')
        
        # Parse the JSON response from the model
        try:
            # Try to extract JSON from the response text
            # First, find the JSON part in case there's surrounding text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                assessment_result = json.loads(json_str)
            else:
                # If no JSON found, handle as error
                raise ValueError("No valid JSON found in model response")
                
            return assessment_result
            
        except (json.JSONDecodeError, ValueError) as json_err:
            logger.error(f"Failed to parse assessment result: {str(json_err)}")
            logger.error(f"Raw response: {response_text}")
            # Return a fallback structured response
            return {
                "criteria_scores": {},
                "overall_score": 0,
                "detailed_feedback": {
                    "error": f"Failed to parse assessment result: {str(json_err)}"
                },
                "summary_feedback": "An error occurred during assessment."
            }
            
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"AWS Bedrock error: {error_code} - {error_message}")
        raise
    except Exception as e:
        logger.error(f"Error assessing speaking with Nova Micro: {str(e)}")
        raise

# Add simple test function to validate credentials and access
def test_bedrock_nova_micro_access():
    """Test if we have proper access to AWS Bedrock Nova Micro model."""
    try:
        client = get_bedrock_client()
        
        # Prepare a simple test request
        request_body = {
            "inferenceConfig": {
                "max_new_tokens": 100
            },
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Explain IELTS assessment in one sentence."
                        }
                    ]
                }
            ]
        }
        
        # Make the API call
        response = client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse the response to verify it worked
        response_body = json.loads(response.get('body').read())
        model_output = response_body.get('output', {})
        response_text = model_output.get('text', '')
        
        print("Successfully connected to AWS Bedrock Nova Micro!")
        print(f"Test response: {response_text}")
        return True
        
    except Exception as e:
        print(f"Failed to connect to AWS Bedrock Nova Micro: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the connection if run directly
    test_bedrock_nova_micro_access()