"""
Check what AWS services are accessible with current credentials.
"""
import boto3
import botocore
import os

def test_aws_services():
    """Test which AWS services are accessible with current credentials."""
    print("Testing AWS services accessibility...")
    
    # List of common AWS services to test
    services = [
        's3', 'ec2', 'lambda', 'dynamodb', 'iam', 
        'cloudwatch', 'sqs', 'sns', 'polly', 'transcribe',
        'bedrock', 'bedrock-runtime'
    ]
    
    region = os.environ.get('AWS_REGION', 'us-east-1')
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    results = {"accessible": [], "inaccessible": []}
    
    for service in services:
        try:
            # Create client for the service
            client = boto3.client(
                service_name=service,
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            
            # Try a simple operation based on the service
            if service == 's3':
                response = client.list_buckets()
                print(f"✓ S3: Can list buckets, found {len(response.get('Buckets', []))} buckets")
            elif service == 'ec2':
                response = client.describe_regions()
                print(f"✓ EC2: Can describe regions, found {len(response.get('Regions', []))} regions")
            elif service == 'lambda':
                response = client.list_functions(MaxItems=10)
                print(f"✓ Lambda: Can list functions, found {len(response.get('Functions', []))} functions")
            elif service == 'dynamodb':
                response = client.list_tables(Limit=10)
                print(f"✓ DynamoDB: Can list tables, found {len(response.get('TableNames', []))} tables")
            elif service == 'iam':
                response = client.list_users(MaxItems=10)
                print(f"✓ IAM: Can list users, found {len(response.get('Users', []))} users")
            elif service == 'cloudwatch':
                response = client.list_metrics(MaxResults=10)
                print(f"✓ CloudWatch: Can list metrics")
            elif service == 'sqs':
                response = client.list_queues(MaxResults=10)
                print(f"✓ SQS: Can list queues, found {len(response.get('QueueUrls', []))} queues")
            elif service == 'sns':
                response = client.list_topics(MaxResults=10)
                print(f"✓ SNS: Can list topics, found {len(response.get('Topics', []))} topics")
            elif service == 'polly':
                response = client.describe_voices(LanguageCode='en-US', MaxResults=10)
                print(f"✓ Polly: Can describe voices, found {len(response.get('Voices', []))} voices")
            elif service == 'transcribe':
                response = client.list_transcription_jobs(MaxResults=10)
                print(f"✓ Transcribe: Can list transcription jobs")
            elif service == 'bedrock':
                response = client.list_foundation_models(maxResults=10)
                print(f"✓ Bedrock: Can list foundation models, found {len(response.get('modelSummaries', []))} models")
            elif service == 'bedrock-runtime':
                print(f"✓ Bedrock Runtime: Client created, but operation test requires a model call")
                # We won't make a model call here since we've already tested that separately
            
            results["accessible"].append(service)
            
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            print(f"✗ {service}: Access error - {error_code} - {error_message}")
            results["inaccessible"].append({
                "service": service, 
                "error": f"{error_code}: {error_message}"
            })
        except Exception as e:
            print(f"✗ {service}: Error - {str(e)}")
            results["inaccessible"].append({
                "service": service, 
                "error": str(e)
            })
    
    print("\nSUMMARY:")
    print(f"Accessible services ({len(results['accessible'])}): {', '.join(results['accessible'])}")
    print(f"Inaccessible services ({len(results['inaccessible'])}): {', '.join([x['service'] for x in results['inaccessible']])}")
    
    return results

if __name__ == "__main__":
    test_aws_services()