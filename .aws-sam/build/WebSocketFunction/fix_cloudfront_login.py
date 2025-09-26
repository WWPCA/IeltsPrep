#!/usr/bin/env python3
"""
Fix CloudFront configuration to allow login API calls
"""

import boto3
import json

def fix_cloudfront_api_access():
    """Update CloudFront to properly handle API requests"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    # Find the distribution
    distributions = cloudfront.list_distributions()
    dist_id = None
    
    for dist in distributions['DistributionList']['Items']:
        aliases = dist.get('Aliases', {}).get('Items', [])
        if any('ieltsaiprep.com' in alias for alias in aliases):
            dist_id = dist['Id']
            break
    
    if not dist_id:
        print("❌ CloudFront distribution not found")
        return False
    
    print(f"Found distribution: {dist_id}")
    
    # Get current configuration
    config_response = cloudfront.get_distribution_config(Id=dist_id)
    config = config_response['DistributionConfig']
    etag = config_response['ETag']
    
    # Update cache behaviors for API endpoints
    if 'CacheBehaviors' not in config:
        config['CacheBehaviors'] = {'Quantity': 0, 'Items': []}
    
    # Find existing API behavior or create new one
    api_behavior_exists = False
    for behavior in config['CacheBehaviors']['Items']:
        if behavior.get('PathPattern') == '/api/*':
            api_behavior_exists = True
            # Update existing behavior
            behavior['CachePolicyId'] = '4135ea2d-6df8-44a3-9df3-4b5a84be39ad'  # CachingDisabled
            behavior['OriginRequestPolicyId'] = '88a5eaf4-2fd4-4709-b370-b4c650ea3fcf'  # CORS-S3Origin
            behavior['ViewerProtocolPolicy'] = 'redirect-to-https'
            behavior['AllowedMethods'] = {
                'Quantity': 7,
                'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']}
            }
            print("✅ Updated existing API behavior")
            break
    
    if not api_behavior_exists:
        # Create new API behavior
        new_behavior = {
            'PathPattern': '/api/*',
            'TargetOriginId': config['Origins']['Items'][0]['Id'],
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 7,
                'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']}
            },
            'ForwardedValues': {
                'QueryString': True,
                'Cookies': {'Forward': 'all'},
                'Headers': {'Quantity': 1, 'Items': ['*']}
            },
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'MinTTL': 0,
            'DefaultTTL': 0,
            'MaxTTL': 0,
            'Compress': False
        }
        
        config['CacheBehaviors']['Items'].append(new_behavior)
        config['CacheBehaviors']['Quantity'] += 1
        print("✅ Created new API behavior")
    
    # Update the distribution
    try:
        cloudfront.update_distribution(
            Id=dist_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        print("✅ CloudFront distribution updated successfully")
        print("⏳ Changes are propagating (may take 10-15 minutes)")
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront: {e}")
        return False

def test_login_after_fix():
    """Test login after CloudFront fix"""
    import requests
    import time
    
    print("\n🧪 Testing login after CloudFront fix...")
    
    # Wait a moment for changes to propagate
    time.sleep(5)
    
    try:
        response = requests.post(
            'https://www.ieltsaiprep.com/api/login',
            json={
                'email': 'prodtest_20250709_175130_i1m2@ieltsaiprep.com',
                'password': 'TestProd2025!',
                'g-recaptcha-response': 'bypassed'
            },
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 302:
            print("✅ Login successful!")
        elif response.status_code == 200:
            print("✅ Login response received")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    print("🔧 Fixing CloudFront configuration for API access...")
    
    if fix_cloudfront_api_access():
        test_login_after_fix()
        print("\n✅ CloudFront updated. Try logging in at https://www.ieltsaiprep.com/login")
        print("Credentials: prodtest_20250709_175130_i1m2@ieltsaiprep.com / TestProd2025!")
    else:
        print("❌ Failed to update CloudFront configuration")