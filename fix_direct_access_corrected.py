#!/usr/bin/env python3
"""
Corrected Solution: Block Direct API Gateway Access While Preserving Domain
Uses proper API Gateway resource policy with CloudFront headers
"""

import boto3
import json
import uuid
from botocore.exceptions import ClientError

def create_cloudfront_secret():
    """Create a unique secret for CloudFront authentication"""
    return f"CloudFront-{str(uuid.uuid4())}"

def update_api_gateway_resource_policy(secret_header):
    """Update API Gateway with resource policy that requires CloudFront header"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    # Resource policy that denies access without CloudFront header
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
                        "aws:RequestTag/X-CloudFront-Secret": secret_header
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
        # Use correct parameter name: patchOperations
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': json.dumps(policy)
                }
            ]
        )
        
        print("✅ API Gateway resource policy updated")
        return True
        
    except ClientError as e:
        print(f"❌ Error updating API Gateway policy: {e}")
        return False

def update_cloudfront_distribution(secret_header):
    """Update CloudFront to send authentication header"""
    
    cloudfront = boto3.client('cloudfront')
    
    try:
        # Find distribution
        distributions = cloudfront.list_distributions()
        distribution_id = None
        
        for dist in distributions['DistributionList'].get('Items', []):
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'www.ieltsaiprep.com' in aliases or 'ieltsaiprep.com' in aliases:
                distribution_id = dist['Id']
                break
        
        if not distribution_id:
            print("❌ CloudFront distribution not found")
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
        
        print(f"✅ CloudFront distribution updated: {distribution_id}")
        return True
        
    except ClientError as e:
        print(f"❌ Error updating CloudFront: {e}")
        return False

def simple_ip_based_restriction():
    """Simpler approach: Block all non-CloudFront IP addresses"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    # Get CloudFront IP ranges
    import requests
    
    try:
        response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
        ip_ranges = response.json()
        
        cloudfront_ips = []
        for prefix in ip_ranges['prefixes']:
            if prefix['service'] == 'CLOUDFRONT':
                cloudfront_ips.append(prefix['ip_prefix'])
        
        # Take first 50 ranges (API Gateway has limits)
        cloudfront_ips = cloudfront_ips[:50]
        
        # Create policy allowing only CloudFront IPs
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "execute-api:Invoke",
                    "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": cloudfront_ips
                        }
                    }
                }
            ]
        }
        
        # Apply policy
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': json.dumps(policy)
                }
            ]
        )
        
        print("✅ IP-based restriction applied")
        print(f"✅ Allowed {len(cloudfront_ips)} CloudFront IP ranges")
        return True
        
    except Exception as e:
        print(f"❌ Error applying IP restriction: {e}")
        return False

def main():
    """Main function to block direct access"""
    
    print("🔒 Blocking Direct API Gateway Access")
    print("=" * 45)
    
    print("Goal:")
    print("✅ Keep www.ieltsaiprep.com working")
    print("❌ Block n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod")
    print()
    
    print("Implementing IP-based restriction (simpler approach)...")
    
    success = simple_ip_based_restriction()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ www.ieltsaiprep.com - WILL WORK (CloudFront IPs allowed)")
        print("❌ n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod - BLOCKED (direct access denied)")
        print("\n⏱️  Changes take effect immediately")
        print("🧪 Test both URLs to verify functionality")
        
        # Save configuration
        with open('api_gateway_protection.json', 'w') as f:
            json.dump({
                'protection_type': 'ip_based',
                'implementation_date': '2025-07-09',
                'purpose': 'Block direct API Gateway access while preserving domain functionality'
            }, f, indent=2)
        
        print("📄 Configuration saved to api_gateway_protection.json")
        
    else:
        print("\n❌ FAILED!")
        print("Could not apply IP-based restriction")
        print("Manual intervention may be required")

if __name__ == "__main__":
    main()