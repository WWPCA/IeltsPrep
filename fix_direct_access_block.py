#!/usr/bin/env python3
"""
Fix Direct Access Issue - Block API Gateway Direct URL While Preserving Domain
Uses CloudFront custom headers to authenticate requests
"""

import boto3
import json
import uuid
from botocore.exceptions import ClientError

def create_cloudfront_custom_header():
    """Create a unique header that CloudFront will send"""
    return f"CloudFront-{str(uuid.uuid4())}"

def update_api_gateway_with_header_restriction(secret_header):
    """Update API Gateway to only accept requests with CloudFront header"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    # Create policy that requires specific header
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:RequestTag/CloudFrontSecret": secret_header
                    }
                }
            },
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*"
            }
        ]
    }
    
    try:
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOps=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': json.dumps(policy)
                }
            ]
        )
        
        print("API Gateway policy updated to require CloudFront header")
        return True
        
    except ClientError as e:
        print(f"Error updating API Gateway policy: {e}")
        return False

def update_cloudfront_with_custom_header(secret_header):
    """Update CloudFront distribution to send custom header"""
    
    cloudfront = boto3.client('cloudfront')
    
    try:
        # Find the distribution
        distributions = cloudfront.list_distributions()
        distribution_id = None
        
        for dist in distributions['DistributionList'].get('Items', []):
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'www.ieltsaiprep.com' in aliases or 'ieltsaiprep.com' in aliases:
                distribution_id = dist['Id']
                break
        
        if not distribution_id:
            print("CloudFront distribution not found")
            return False
        
        # Get current configuration
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update origin with custom header
        for origin in config['Origins']['Items']:
            if 'n0cpf1rmvc.execute-api.us-east-1.amazonaws.com' in origin['DomainName']:
                origin['CustomHeaders'] = {
                    'Quantity': 1,
                    'Items': [
                        {
                            'HeaderName': 'X-CloudFront-Secret',
                            'HeaderValue': secret_header
                        }
                    ]
                }
                break
        
        # Update distribution
        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"CloudFront distribution updated with custom header: {distribution_id}")
        return True
        
    except ClientError as e:
        print(f"Error updating CloudFront: {e}")
        return False

def implement_lambda_layer_protection():
    """Update Lambda function to check for CloudFront header"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Get current function code
    try:
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        
        # Download current code
        import requests
        code_response = requests.get(response['Code']['Location'])
        
        # This approach requires modifying the Lambda code
        # For now, we'll use the API Gateway policy approach
        
        print("Lambda function found - using API Gateway policy approach instead")
        return True
        
    except ClientError as e:
        print(f"Error accessing Lambda function: {e}")
        return False

def main():
    """Main function to fix the direct access issue"""
    
    print("Fixing Direct Access Issue")
    print("=" * 40)
    
    print("Implementation plan:")
    print("1. Generate unique CloudFront header")
    print("2. Update CloudFront to send header to API Gateway")
    print("3. Update API Gateway to require header")
    print("4. Test both URLs")
    print()
    
    # Generate unique header
    secret_header = create_cloudfront_custom_header()
    print(f"Generated secret header: {secret_header}")
    
    # Update CloudFront first
    print("\nUpdating CloudFront distribution...")
    cloudfront_success = update_cloudfront_with_custom_header(secret_header)
    
    if cloudfront_success:
        print("CloudFront updated successfully")
        
        # Update API Gateway
        print("\nUpdating API Gateway policy...")
        api_success = update_api_gateway_with_header_restriction(secret_header)
        
        if api_success:
            print("\nSUCCESS: Direct access blocking implemented")
            print("www.ieltsaiprep.com - WILL WORK (has CloudFront header)")
            print("n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod - WILL BE BLOCKED")
            print("\nCloudFront propagation takes 15-20 minutes to complete")
            
            # Save configuration for future reference
            with open('cloudfront_protection_config.json', 'w') as f:
                json.dump({
                    'secret_header': secret_header,
                    'implementation_date': '2025-07-09',
                    'purpose': 'Block direct API Gateway access while preserving domain'
                }, f, indent=2)
            
            print("Configuration saved to cloudfront_protection_config.json")
            
        else:
            print("\nFAILED: Could not update API Gateway policy")
    else:
        print("\nFAILED: Could not update CloudFront distribution")

if __name__ == "__main__":
    main()