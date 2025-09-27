from app_secure import app  # noqa: F401

# For Lambda compatibility
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': 'Flask app running'
    }