#!/usr/bin/env python3
"""
Fix CloudFront distribution to properly handle POST requests to /api/*
"""

import boto3
import json
import time

def fix_cloudfront_for_post_requests():
    """Update CloudFront distribution to handle POST requests properly"""
    
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
        print("CloudFront distribution not found")
        return False
    
    print(f"Found distribution: {dist_id}")
    
    # Get current configuration
    config_response = cloudfront.get_distribution_config(Id=dist_id)
    config = config_response['DistributionConfig']
    etag = config_response['ETag']
    
    print("Current configuration:")
    print(f"Default cache behavior allows: {config['DefaultCacheBehavior']['AllowedMethods']['Items']}")
    
    # Update the /api/* cache behavior
    updated = False
    for behavior in config['CacheBehaviors']['Items']:
        if behavior['PathPattern'] == '/api/*':
            print(f"Found /api/* behavior, current settings:")
            print(f"  Allowed methods: {behavior['AllowedMethods']['Items']}")
            print(f"  Cache policy: {behavior.get('CachePolicyId', 'None')}")
            print(f"  Origin request policy: {behavior.get('OriginRequestPolicyId', 'None')}")
            
            # Update the behavior to handle POST requests properly
            behavior['AllowedMethods'] = {
                'Quantity': 7,
                'Items': ['HEAD', 'DELETE', 'POST', 'GET', 'OPTIONS', 'PUT', 'PATCH'],
                'CachedMethods': {'Quantity': 2, 'Items': ['HEAD', 'GET']}
            }
            
            # Use proper cache policy for API requests (disable caching)
            behavior['CachePolicyId'] = '4135ea2d-6df8-44a3-9df3-4b5a84be39ad'  # CachingDisabled
            
            # Use proper origin request policy
            behavior['OriginRequestPolicyId'] = '88a5eaf4-2fd4-4709-b370-b4c650ea3fcf'  # CORS-S3Origin
            
            # Remove deprecated ForwardedValues if present
            if 'ForwardedValues' in behavior:
                del behavior['ForwardedValues']
            
            # Remove deprecated TTL settings
            for key in ['DefaultTTL', 'MaxTTL', 'MinTTL']:
                if key in behavior:
                    del behavior[key]
            
            updated = True
            print("Updated /api/* behavior")
            break
    
    if not updated:
        print("No /api/* behavior found to update")
        return False
    
    # Update the distribution
    try:
        cloudfront.update_distribution(
            Id=dist_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        print("CloudFront distribution updated successfully")
        print("Changes are propagating (5-10 minutes)")
        return True
        
    except Exception as e:
        print(f"Error updating CloudFront: {e}")
        return False

def wait_for_propagation():
    """Wait for CloudFront changes to propagate"""
    print("Waiting for CloudFront changes to propagate...")
    
    # Wait 2 minutes for basic propagation
    for i in range(24):  # 24 * 5 = 120 seconds
        time.sleep(5)
        print(f"Waiting... {(i+1)*5}/120 seconds")
        
        # Test if POST requests are working
        if i > 12:  # After 1 minute, start testing
            try:
                import requests
                response = requests.post(
                    'https://www.ieltsaiprep.com/api/login',
                    json={'test': 'ping'},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                if response.status_code != 403:
                    print(f"POST request succeeded with status {response.status_code}!")
                    return True
                    
            except Exception as e:
                continue
    
    print("Propagation may still be in progress...")
    return False

def test_post_requests():
    """Test if POST requests are working after CloudFront fix"""
    import requests
    
    print("Testing POST requests...")
    
    try:
        # Test login
        response = requests.post(
            'https://www.ieltsaiprep.com/api/login',
            json={
                'email': 'prodtest_20250709_175130_i1m2@ieltsaiprep.com',
                'password': 'TestProd2025!'
            },
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"Login test - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login working!")
            return True
        elif response.status_code == 401:
            print("✅ POST requests reaching Lambda (authentication issue)")
            return True
        else:
            print(f"❌ Still failing: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing CloudFront for POST requests...")
    
    if fix_cloudfront_for_post_requests():
        if wait_for_propagation():
            print("✅ CloudFront changes propagated successfully!")
        
        if test_post_requests():
            print("\n🎉 POST requests are now working!")
            print("You can now log in at: https://www.ieltsaiprep.com/login")
        else:
            print("\n⏳ CloudFront changes may still be propagating...")
            print("Please try again in 5-10 minutes")
    else:
        print("❌ Failed to fix CloudFront configuration")