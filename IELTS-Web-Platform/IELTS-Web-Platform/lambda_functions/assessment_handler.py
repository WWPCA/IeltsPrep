import json
import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
assessments_table = dynamodb.Table('ielts-genai-prep-assessments')

def lambda_handler(event, context):
    """
    Main Lambda handler for assessment endpoints
    """
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        if http_method == 'GET' and '/assessment/' in path:
            assessment_type = path.split('/assessment/')[-1]
            return handle_get_assessment_questions(assessment_type)
        elif http_method == 'POST' and path == '/api/submit-speaking-response':
            body = json.loads(event.get('body', '{}'))
            return handle_submit_speaking_response(body)
        elif http_method == 'GET' and path == '/api/get-assessment-result':
            query_params = event.get('queryStringParameters', {}) or {}
            return handle_get_assessment_result(query_params)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error in assessment lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_get_assessment_questions(assessment_type):
    """
    Get assessment questions for specific type
    """
    try:
        # Sample questions for each assessment type
        questions = {
            'academic-writing': {
                'task1': {
                    'type': 'graph_description',
                    'prompt': 'The chart below shows the percentage of households in owned and rented accommodation in England and Wales between 1918 and 2011. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.',
                    'time_limit': 20,
                    'word_count': 150
                },
                'task2': {
                    'type': 'essay',
                    'prompt': 'Some people think that universities should provide graduates with the knowledge and skills needed in the workplace. Others think that the true function of a university should be to give access to knowledge for its own sake, regardless of whether the course is useful to an employer. What, in your opinion, should be the main function of a university?',
                    'time_limit': 40,
                    'word_count': 250
                }
            },
            'general-writing': {
                'task1': {
                    'type': 'letter',
                    'prompt': 'You recently bought a piece of equipment for your kitchen but it did not work. You phoned the shop but no action was taken. Write a letter to the shop manager.',
                    'time_limit': 20,
                    'word_count': 150
                },
                'task2': {
                    'type': 'essay',
                    'prompt': 'Some people prefer to spend their lives doing the same things and avoiding change. Others, however, think that change is always a good thing. Discuss both these views and give your own opinion.',
                    'time_limit': 40,
                    'word_count': 250
                }
            },
            'academic-speaking': {
                'part1': {
                    'topic': 'Studies',
                    'questions': [
                        'What subject are you studying?',
                        'Why did you choose this subject?',
                        'What do you find most interesting about your studies?'
                    ]
                },
                'part2': {
                    'topic': 'Describe a book you have recently read',
                    'prompt': 'You should say: What the book was about, Why you decided to read it, What you learned from it, And explain whether you would recommend it to others'
                },
                'part3': {
                    'topic': 'Reading habits',
                    'questions': [
                        'How important is reading in your country?',
                        'Do you think digital books will replace physical books?',
                        'What are the benefits of reading for children?'
                    ]
                }
            },
            'general-speaking': {
                'part1': {
                    'topic': 'Hometown',
                    'questions': [
                        'Where are you from?',
                        'What do you like about your hometown?',
                        'Has your hometown changed much since you were young?'
                    ]
                },
                'part2': {
                    'topic': 'Describe a memorable meal',
                    'prompt': 'You should say: Where you had this meal, Who you were with, What you ate, And explain why it was memorable'
                },
                'part3': {
                    'topic': 'Food and culture',
                    'questions': [
                        'How important is food in your culture?',
                        'Do you think fast food is affecting traditional cooking?',
                        'What role does food play in social gatherings?'
                    ]
                }
            }
        }
        
        if assessment_type not in questions:
            return create_response(404, {'error': 'Assessment type not found'})
        
        return create_response(200, {
            'success': True,
            'assessment_type': assessment_type,
            'questions': questions[assessment_type],
            'instructions': get_assessment_instructions(assessment_type)
        })
        
    except Exception as e:
        print(f"Error getting assessment questions: {str(e)}")
        return create_response(500, {'error': 'Failed to get assessment questions'})

def handle_submit_speaking_response(body):
    """
    Submit speaking assessment response
    """
    try:
        user_id = body.get('user_id')
        assessment_type = body.get('assessment_type')
        responses = body.get('responses', {})
        
        if not all([user_id, assessment_type, responses]):
            return create_response(400, {'error': 'Missing required fields'})
        
        # Create assessment record
        assessment_id = str(uuid.uuid4())
        assessment_record = {
            'assessment_id': assessment_id,
            'user_id': user_id,
            'assessment_type': assessment_type,
            'responses': responses,
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'submitted',
            'ai_evaluation': 'pending'
        }
        
        assessments_table.put_item(Item=assessment_record)
        
        return create_response(200, {
            'success': True,
            'assessment_id': assessment_id,
            'message': 'Speaking response submitted successfully',
            'status': 'submitted'
        })
        
    except Exception as e:
        print(f"Error submitting speaking response: {str(e)}")
        return create_response(500, {'error': 'Failed to submit speaking response'})

def handle_get_assessment_result(query_params):
    """
    Get assessment result by ID
    """
    try:
        assessment_id = query_params.get('assessment_id')
        
        if not assessment_id:
            return create_response(400, {'error': 'Assessment ID required'})
        
        # Get assessment from database
        response = assessments_table.get_item(Key={'assessment_id': assessment_id})
        
        if 'Item' not in response:
            return create_response(404, {'error': 'Assessment not found'})
        
        assessment = response['Item']
        
        return create_response(200, {
            'success': True,
            'assessment': {
                'assessment_id': assessment['assessment_id'],
                'assessment_type': assessment['assessment_type'],
                'status': assessment.get('status', 'unknown'),
                'submitted_at': assessment.get('submitted_at'),
                'ai_evaluation': assessment.get('ai_evaluation', 'pending'),
                'band_score': assessment.get('band_score'),
                'feedback': assessment.get('feedback')
            }
        })
        
    except Exception as e:
        print(f"Error getting assessment result: {str(e)}")
        return create_response(500, {'error': 'Failed to get assessment result'})

def get_assessment_instructions(assessment_type):
    """
    Get instructions for specific assessment type
    """
    instructions = {
        'academic-writing': {
            'overview': 'The Academic Writing test consists of two tasks.',
            'task1': 'Describe, summarize or explain information in your own words.',
            'task2': 'Write an essay in response to a point of view, argument or problem.',
            'total_time': '60 minutes',
            'scoring': 'Task 2 carries more weight than Task 1.'
        },
        'general-writing': {
            'overview': 'The General Training Writing test consists of two tasks.',
            'task1': 'Write a letter in response to a given situation.',
            'task2': 'Write an essay in response to a point of view, argument or problem.',
            'total_time': '60 minutes',
            'scoring': 'Task 2 carries more weight than Task 1.'
        },
        'academic-speaking': {
            'overview': 'The Speaking test consists of three parts.',
            'part1': 'Introduction and interview (4-5 minutes)',
            'part2': 'Long turn - individual presentation (3-4 minutes)',
            'part3': 'Two-way discussion (4-5 minutes)',
            'total_time': '11-14 minutes',
            'scoring': 'All parts are equally weighted.'
        },
        'general-speaking': {
            'overview': 'The Speaking test consists of three parts.',
            'part1': 'Introduction and interview (4-5 minutes)',
            'part2': 'Long turn - individual presentation (3-4 minutes)',
            'part3': 'Two-way discussion (4-5 minutes)',
            'total_time': '11-14 minutes',
            'scoring': 'All parts are equally weighted.'
        }
    }
    
    return instructions.get(assessment_type, {})

def create_response(status_code, body):
    """
    Create standardized API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }