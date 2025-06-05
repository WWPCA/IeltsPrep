"""
Test Nova Micro Writing Assessment API Calls
Verify that amazon.nova-micro-v1:0 is working for IELTS writing evaluations
"""

import os
import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nova_micro_direct():
    """Test direct Nova Micro invocation for writing assessment"""
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        logger.info("Testing direct Nova Micro invocation with amazon.nova-micro-v1:0...")
        
        # Sample IELTS writing task for testing
        sample_essay = """
        Some people believe that the best way to increase road safety is to increase the minimum legal age for driving cars or riding motorbikes. To what extent do you agree or disagree?

        In recent years, road accidents have become a significant concern worldwide. While some argue that raising the minimum driving age would improve road safety, I believe this approach alone is insufficient and that a combination of better education, stricter enforcement, and improved infrastructure would be more effective.

        Firstly, age alone does not determine driving competency. Many young drivers are careful and responsible, while some older drivers may lack the necessary skills or awareness. Research shows that experience and proper training are more crucial factors in safe driving than age. Therefore, simply increasing the age limit would unfairly restrict capable young people from accessing transportation.

        However, I acknowledge that younger drivers do statistically have higher accident rates due to inexperience and risk-taking behavior. Instead of raising the age limit, governments should focus on improving driver education programs and implementing graduated licensing systems that gradually introduce new drivers to more complex driving situations.

        In conclusion, while age restrictions might have some benefits, a comprehensive approach involving better education, stricter enforcement of traffic laws, and improved road infrastructure would be more effective in enhancing road safety for all users.
        """
        
        # Nova Micro request for writing assessment
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": f"""You are an expert IELTS examiner evaluating an Academic Task 2 writing essay. 
                            
                            Assess this essay based on IELTS criteria:
                            - Task Response
                            - Coherence and Cohesion  
                            - Lexical Resource
                            - Grammatical Range and Accuracy
                            
                            Provide scores (0-9) and feedback in JSON format:
                            {{"task_response": score, "coherence": score, "lexical": score, "grammar": score, "overall": score, "feedback": "detailed feedback"}}
                            
                            Essay: {sample_essay}"""
                        }
                    ]
                }
            ]
        }
        
        # Direct call to Nova Micro
        response = client.invoke_model(
            modelId='amazon.nova-micro-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        logger.info("Nova Micro direct call successful!")
        
        # Check response structure
        if 'output' in result and 'message' in result['output']:
            content = result['output']['message']['content']
            
            if content and len(content) > 0:
                response_text = content[0].get('text', '')
                
                print("✓ Nova Micro writing assessment working")
                print(f"  Response length: {len(response_text)} characters")
                print(f"  Response preview: {response_text[:200]}...")
                
                # Try to extract JSON assessment
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    try:
                        assessment_json = json.loads(response_text[json_start:json_end])
                        print("  ✓ JSON assessment extracted successfully")
                        print(f"  Overall score: {assessment_json.get('overall', 'N/A')}")
                    except:
                        print("  ⚠ Response not in expected JSON format")
                
                return True, result
            else:
                print("✗ Empty content in response")
                return False, result
        else:
            print("✗ Unexpected response structure")
            return False, result
            
    except Exception as e:
        error_message = str(e)
        print(f"✗ Nova Micro writing assessment failed: {error_message}")
        
        if "ValidationException" in error_message:
            print("  Issue: ValidationException - Model access problem")
        elif "AccessDeniedException" in error_message:
            print("  Issue: AccessDeniedException - Credential problem")
        else:
            print(f"  Issue: {error_message}")
        
        return False, error_message

def test_writing_assessment_service():
    """Test the writing assessment service integration"""
    
    try:
        from nova_writing_assessment import evaluate_writing_with_nova
        
        sample_essay = "Climate change is one of the most pressing issues of our time. Governments should take immediate action to reduce carbon emissions through stricter regulations and investment in renewable energy."
        
        sample_prompt = "Some people believe that governments should take primary responsibility for addressing climate change, while others think individuals should take the lead. Discuss both views and give your opinion."
        
        result = evaluate_writing_with_nova(
            essay_text=sample_essay,
            prompt_text=sample_prompt,
            essay_type="task2",
            test_type="academic"
        )
        
        if 'criteria_scores' in result:
            print("✓ Writing assessment service working")
            print(f"  Overall score: {result.get('overall_score', 'N/A')}")
            print(f"  Criteria scores available: {len(result['criteria_scores'])} criteria")
            
            if 'detailed_feedback' in result:
                print("  ✓ Detailed feedback provided")
            
            return True, result
        else:
            print(f"✗ Writing assessment service failed: {result}")
            return False, result
            
    except Exception as e:
        print(f"✗ Service integration failed: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("Testing Nova Micro writing assessment...")
    
    # Test 1: Direct API call
    success1, result1 = test_nova_micro_direct()
    
    if success1:
        print("\n" + "="*50)
        print("✓ Nova Micro API access confirmed")
        
        # Test 2: Service integration
        success2, result2 = test_writing_assessment_service()
        
        if success2:
            print("✓ Complete Nova Micro writing assessment working")
        else:
            print("✗ Service integration needs adjustment")
    else:
        print("\n" + "="*50)
        print("✗ Nova Micro API access issue")
        print("  This indicates credential or permission problems")