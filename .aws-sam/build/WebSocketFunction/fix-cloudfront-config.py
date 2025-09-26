#!/usr/bin/env python3
"""
Fix CloudFront configuration to allow all HTTP methods
"""
import json
import boto3
import sys

def update_cloudfront_config():
    """Update CloudFront to allow all HTTP methods"""
    
    # Load current config
    with open('current-distribution-config.json', 'r') as f:
        response = json.load(f)
    
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Update default cache behavior to allow all methods
    config['DefaultCacheBehavior']['AllowedMethods'] = {
        "Quantity": 7,
        "Items": ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
        "CachedMethods": {
            "Quantity": 2,
            "Items": ["HEAD", "GET"]
        }
    }
    
    # Update API cache behavior to allow all methods
    for behavior in config['CacheBehaviors']['Items']:
        if behavior['PathPattern'] == '/api/*':
            behavior['AllowedMethods'] = {
                "Quantity": 7,
                "Items": ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
                "CachedMethods": {
                    "Quantity": 2,
                    "Items": ["HEAD", "GET"]
                }
            }
    
    # Save updated config - just the DistributionConfig part
    with open('updated-distribution-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("CloudFront configuration updated to allow all HTTP methods")
    return config, etag

if __name__ == "__main__":
    update_cloudfront_config()