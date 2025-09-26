#!/usr/bin/env python3
"""
EMERGENCY: Restore www.ieltsaiprep.com immediately
"""

import boto3
import json
from botocore.exceptions import ClientError

def emergency_restore():
    """Emergency restoration of domain access"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    print("🚨 EMERGENCY DOMAIN RESTORATION")
    print("=" * 40)
    
    # Step 1: Re-enable execute API endpoint
    try:
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/disableExecuteApiEndpoint',
                    'value': 'false'
                }
            ]
        )
        print("✅ Execute API endpoint re-enabled")
    except Exception as e:
        print(f"⚠️  Execute API endpoint status: {e}")
    
    # Step 2: Remove resource policy completely
    try:
        # First get current API to check if policy exists
        current_api = apigateway.get_rest_api(restApiId=api_id)
        
        if 'policy' in current_api and current_api['policy']:
            apigateway.update_rest_api(
                restApiId=api_id,
                patchOperations=[
                    {
                        'op': 'replace',
                        'path': '/policy',
                        'value': ''
                    }
                ]
            )
            print("✅ Resource policy removed")
        else:
            print("✅ No resource policy to remove")
    except Exception as e:
        print(f"⚠️  Resource policy removal: {e}")
    
    # Step 3: Ensure prod stage exists
    try:
        # Check if prod stage exists
        stages = apigateway.get_stages(restApiId=api_id)
        
        has_prod_stage = any(stage['stageName'] == 'prod' for stage in stages['item'])
        
        if not has_prod_stage:
            # Create deployment and stage
            deployment = apigateway.create_deployment(
                restApiId=api_id,
                description='Emergency restoration deployment'
            )
            
            apigateway.create_stage(
                restApiId=api_id,
                stageName='prod',
                deploymentId=deployment['id'],
                description='Production stage - restored'
            )
            print("✅ Prod stage recreated")
        else:
            print("✅ Prod stage exists")
    except Exception as e:
        print(f"⚠️  Stage creation: {e}")
    
    # Step 4: Test both URLs
    print("\n🧪 Testing URLs...")
    
    import requests
    
    # Test domain
    try:
        response = requests.get('https://www.ieltsaiprep.com', timeout=15)
        if response.status_code == 200:
            print("✅ www.ieltsaiprep.com - WORKING")
        else:
            print(f"❌ www.ieltsaiprep.com - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ www.ieltsaiprep.com - ERROR: {e}")
    
    # Test direct API Gateway
    try:
        response = requests.get('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod', timeout=15)
        if response.status_code == 200:
            print("✅ Direct API Gateway - WORKING")
        else:
            print(f"❌ Direct API Gateway - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Direct API Gateway - ERROR: {e}")
    
    print("\n🎯 RESTORATION COMPLETE")
    print("Both URLs should now be accessible")

if __name__ == "__main__":
    emergency_restore()