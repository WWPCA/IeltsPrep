#!/usr/bin/env python3
"""
Fix CloudFront cache configuration to disable caching temporarily
"""
import boto3
import json

def update_cloudfront_disable_cache():
    """Temporarily disable CloudFront caching to fix forbidden responses"""
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    # Get current distribution config
    response = cloudfront.get_distribution_config(Id='E1EPXAU67877FR')
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Set CachingDisabled policy and remove conflicting parameters
    config['DefaultCacheBehavior']['CachePolicyId'] = '4135ea2d-6df8-44a3-9df3-4b5a84be39ad'  # CachingDisabled policy
    
    # Remove conflicting parameters when using CachePolicyId
    if 'ForwardedValues' in config['DefaultCacheBehavior']:
        del config['DefaultCacheBehavior']['ForwardedValues']
    if 'MinTTL' in config['DefaultCacheBehavior']:
        del config['DefaultCacheBehavior']['MinTTL']
    if 'DefaultTTL' in config['DefaultCacheBehavior']:
        del config['DefaultCacheBehavior']['DefaultTTL']
    if 'MaxTTL' in config['DefaultCacheBehavior']:
        del config['DefaultCacheBehavior']['MaxTTL']
    
    print("Updating CloudFront distribution to disable caching...")
    
    # Update the distribution
    update_response = cloudfront.update_distribution(
        Id='E1EPXAU67877FR',
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print(f"CloudFront update initiated. Status: {update_response['Distribution']['Status']}")
    print("Cache disabled - all requests will go directly to origin")
    return True

if __name__ == "__main__":
    update_cloudfront_disable_cache()