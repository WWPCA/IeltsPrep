"""
AWS Lambda Deployment Script for IELTS GenAI Prep
Deploys to multiple regions with proper Nova Sonic routing
"""

import boto3
import json
import zipfile
import os
import time
from typing import List, Dict

class LambdaDeployer:
    """Handles multi-region Lambda deployment"""
    
    def __init__(self):
        self.regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']
        self.function_name = 'ielts-genai-prep'
        self.runtime = 'python3.11'
        self.handler = 'lambda_app.lambda_handler'
        
    def create_deployment_package(self) -> str:
        """Create deployment ZIP package"""
        zip_filename = 'lambda_deployment.zip'
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add main application files
            zipf.write('lambda_app.py')
            zipf.write('regional_router.py')
            zipf.write('app_store_payments.py')
            
            # Add dependencies (would normally use layer)
            # For now, assume dependencies are installed in site-packages
            
        return zip_filename
    
    def deploy_to_region(self, region: str, zip_file: str) -> Dict:
        """Deploy Lambda function to specific region"""
        lambda_client = boto3.client('lambda', region_name=region)
        
        try:
            # Read deployment package
            with open(zip_file, 'rb') as f:
                zip_content = f.read()
            
            # Environment variables for Lambda
            environment = {
                'Variables': {
                    'AWS_REGION': region,
                    'DYNAMODB_TABLE': f'IELTSUsers-prod',
                    'ASSESSMENTS_TABLE': f'IELTSAssessments-prod',
                    'ELASTICACHE_ENDPOINT': os.environ.get('ELASTICACHE_ENDPOINT', ''),
                    'FLASK_SECRET_KEY': os.environ.get('FLASK_SECRET_KEY', 'your-secret-key'),
                    'APPLE_SHARED_SECRET': os.environ.get('APPLE_SHARED_SECRET', ''),
                    'GOOGLE_SERVICE_ACCOUNT_JSON': os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '{}')
                }
            }
            
            # Try to update existing function first
            try:
                response = lambda_client.update_function_code(
                    FunctionName=self.function_name,
                    ZipFile=zip_content
                )
                print(f"Updated function in {region}")
                
                # Update environment variables
                lambda_client.update_function_configuration(
                    FunctionName=self.function_name,
                    Environment=environment,
                    Timeout=60 if region == 'us-east-1' else 30,  # Extended timeout for Nova Sonic
                    MemorySize=2048 if region == 'us-east-1' else 1024
                )
                
            except lambda_client.exceptions.ResourceNotFoundException:
                # Create new function
                response = lambda_client.create_function(
                    FunctionName=self.function_name,
                    Runtime=self.runtime,
                    Role=f'arn:aws:iam::{boto3.client("sts").get_caller_identity()["Account"]}:role/lambda-execution-role',
                    Handler=self.handler,
                    Code={'ZipFile': zip_content},
                    Environment=environment,
                    Timeout=60 if region == 'us-east-1' else 30,
                    MemorySize=2048 if region == 'us-east-1' else 1024,
                    Publish=True
                )
                print(f"Created function in {region}")
            
            return {
                'region': region,
                'function_arn': response.get('FunctionArn'),
                'status': 'success'
            }
            
        except Exception as e:
            print(f"Deployment failed in {region}: {e}")
            return {
                'region': region,
                'error': str(e),
                'status': 'failed'
            }
    
    def setup_api_gateway(self, region: str, lambda_arn: str) -> str:
        """Set up API Gateway for Lambda function"""
        api_client = boto3.client('apigateway', region_name=region)
        
        try:
            # Create REST API
            api_response = api_client.create_rest_api(
                name=f'ielts-api-{region}',
                description=f'IELTS GenAI Prep API for {region}',
                endpointConfiguration={'types': ['REGIONAL']}
            )
            
            api_id = api_response['id']
            
            # Get root resource
            resources = api_client.get_resources(restApiId=api_id)
            root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
            
            # Create proxy resource
            proxy_resource = api_client.create_resource(
                restApiId=api_id,
                parentId=root_id,
                pathPart='{proxy+}'
            )
            
            # Create ANY method on proxy resource
            api_client.put_method(
                restApiId=api_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                authorizationType='NONE'
            )
            
            # Set up Lambda integration
            integration_uri = f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
            
            api_client.put_integration(
                restApiId=api_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=integration_uri
            )
            
            # Deploy API
            api_client.create_deployment(
                restApiId=api_id,
                stageName='prod'
            )
            
            # Add Lambda permission for API Gateway
            lambda_client = boto3.client('lambda', region_name=region)
            lambda_client.add_permission(
                FunctionName=self.function_name,
                StatementId=f'apigateway-{region}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:{region}:*:{api_id}/*/*'
            )
            
            api_url = f'https://{api_id}.execute-api.{region}.amazonaws.com/prod'
            print(f"API Gateway deployed in {region}: {api_url}")
            
            return api_url
            
        except Exception as e:
            print(f"API Gateway setup failed in {region}: {e}")
            return ""
    
    def deploy_all_regions(self) -> Dict:
        """Deploy to all regions and set up routing"""
        zip_file = self.create_deployment_package()
        results = {}
        api_endpoints = {}
        
        for region in self.regions:
            print(f"Deploying to {region}...")
            result = self.deploy_to_region(region, zip_file)
            results[region] = result
            
            if result['status'] == 'success':
                api_url = self.setup_api_gateway(region, result['function_arn'])
                if api_url:
                    api_endpoints[region] = api_url
            
            time.sleep(5)  # Avoid rate limits
        
        # Clean up deployment package
        os.remove(zip_file)
        
        # Update Route 53 for regional routing
        self.setup_route53_routing(api_endpoints)
        
        return {
            'deployment_results': results,
            'api_endpoints': api_endpoints,
            'nova_sonic_endpoint': api_endpoints.get('us-east-1', '')
        }
    
    def setup_route53_routing(self, api_endpoints: Dict) -> None:
        """Set up Route 53 for regional routing"""
        route53 = boto3.client('route53')
        
        try:
            # This would set up latency-based routing
            # For now, just print the configuration needed
            print("\nRoute 53 Configuration Needed:")
            print("Create latency-based routing records:")
            
            for region, endpoint in api_endpoints.items():
                print(f"  {region}: {endpoint}")
            
            print(f"\nNova Sonic (fixed to us-east-1): {api_endpoints.get('us-east-1', 'Not deployed')}")
            
        except Exception as e:
            print(f"Route 53 setup info: {e}")

def main():
    deployer = LambdaDeployer()
    results = deployer.deploy_all_regions()
    
    print("\n" + "="*50)
    print("DEPLOYMENT SUMMARY")
    print("="*50)
    
    for region, result in results['deployment_results'].items():
        status = result['status']
        print(f"{region}: {status}")
        if status == 'failed':
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    print(f"\nAPI Endpoints:")
    for region, endpoint in results['api_endpoints'].items():
        print(f"  {region}: {endpoint}")
    
    print(f"\nNova Sonic Endpoint (us-east-1 only):")
    print(f"  {results['nova_sonic_endpoint']}")

if __name__ == "__main__":
    main()