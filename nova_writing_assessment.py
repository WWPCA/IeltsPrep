"""
IELTS Writing Assessment with AWS Bedrock Nova Micro
This module provides enhanced writing assessment using AWS Bedrock Nova Micro model
with context-aware prompting based on official IELTS guidelines.
"""

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

from assessment_criteria.context_loader import get_ielts_context_for_assessment

logger = logging.getLogger(__name__)

def get_bedrock_client():
    """
    Get an AWS Bedrock client using environment credentials.
    
    Returns:
        boto3.client: AWS Bedrock runtime client
    """
    try:
        # Use environment variables for credentials
        return boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {str(e)}")
        raise

def evaluate_writing_with_nova(essay_text, prompt_text, essay_type, test_type="academic"):
    """
    Evaluate an IELTS writing response using AWS Bedrock Nova Micro with enhanced context.
    
    Args:
        essay_text (str): The student's essay text to evaluate
        prompt_text (str): The original writing prompt
        essay_type (str): "task1" or "task2" to indicate the essay type
        test_type (str): "academic" or "general" to indicate test type
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Get the appropriate context for this assessment
    task_number = 1 if essay_type == "task1" else 2
    context = get_ielts_context_for_assessment("writing", test_type, task_number)
    
    # Determine if this is a letter task (General Training Task 1)
    is_letter_task = test_type.lower() == "general" and essay_type == "task1"
    response_type = "letter" if is_letter_task else "essay"
    
    # Get the correct criteria for this task
    if essay_type == "task1":
        criteria = ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
    else:  # task2
        criteria = ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
    
    # Create a detailed system prompt with assessment instructions and context
    system_message = (
        f"You are an expert IELTS examiner evaluating a {test_type.capitalize()} {essay_type} writing {response_type}. "
        f"Assess the following {response_type} based on the official IELTS criteria and band descriptors below. "
        f"The original prompt was: '{prompt_text}'"
        
        f"\n\nIELTS Writing Assessment Criteria:"
        f"\n- {criteria[0]}: {context['band_descriptors'][9][criteria[0]]}"
        f"\n- {criteria[1]}: {context['band_descriptors'][9][criteria[1]]}"
        f"\n- {criteria[2]}: {context['band_descriptors'][9][criteria[2]]}"
        f"\n- {criteria[3]}: {context['band_descriptors'][9][criteria[3]]}"
        
        f"\n\nAssessment Guidance:\n{context['assessment_guidance']}"
        
        f"\n\nPrompt Analysis Requirements:"
        f"Pay special attention to how well the response addresses the specific requirements of the prompt. "
        f"Carefully analyze if the writer has:"
        f"\n1. Fully understood the question/task in the prompt"
        f"\n2. Addressed all parts or aspects of the prompt"
        f"\n3. Provided relevant examples and details that directly relate to the prompt"
        f"\n4. Stayed focused on the topic without irrelevant digressions"
        f"\n5. Demonstrated understanding of key concepts mentioned in the prompt"
        f"\nThis analysis should significantly impact the {criteria[0]} score."
        
        f"\n\nIELTS Band Descriptors (Bands 9-5):"
    )
    
    # Add key band descriptors (9, 7, 5)
    for band in [9, 7, 5]:
        system_message += f"\n\nBand {band}:"
        for criterion in criteria:
            system_message += f"\n- {criterion}: {context['band_descriptors'][band][criterion]}"
    
    # Add detailed instructions for the assessment output format
    system_message += (
        f"\n\nProvide detailed feedback and assign a band score from 0-9 (with .5 increments) for each criterion. "
        f"Also provide an overall band score based on the average of the individual criteria scores. "
        f"Format your response as JSON with this structure: "
        f"{{\"criteria_scores\": {{\"{criteria[0]}\": score, \"{criteria[1]}\": score, \"{criteria[2]}\": score, \"{criteria[3]}\": score}}, "
        f"\"overall_score\": float, "
        f"\"detailed_feedback\": {{\"{criteria[0]}\": feedback, \"{criteria[1]}\": feedback, \"{criteria[2]}\": feedback, \"{criteria[3]}\": feedback}}, "
        f"\"prompt_analysis\": {{\"score\": float, \"explanation\": string}}, "
        f"\"summary_feedback\": string, "
        f"\"improvement_tips\": [\"tip1\", \"tip2\", \"tip3\"]}}"
        f"\n\nIn the prompt_analysis section, include a specific score (0-10) and explanation of how well the response addresses the specific requirements in the prompt. "
        f"This should analyze whether the writer has fully understood and addressed all aspects of the prompt."
    )
    
    # Create user message with the essay
    user_message = f"{response_type.capitalize()} to evaluate:\n\n{essay_text}"
    
    try:
        client = get_bedrock_client()
        
        # Prepare the request for Nova Micro with correct format
        # Nova Micro expects messages array with "content" as an array of objects
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": f"{system_message}\n\n{user_message}"}
                    ]
                }
            ]
        }
        
        # Make the API call to Nova Micro for text-based writing assessment
        response = client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse the response - Nova Micro uses a different format
        response_body = json.loads(response.get('body').read())
        
        # Navigate the nested structure to get the response text
        # For Nova Micro format: output -> message -> content -> [0] -> text
        model_output = response_body.get('output', {})
        message = model_output.get('message', {})
        content_array = message.get('content', [])
        
        # Extract the response text from the first content item
        response_text = ""
        if content_array and len(content_array) > 0:
            response_text = content_array[0].get('text', '')
        
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
                "summary_feedback": "An error occurred during assessment.",
                "improvement_tips": ["Please try submitting your response again."]
            }
            
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"AWS Bedrock error: {error_code} - {error_message}")
        raise
    except Exception as e:
        logger.error(f"Error evaluating writing with Nova Sonic: {str(e)}")
        raise

def analyze_writing_response(student_essay, prompt, task_type="task1", test_type="academic"):
    """
    Analyze an IELTS writing response and provide detailed feedback.
    This is the main function to call from other modules.
    
    Args:
        student_essay (str): The student's essay to evaluate
        prompt (str): The original writing prompt
        task_type (str): "task1" or "task2" to indicate the essay type
        test_type (str): "academic" or "general" to indicate the test type
        
    Returns:
        dict: Assessment results with scores, feedback, and improvement tips
    """
    try:
        # Get a detailed assessment using Nova Micro
        assessment = evaluate_writing_with_nova(
            student_essay, 
            prompt, 
            task_type,
            test_type
        )
        
        # Ensure we have all expected keys
        if not assessment.get("improvement_tips"):
            assessment["improvement_tips"] = [
                "Focus on addressing all parts of the task",
                "Organize your ideas more clearly with proper paragraphing",
                "Use a wider range of vocabulary and grammar structures"
            ]
            
        # Round the overall score to the nearest 0.5
        overall_score = assessment.get("overall_score", 0)
        rounded_score = round(overall_score * 2) / 2
        assessment["overall_score"] = rounded_score
            
        return assessment
        
    except Exception as e:
        logger.error(f"Error analyzing writing response: {str(e)}")
        # Provide a meaningful error response
        return {
            "criteria_scores": {
                "Task Achievement": 0,
                "Coherence and Cohesion": 0, 
                "Lexical Resource": 0,
                "Grammatical Range and Accuracy": 0
            },
            "overall_score": 0,
            "detailed_feedback": {
                "error": f"Assessment service unavailable: {str(e)}"
            },
            "summary_feedback": "We are currently experiencing technical difficulties with our assessment service. Please try again later.",
            "improvement_tips": ["Please try submitting your response again later."]
        }

def assess_writing_task1(essay_text, prompt_text, test_type="academic"):
    """
    Assess IELTS Writing Task 1 using Nova Micro.
    
    Args:
        essay_text (str): The student's Task 1 response
        prompt_text (str): The original Task 1 prompt
        test_type (str): "academic" or "general"
    
    Returns:
        dict: Assessment results
    """
    return analyze_writing_response(essay_text, prompt_text, "task1", test_type)

def assess_writing_task2(essay_text, prompt_text, test_type="academic"):
    """
    Assess IELTS Writing Task 2 using Nova Micro.
    
    Args:
        essay_text (str): The student's Task 2 response
        prompt_text (str): The original Task 2 prompt
        test_type (str): "academic" or "general"
    
    Returns:
        dict: Assessment results
    """
    return analyze_writing_response(essay_text, prompt_text, "task2", test_type)

def assess_complete_writing_test(task1_text, task1_prompt, task2_text, task2_prompt, test_type="academic"):
    """
    Assess a complete IELTS Writing test (both tasks) using Nova Micro.
    
    Args:
        task1_text (str): The student's Task 1 response
        task1_prompt (str): The original Task 1 prompt
        task2_text (str): The student's Task 2 response
        task2_prompt (str): The original Task 2 prompt
        test_type (str): "academic" or "general"
    
    Returns:
        dict: Combined assessment results for both tasks
    """
    try:
        # Assess both tasks separately
        task1_assessment = assess_writing_task1(task1_text, task1_prompt, test_type)
        task2_assessment = assess_writing_task2(task2_text, task2_prompt, test_type)
        
        # Calculate overall score (Task 2 weighted more heavily)
        task1_score = task1_assessment.get("overall_score", 0)
        task2_score = task2_assessment.get("overall_score", 0)
        overall_score = round(((task1_score + task2_score * 2) / 3) * 2) / 2  # Round to nearest 0.5
        
        return {
            "task1_assessment": task1_assessment,
            "task2_assessment": task2_assessment,
            "overall_score": overall_score,
            "summary_feedback": f"Overall performance across both writing tasks shows {overall_score} band level.",
            "improvement_tips": [
                "Focus on fully addressing all parts of each task",
                "Improve coherence and organization across both responses",
                "Expand vocabulary range and accuracy",
                "Work on grammatical complexity and accuracy"
            ]
        }
    except Exception as e:
        logger.error(f"Error assessing complete writing test: {str(e)}")
        return {
            "task1_assessment": {"overall_score": 0, "error": str(e)},
            "task2_assessment": {"overall_score": 0, "error": str(e)},
            "overall_score": 0,
            "summary_feedback": "Assessment service temporarily unavailable.",
            "improvement_tips": ["Please try again later."]
        }