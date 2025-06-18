import json
import traceback

def lambda_handler(event, context):
    try:
        # Basic test response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'IELTS GenAI Prep API is running',
                'version': '1.0',
                'environment': 'production',
                'event': event
            })
        }
    except Exception as e:
        # Return detailed error information
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'event': event
            })
        }