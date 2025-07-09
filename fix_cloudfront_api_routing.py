#!/usr/bin/env python3
"""
Fix CloudFront API Routing for www.ieltsaiprep.com
"""

import boto3
import json
import time

def fix_cloudfront_api_routing():
    """Fix CloudFront distribution to properly route API calls"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    print("🔧 Fixing CloudFront API Routing for www.ieltsaiprep.com")
    print("=" * 60)
    
    # Working API Gateway details
    WORKING_API_ID = "n0cpf1rmvc"
    WORKING_DOMAIN = f"{WORKING_API_ID}.execute-api.us-east-1.amazonaws.com"
    
    try:
        # Get CloudFront distribution for www.ieltsaiprep.com
        distributions = cloudfront.list_distributions()
        target_distribution = None
        
        for dist in distributions['DistributionList']['Items']:
            if 'www.ieltsaiprep.com' in dist.get('Aliases', {}).get('Items', []):
                target_distribution = dist
                break
        
        if not target_distribution:
            print("❌ CloudFront distribution not found")
            return False
        
        distribution_id = target_distribution['Id']
        print(f"✅ Found distribution: {distribution_id}")
        
        # Get current configuration
        config_response = cloudfront.get_distribution_config(Id=distribution_id)
        config = config_response['DistributionConfig']
        etag = config_response['ETag']
        
        print(f"📋 Current Origins: {len(config['Origins']['Items'])}")
        print(f"📋 Current Behaviors: {len(config.get('CacheBehaviors', {}).get('Items', []))}")
        
        # Update lambda origin
        lambda_origin_found = False
        for origin in config['Origins']['Items']:
            if origin['Id'] == 'lambda-origin':
                print(f"🔧 Updating lambda origin: {origin['DomainName']} -> {WORKING_DOMAIN}")
                origin['DomainName'] = WORKING_DOMAIN
                origin['OriginPath'] = '/prod'
                
                # Ensure proper origin configuration
                origin['CustomOriginConfig'] = {
                    'HTTPPort': 443,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'https-only',
                    'OriginSslProtocols': {
                        'Quantity': 3,
                        'Items': ['TLSv1.2', 'TLSv1.1', 'TLSv1']
                    }
                }
                lambda_origin_found = True
                break
        
        if not lambda_origin_found:
            print("❌ Lambda origin not found")
            return False
        
        # Ensure proper API behavior exists
        if 'CacheBehaviors' not in config:
            config['CacheBehaviors'] = {'Quantity': 0, 'Items': []}
        
        # Check if API behavior exists
        api_behavior_exists = False
        for behavior in config['CacheBehaviors']['Items']:
            if behavior['PathPattern'] == '/api/*':
                api_behavior_exists = True
                print("✅ API behavior exists")
                
                # Update the behavior to ensure proper settings
                behavior.update({
                    'TargetOriginId': 'lambda-origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'MinTTL': 0,
                    'DefaultTTL': 0,
                    'MaxTTL': 0,
                    'ForwardedValues': {
                        'QueryString': True,
                        'Cookies': {'Forward': 'all'},
                        'Headers': {
                            'Quantity': 5,
                            'Items': ['Authorization', 'Content-Type', 'Cookie', 'X-Forwarded-For', 'Origin']
                        }
                    },
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'AllowedMethods': {
                        'Quantity': 7,
                        'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD']
                        }
                    },
                    'Compress': False
                })
                break
        
        if not api_behavior_exists:
            print("🔧 Adding API behavior")
            api_behavior = {
                'PathPattern': '/api/*',
                'TargetOriginId': 'lambda-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'MinTTL': 0,
                'DefaultTTL': 0,
                'MaxTTL': 0,
                'ForwardedValues': {
                    'QueryString': True,
                    'Cookies': {'Forward': 'all'},
                    'Headers': {
                        'Quantity': 5,
                        'Items': ['Authorization', 'Content-Type', 'Cookie', 'X-Forwarded-For', 'Origin']
                    }
                },
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },
                'AllowedMethods': {
                    'Quantity': 7,
                    'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'Compress': False
            }
            
            config['CacheBehaviors']['Items'].append(api_behavior)
            config['CacheBehaviors']['Quantity'] += 1
        
        # Also add behavior for /login, /dashboard, /assessment paths
        protected_paths = ['/login', '/dashboard', '/assessment/*']
        
        for path in protected_paths:
            path_exists = any(behavior['PathPattern'] == path for behavior in config['CacheBehaviors']['Items'])
            
            if not path_exists:
                print(f"🔧 Adding behavior for {path}")
                protected_behavior = {
                    'PathPattern': path,
                    'TargetOriginId': 'lambda-origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'MinTTL': 0,
                    'DefaultTTL': 0,
                    'MaxTTL': 0,
                    'ForwardedValues': {
                        'QueryString': True,
                        'Cookies': {'Forward': 'all'},
                        'Headers': {
                            'Quantity': 5,
                            'Items': ['Authorization', 'Content-Type', 'Cookie', 'X-Forwarded-For', 'Origin']
                        }
                    },
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'AllowedMethods': {
                        'Quantity': 7,
                        'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                        'CachedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD']
                        }
                    },
                    'Compress': False
                }
                
                config['CacheBehaviors']['Items'].append(protected_behavior)
                config['CacheBehaviors']['Quantity'] += 1
        
        # Update the distribution
        print("📝 Updating CloudFront distribution...")
        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ CloudFront distribution updated successfully")
        print(f"📋 Total behaviors: {config['CacheBehaviors']['Quantity']}")
        print(f"🎯 Lambda origin: {WORKING_DOMAIN}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def wait_for_deployment(distribution_id):
    """Wait for CloudFront deployment to complete"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    print("\n⏳ Waiting for CloudFront deployment...")
    start_time = time.time()
    
    while time.time() - start_time < 900:  # 15 minute timeout
        try:
            dist_info = cloudfront.get_distribution(Id=distribution_id)
            status = dist_info['Distribution']['Status']
            
            if status == 'Deployed':
                print("✅ CloudFront deployment completed")
                return True
            elif status == 'InProgress':
                elapsed = int(time.time() - start_time)
                print(f"   Status: {status} (elapsed: {elapsed}s)")
                time.sleep(30)
            else:
                print(f"❌ Unexpected status: {status}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking deployment: {str(e)}")
            return False
    
    print("❌ Deployment timeout (15 minutes)")
    return False

def test_fixed_endpoints():
    """Test the fixed endpoints"""
    
    print("\n🧪 Testing Fixed Endpoints")
    print("=" * 30)
    
    import requests
    
    base_url = "https://www.ieltsaiprep.com"
    
    # Test API endpoints
    api_tests = [
        ("/api/maya/introduction", "Maya AI"),
        ("/api/nova-micro/submit", "Nova Micro"),
        ("/login", "Login page"),
        ("/dashboard", "Dashboard")
    ]
    
    for endpoint, name in api_tests:
        try:
            if endpoint.startswith('/api/'):
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=15)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=15)
            
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
                if endpoint.startswith('/api/'):
                    try:
                        data = response.json()
                        if 'message' in data:
                            print(f"   Message: {data['message'][:50]}...")
                    except:
                        pass
            elif response.status_code == 302:
                print(f"✅ {name}: 302 (redirect - security working)")
            else:
                print(f"❌ {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 CloudFront API Routing Fix")
    print("=" * 35)
    
    success = fix_cloudfront_api_routing()
    
    if success:
        print("\n✅ CLOUDFRONT API ROUTING FIXED")
        
        # Get distribution ID for monitoring
        cloudfront = boto3.client('cloudfront', region_name='us-east-1')
        distributions = cloudfront.list_distributions()
        distribution_id = None
        
        for dist in distributions['DistributionList']['Items']:
            if 'www.ieltsaiprep.com' in dist.get('Aliases', {}).get('Items', []):
                distribution_id = dist['Id']
                break
        
        if distribution_id:
            # Wait for deployment
            deployment_success = wait_for_deployment(distribution_id)
            
            if deployment_success:
                print("\n🎉 DEPLOYMENT COMPLETE")
                test_fixed_endpoints()
                print("\n✅ www.ieltsaiprep.com July 8th features should now work!")
                print("🔑 Test credentials: test@ieltsaiprep.com / password123")
                print("📱 Ready for comprehensive feature testing")
            else:
                print("\n⚠️ Deployment may still be in progress")
                print("🔄 Try testing endpoints in 5-10 minutes")
        
    else:
        print("\n❌ CLOUDFRONT FIX FAILED")