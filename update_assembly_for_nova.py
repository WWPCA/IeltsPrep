"""
Update the AssemblyAI integration to use AWS Nova Micro for assessment.
This script modifies the assemblyai_services.py file to replace GPT-4o with Nova Micro
for IELTS speaking assessment while keeping the transcription service the same.
"""
import os
import re

def update_assembly_services():
    """Update assemblyai_services.py to use AWS Nova Micro for assessment."""
    
    # Path to the original file
    original_file = 'assemblyai_services.py'
    
    # Read the original file
    try:
        with open(original_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {original_file} not found.")
        return False
    
    # Create a backup of the original file
    backup_file = f'{original_file}.bak'
    try:
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"Created backup at {backup_file}")
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False
    
    # Replace the assess_speaking_with_gpt4o function with Nova Micro version
    new_function = """
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
    # Import the Nova Micro assessment function
    from aws_bedrock_services import assess_speaking_with_nova_micro as nova_assess
    
    # Call the Nova Micro assessment function
    try:
        assessment_result = nova_assess(transcription, prompt_text, part_number)
        return assessment_result
    except Exception as e:
        print(f"Error assessing speaking with Nova Micro: {str(e)}")
        # Fall back to OpenAI assessment if Nova fails
        print("Falling back to OpenAI assessment...")
        from openai import OpenAI
        
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Get speaking assessment criteria
        from assessment_criteria.speaking_criteria import get_speaking_assessment_criteria
        criteria = get_speaking_assessment_criteria()
        
        # Format the prompt
        system_message = (
            f"You are an expert IELTS examiner evaluating a Part {part_number} speaking response. "
            f"Assess the following transcribed speech based on the official IELTS speaking criteria below. "
            f"The original prompt was: '{prompt_text}'"
            f"\\n\\nIELTS Speaking Assessment Criteria:\\n{json.dumps(criteria, indent=2)}"
            f"\\n\\nProvide detailed feedback and assign a band score from 0-9 (with .5 increments) for each criterion. "
            f"Also provide an overall band score based on the average of the individual criteria scores."
        )
        
        # Make the OpenAI API call
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Speaking response transcription to evaluate:\\n\\n{transcription}"}
                ]
            )
            
            # Parse the JSON response
            assessment_data = json.loads(response.choices[0].message.content)
            return assessment_data
            
        except Exception as inner_e:
            print(f"Error with OpenAI fallback: {str(inner_e)}")
            # Return a basic error response
            return {
                "criteria_scores": {},
                "overall_score": 0,
                "detailed_feedback": {
                    "error": f"Assessment failed: {str(inner_e)}"
                },
                "summary_feedback": "An error occurred during assessment."
            }
"""
    
    # Replace the assess_speaking_with_gpt4o function
    pattern = r'def assess_speaking_with_gpt4o\(transcription, prompt_text, part_number\):.*?""".*?dict: Assessment results including scores and feedback.*?""".*?return assessment_data'
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # Update the process_speaking_response function to use Nova Micro
    original_call = "assessment_data = assess_speaking_with_gpt4o(transcription_text, prompt_text, part_number)"
    new_call = "assessment_data = assess_speaking_with_nova_micro(transcription_text, prompt_text, part_number)"
    new_content = new_content.replace(original_call, new_call)
    
    # Update the assess_existing_transcription function to use Nova Micro
    original_call2 = "return assess_speaking_with_gpt4o(transcription_text, prompt_text, part_number)"
    new_call2 = "return assess_speaking_with_nova_micro(transcription_text, prompt_text, part_number)"
    new_content = new_content.replace(original_call2, new_call2)
    
    # Make sure we import the aws_bedrock_services module
    if "import aws_bedrock_services" not in new_content:
        import_line = "import json\nimport os\nimport aws_bedrock_services"
        new_content = new_content.replace("import json\nimport os", import_line)
    
    # Write the updated content back to the file
    try:
        with open(original_file, 'w') as f:
            f.write(new_content)
        print(f"Successfully updated {original_file} to use AWS Nova Micro for assessment.")
        return True
    except Exception as e:
        print(f"Error writing updated file: {str(e)}")
        return False

if __name__ == "__main__":
    update_assembly_services()