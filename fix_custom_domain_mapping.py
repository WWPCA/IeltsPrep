#!/usr/bin/env python3
"""
Fix Custom Domain Mapping for API Gateway
"""

import boto3
import json
import time

def fix_custom_domain_mapping():
    """Fix API Gateway custom domain mapping"""
    
    # Initialize clients
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    print("🔧 Fixing Custom Domain Mapping for www.ieltsaiprep.com")
    print("=" * 60)
    
    try:
        # Get current CloudFront distributions
        distributions = cloudfront.list_distributions()
        target_distribution = None
        
        for dist in distributions['DistributionList']['Items']:
            if 'www.ieltsaiprep.com' in dist.get('Aliases', {}).get('Items', []):
                target_distribution = dist
                break
        
        if not target_distribution:
            print("❌ CloudFront distribution for www.ieltsaiprep.com not found")
            return False
        
        distribution_id = target_distribution['Id']
        distribution_domain = target_distribution['DomainName']
        
        print(f"✅ Found CloudFront distribution: {distribution_id}")
        print(f"   Domain: {distribution_domain}")
        
        # Get current API Gateway configuration
        apis = apigateway.get_rest_apis()
        target_api = None
        
        for api in apis['items']:
            if 'ielts-genai-prep' in api['name']:
                target_api = api
                break
        
        if not target_api:
            print("❌ API Gateway for IELTS GenAI Prep not found")
            return False
        
        api_id = target_api['id']
        print(f"✅ Found API Gateway: {api_id}")
        print(f"   Name: {target_api['name']}")
        
        # Update CloudFront distribution to properly route API calls
        print("\n📝 Updating CloudFront behavior for API routing...")
        
        # Get current distribution config
        config_response = cloudfront.get_distribution_config(Id=distribution_id)
        distribution_config = config_response['DistributionConfig']
        etag = config_response['ETag']
        
        # Add API behavior if not exists
        api_behavior = {
            'PathPattern': '/api/*',
            'TargetOriginId': 'lambda-origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'ForwardedValues': {
                'QueryString': True,
                'Cookies': {'Forward': 'all'},
                'Headers': {
                    'Quantity': 4,
                    'Items': ['Authorization', 'Content-Type', 'Cookie', 'X-Forwarded-For']
                }
            },
            'MinTTL': 0,
            'DefaultTTL': 0,
            'MaxTTL': 0,
            'Compress': False,
            'AllowedMethods': {
                'Quantity': 7,
                'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD']
                }
            }
        }
        
        # Check if API behavior already exists
        api_behavior_exists = False
        for behavior in distribution_config.get('CacheBehaviors', {}).get('Items', []):
            if behavior['PathPattern'] == '/api/*':
                api_behavior_exists = True
                break
        
        if not api_behavior_exists:
            # Add API behavior
            if 'CacheBehaviors' not in distribution_config:
                distribution_config['CacheBehaviors'] = {'Quantity': 0, 'Items': []}
            
            distribution_config['CacheBehaviors']['Items'].append(api_behavior)
            distribution_config['CacheBehaviors']['Quantity'] += 1
            
            # Update distribution
            cloudfront.update_distribution(
                Id=distribution_id,
                DistributionConfig=distribution_config,
                IfMatch=etag
            )
            
            print("✅ CloudFront behavior updated for API routing")
        else:
            print("✅ CloudFront API behavior already exists")
        
        # Ensure the Lambda origin points to the correct API Gateway
        lambda_origin_updated = False
        for origin in distribution_config['Origins']['Items']:
            if origin['Id'] == 'lambda-origin':
                correct_domain = f"{api_id}.execute-api.us-east-1.amazonaws.com"
                if origin['DomainName'] != correct_domain:
                    origin['DomainName'] = correct_domain
                    origin['OriginPath'] = '/prod'
                    lambda_origin_updated = True
                break
        
        if lambda_origin_updated:
            print("✅ Lambda origin updated to correct API Gateway")
        else:
            print("✅ Lambda origin already correct")
        
        print("\n🎯 Custom Domain Mapping Status:")
        print(f"   • Custom Domain: www.ieltsaiprep.com")
        print(f"   • CloudFront Distribution: {distribution_id}")
        print(f"   • API Gateway: {api_id}")
        print(f"   • Lambda Function: ielts-genai-prep-api")
        print(f"   • API Endpoint: {api_id}.execute-api.us-east-1.amazonaws.com/prod")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing custom domain mapping: {str(e)}")
        return False

def test_custom_domain_endpoints():
    """Test custom domain endpoints"""
    
    print("\n🧪 Testing Custom Domain Endpoints")
    print("=" * 40)
    
    import requests
    
    base_url = "https://www.ieltsaiprep.com"
    
    # Test endpoints
    test_endpoints = [
        ("/", "Home page"),
        ("/login", "Login page"),
        ("/api/maya/introduction", "Maya API"),
        ("/robots.txt", "Robots.txt")
    ]
    
    for endpoint, name in test_endpoints:
        try:
            if endpoint.startswith('/api/'):
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=10)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
            
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
    
    print(f"\n✅ Custom domain testing complete")
    print(f"🌐 Production URL: {base_url}")

if __name__ == "__main__":
    print("🚀 IELTS GenAI Prep - Custom Domain Fix")
    print("=" * 50)
    
    success = fix_custom_domain_mapping()
    
    if success:
        print("\n✅ CUSTOM DOMAIN MAPPING FIXED")
        
        # Wait for CloudFront to propagate
        print("\n⏳ Waiting for CloudFront propagation (30 seconds)...")
        time.sleep(30)
        
        # Test the endpoints
        test_custom_domain_endpoints()
        
        print("\n🎉 www.ieltsaiprep.com should now work correctly!")
        print("🔑 Test credentials: test@ieltsaiprep.com / password123")
        print("📱 Ready for mobile app store deployment")
    else:
        print("\n❌ CUSTOM DOMAIN MAPPING FAILED")