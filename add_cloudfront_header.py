#!/usr/bin/env python3
"""
Add the CloudFront secret header to the distribution configuration
"""

import boto3
import json

def add_cloudfront_header():
    """Add X-CloudFront-Secret header to CloudFront distribution"""
    
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
    
    # Add custom header to origin
    origin = config['Origins']['Items'][0]
    
    if 'CustomHeaders' not in origin:
        origin['CustomHeaders'] = {'Quantity': 0, 'Items': []}
    
    # Check if header already exists
    header_exists = False
    for header in origin['CustomHeaders']['Items']:
        if header['HeaderName'] == 'X-CloudFront-Secret':
            header_exists = True
            print("Header already exists")
            break
    
    if not header_exists:
        # Add the secret header
        new_header = {
            'HeaderName': 'X-CloudFront-Secret',
            'HeaderValue': 'CF-Secret-3140348d'
        }
        
        origin['CustomHeaders']['Items'].append(new_header)
        origin['CustomHeaders']['Quantity'] += 1
        
        print("Added X-CloudFront-Secret header")
    
    # Update the distribution
    try:
        cloudfront.update_distribution(
            Id=dist_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        print("CloudFront distribution updated successfully")
        print("Changes are propagating (may take 10-15 minutes)")
        return True
        
    except Exception as e:
        print(f"Error updating CloudFront: {e}")
        return False

def test_after_header_addition():
    """Test login after adding CloudFront header"""
    import requests
    import time
    
    print("\nTesting after header addition...")
    
    # Wait for propagation
    time.sleep(10)
    
    try:
        response = requests.post(
            'https://www.ieltsaiprep.com/api/login',
            json={
                'email': 'prodtest_20250709_175130_i1m2@ieltsaiprep.com',
                'password': 'TestProd2025!'
            },
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Login successful!")
        else:
            print(f"Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Login test error: {e}")

if __name__ == "__main__":
    print("Adding CloudFront secret header...")
    
    if add_cloudfront_header():
        test_after_header_addition()
        print("\nCloudFront updated. Login should work at https://www.ieltsaiprep.com/login")
    else:
        print("Failed to update CloudFront configuration")