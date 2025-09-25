#!/usr/bin/env python3
"""
IELTS GenAI Prep Backend Deployment Script
Deploys AWS Lambda functions using boto3 directly (no Serverless Framework required)
"""

import boto3
import json
import zipfile
import os
import sys
from datetime import datetime

# AWS Configuration
AWS_REGION = 'us-east-1'
LAMBDA_ROLE_NAME = 'ielts-lambda-execution-role'
API_GATEWAY_NAME = 'ielts-genai-prep-api'

def create_lambda_role():
    """Create IAM role for Lambda execution"""
    iam = boto3.client('iam', region_name=AWS_REGION)
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Create role
        role_response = iam.create_role(
            RoleName=LAMBDA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Execution role for IELTS GenAI Prep Lambda functions'
        )
        
        # Attach basic Lambda execution policy
        iam.attach_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Attach DynamoDB policy
        dynamodb_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem"
                    ],
                    "Resource": [
                        "arn:aws:dynamodb:us-east-1:*:table/ielts-genai-prep-users",
                        "arn:aws:dynamodb:us-east-1:*:table/ielts-genai-prep-assessments",
                        "arn:aws:dynamodb:us-east-1:*:table/ielts-genai-prep-auth-tokens"
                    ]
                }
            ]
        }
        
        iam.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='DynamoDBAccess',
            PolicyDocument=json.dumps(dynamodb_policy)
        )
        
        # Attach Bedrock policy
        bedrock_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": [
                        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-sonic-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
                    ]
                }
            ]
        }
        
        iam.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='BedrockAccess',
            PolicyDocument=json.dumps(bedrock_policy)
        )
        
        print(f"✅ Created IAM role: {LAMBDA_ROLE_NAME}")
        return role_response['Role']['Arn']
        
    except iam.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        role = iam.get_role(RoleName=LAMBDA_ROLE_NAME)
        print(f"✅ Using existing IAM role: {LAMBDA_ROLE_NAME}")
        return role['Role']['Arn']

def create_deployment_package(function_name):
    """Create deployment package for Lambda function"""
    zip_filename = f"{function_name}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the main function file
        function_file = f"lambda_functions/{function_name}.py"
        if os.path.exists(function_file):
            zipf.write(function_file, f"{function_name}.py")
        
        # Add requirements (boto3 is available by default in Lambda)
        # For production, you'd include other dependencies here
        
    print(f"✅ Created deployment package: {zip_filename}")
    return zip_filename

def deploy_lambda_function(function_name, role_arn, description):
    """Deploy individual Lambda function"""
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    
    # Create deployment package
    zip_file = create_deployment_package(function_name)
    
    # Read the zip file
    with open(zip_file, 'rb') as f:
        zip_content = f.read()
    
    function_config = {
        'FunctionName': f"ielts-{function_name.replace('_', '-')}",
        'Runtime': 'python3.11',
        'Role': role_arn,
        'Handler': f"{function_name}.lambda_handler",
        'Code': {'ZipFile': zip_content},
        'Description': description,
        'Timeout': 30,
        'MemorySize': 512,
        'Environment': {
            'Variables': {
                'DYNAMODB_USERS_TABLE': 'ielts-genai-prep-users',
                'DYNAMODB_ASSESSMENTS_TABLE': 'ielts-genai-prep-assessments',
                'DYNAMODB_TOKENS_TABLE': 'ielts-genai-prep-auth-tokens',
                'JWT_SECRET': 'your-jwt-secret-key-here',
                'STAGE': 'dev'
            }
        }
    }
    
    # Special config for Nova AI handler (needs more memory and time)
    if 'nova_ai' in function_name:
        function_config['Timeout'] = 300  # 5 minutes
        function_config['MemorySize'] = 1024
    
    try:
        # Create function
        response = lambda_client.create_function(**function_config)
        print(f"✅ Created Lambda function: {response['FunctionName']}")
        
    except lambda_client.exceptions.ResourceConflictException:
        # Function exists, update it
        lambda_client.update_function_code(
            FunctionName=function_config['FunctionName'],
            ZipFile=zip_content
        )
        
        lambda_client.update_function_configuration(
            FunctionName=function_config['FunctionName'],
            Runtime=function_config['Runtime'],
            Role=function_config['Role'],
            Handler=function_config['Handler'],
            Description=function_config['Description'],
            Timeout=function_config['Timeout'],
            MemorySize=function_config['MemorySize'],
            Environment=function_config['Environment']
        )
        
        print(f"✅ Updated Lambda function: {function_config['FunctionName']}")
    
    # Clean up zip file
    os.remove(zip_file)
    
    return function_config['FunctionName']

def create_api_gateway():
    """Create API Gateway for the Lambda functions"""
    apigateway = boto3.client('apigateway', region_name=AWS_REGION)
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    
    try:
        # Create REST API
        api_response = apigateway.create_rest_api(
            name=API_GATEWAY_NAME,
            description='IELTS GenAI Prep API Gateway',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        
        api_id = api_response['id']
        print(f"✅ Created API Gateway: {API_GATEWAY_NAME} (ID: {api_id})")
        
    except Exception as e:
        # API might already exist, get existing one
        apis = apigateway.get_rest_apis()
        existing_api = next((api for api in apis['items'] if api['name'] == API_GATEWAY_NAME), None)
        
        if existing_api:
            api_id = existing_api['id']
            print(f"✅ Using existing API Gateway: {API_GATEWAY_NAME} (ID: {api_id})")
        else:
            raise e
    
    # Get root resource
    resources = apigateway.get_resources(restApiId=api_id)
    root_resource_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
    
    # Create /api resource
    try:
        api_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='api'
        )
        api_resource_id = api_resource['id']
        print(f"✅ Created /api resource")
        
    except apigateway.exceptions.ConflictException:
        # Resource exists
        api_resource_id = next(r['id'] for r in resources['items'] if r.get('pathPart') == 'api')
        print(f"✅ Using existing /api resource")
    
    # Create health endpoint
    create_api_endpoint(apigateway, lambda_client, api_id, api_resource_id, 'health', 'GET', 'ielts-auth-handler')
    
    # Deploy API
    deployment = apigateway.create_deployment(
        restApiId=api_id,
        stageName='dev',
        description=f'Deployment at {datetime.now().isoformat()}'
    )
    
    api_url = f"https://{api_id}.execute-api.{AWS_REGION}.amazonaws.com/dev"
    print(f"✅ API deployed at: {api_url}")
    
    return api_id, api_url

def create_api_endpoint(apigateway, lambda_client, api_id, parent_resource_id, path, method, lambda_function_name):
    """Create individual API endpoint"""
    try:
        # Create resource
        resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=parent_resource_id,
            pathPart=path
        )
        resource_id = resource['id']
        
    except apigateway.exceptions.ConflictException:
        # Resource exists, get it
        resources = apigateway.get_resources(restApiId=api_id)
        resource_id = next(r['id'] for r in resources['items'] if r.get('pathPart') == path)
    
    # Create method
    try:
        apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=method,
            authorizationType='NONE'
        )
        
        # Set up integration
        lambda_arn = f"arn:aws:lambda:{AWS_REGION}:*:function:{lambda_function_name}"
        
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        
        # Add Lambda permission
        lambda_client.add_permission(
            FunctionName=lambda_function_name,
            StatementId=f"{lambda_function_name}-{path}-{method}",
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:{AWS_REGION}:*:{api_id}/*/{method}/{path}"
        )
        
        print(f"✅ Created endpoint: {method} /{path}")
        
    except Exception as e:
        print(f"⚠️  Endpoint {method} /{path} might already exist: {str(e)}")

def main():
    """Main deployment function"""
    print("🚀 Starting IELTS GenAI Prep Backend Deployment")
    print("=" * 50)
    
    try:
        # Step 1: Create IAM role
        print("\n📋 Step 1: Creating IAM role...")
        role_arn = create_lambda_role()
        
        # Wait a bit for role to propagate
        import time
        time.sleep(10)
        
        # Step 2: Deploy Lambda functions
        print("\n📋 Step 2: Deploying Lambda functions...")
        
        functions = [
            ('auth_handler', 'Authentication and user management'),
            ('purchase_handler', 'Purchase verification and management'),
            ('nova_ai_handler', 'Nova AI integration for assessments')
        ]
        
        deployed_functions = []
        for func_name, description in functions:
            try:
                function_name = deploy_lambda_function(func_name, role_arn, description)
                deployed_functions.append(function_name)
            except Exception as e:
                print(f"❌ Failed to deploy {func_name}: {str(e)}")
        
        # Step 3: Create API Gateway
        print("\n📋 Step 3: Creating API Gateway...")
        api_id, api_url = create_api_gateway()
        
        # Step 4: Test deployment
        print("\n📋 Step 4: Testing deployment...")
        test_deployment(api_url)
        
        print("\n🎉 Deployment Complete!")
        print("=" * 50)
        print(f"API URL: {api_url}")
        print(f"Health Check: {api_url}/api/health")
        print("\nNext steps:")
        print("1. Update your mobile app with the API URL")
        print("2. Test the authentication flow")
        print("3. Verify purchase verification works")
        print("4. Test Nova AI integration")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        sys.exit(1)

def test_deployment(api_url):
    """Test the deployed API"""
    import requests
    
    try:
        response = requests.get(f"{api_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️  Health check returned status {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Health check failed: {str(e)}")
        print("This might be normal if API Gateway is still propagating")

if __name__ == "__main__":
    main()