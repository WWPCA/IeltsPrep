#!/usr/bin/env python3
"""
Simple CloudFront cache invalidation to fix API routing
"""
import boto3

def invalidate_cloudfront_cache():
    """Create invalidation for /api/* paths"""
    
    cloudfront_client = boto3.client('cloudfront', region_name='us-east-1')
    distribution_id = 'E1EPXAU67877FR'
    
    try:
        # Create cache invalidation for API paths
        response = cloudfront_client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 2,
                    'Items': [
                        '/api/*',
                        '/api/login'
                    ]
                },
                'CallerReference': f'api-fix-{int(time.time())}'
            }
        )
        
        print(f"Cache invalidation created: {response['Invalidation']['Id']}")
        print("API routes should work in 3-5 minutes after cache clears")
        return True
        
    except Exception as e:
        print(f"Invalidation failed: {e}")
        return False

if __name__ == "__main__":
    import time
    invalidate_cloudfront_cache()