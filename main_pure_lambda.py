from pure_lambda_handler import lambda_handler

# Entry point for pure Lambda architecture
if __name__ == "__main__":
    import json
    
    # Test the pure handler locally
    test_event = {
        'path': '/api/health',
        'httpMethod': 'GET',
        'headers': {},
        'queryStringParameters': {},
        'body': ''
    }
    
    class MockContext:
        aws_request_id = 'local-test'
    
    result = lambda_handler(test_event, MockContext())
    print("Pure Lambda Handler Test:")
    print(json.dumps(result, indent=2))
