#!/usr/bin/env python3
"""
Fix CloudFront distribution to properly route API requests to Lambda
"""
import boto3
import json

def fix_cloudfront_api_routing():
    """Update CloudFront to properly route /api/* requests"""
    
    cloudfront_client = boto3.client('cloudfront', region_name='us-east-1')
    distribution_id = 'E1EPXAU67877FR'
    
    try:
        # Get current distribution configuration
        response = cloudfront_client.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        print("Current distribution configuration retrieved")
        
        # Add cache behavior for /api/* paths
        api_cache_behavior = {
            'PathPattern': '/api/*',
            'TargetOriginId': 'ielts-genai-prep-api-gateway',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 7,
                'Items': ['HEAD', 'DELETE', 'POST', 'GET', 'OPTIONS', 'PUT', 'PATCH'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['HEAD', 'GET']
                }
            },
            'Compress': True,
            'ForwardedValues': {
                'QueryString': True,
                'Cookies': {'Forward': 'all'},
                'Headers': {
                    'Quantity': 4,
                    'Items': ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
                }
            },
            'MinTTL': 0,
            'DefaultTTL': 0,
            'MaxTTL': 0,
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            }
        }
        
        # Check if API cache behavior already exists
        api_behavior_exists = False
        for behavior in config.get('CacheBehaviors', {}).get('Items', []):
            if behavior.get('PathPattern') == '/api/*':
                api_behavior_exists = True
                print("API cache behavior already exists")
                break
        
        if not api_behavior_exists:
            # Add the API cache behavior
            if 'CacheBehaviors' not in config:
                config['CacheBehaviors'] = {'Quantity': 0, 'Items': []}
            
            config['CacheBehaviors']['Items'].append(api_cache_behavior)
            config['CacheBehaviors']['Quantity'] = len(config['CacheBehaviors']['Items'])
            
            print("Adding API cache behavior for /api/* paths")
        
        # Update default cache behavior to disable caching for dynamic content
        config['DefaultCacheBehavior']['MinTTL'] = 0
        config['DefaultCacheBehavior']['DefaultTTL'] = 0
        config['DefaultCacheBehavior']['MaxTTL'] = 86400
        
        # Ensure all HTTP methods are allowed on default behavior
        config['DefaultCacheBehavior']['AllowedMethods'] = {
            'Quantity': 7,
            'Items': ['HEAD', 'DELETE', 'POST', 'GET', 'OPTIONS', 'PUT', 'PATCH'],
            'CachedMethods': {
                'Quantity': 2,
                'Items': ['HEAD', 'GET']
            }
        }
        
        # Forward all headers for API requests
        config['DefaultCacheBehavior']['ForwardedValues'] = {
            'QueryString': True,
            'Cookies': {'Forward': 'all'},
            'Headers': {
                'Quantity': 6,
                'Items': ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin', 'User-Agent']
            }
        }
        
        print("Updating CloudFront distribution...")
        
        # Update the distribution
        update_response = cloudfront_client.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"Distribution update initiated. Status: {update_response['Distribution']['Status']}")
        print("CloudFront is propagating changes globally (this takes 15-20 minutes)")
        print("API requests should work properly once propagation completes")
        
        return True
        
    except Exception as e:
        print(f"Error updating CloudFront: {e}")
        return False

if __name__ == "__main__":
    fix_cloudfront_api_routing()