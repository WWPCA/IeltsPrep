#!/usr/bin/env python3
"""
Fix Nova Integration with Correct Model Formats
Implement proper Amazon Polly + Nova Micro integration
"""

import boto3
import json
from botocore.exceptions import ClientError

def test_corrected_nova_integration():
    """Test Nova models with correct request formats"""
    
    print("🔧 Testing Corrected Nova Integration")
    print("=" * 50)
    
    # Test Nova Micro with correct format
    print("\n1. Testing Nova Micro (IELTS Assessment)...")
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Correct format for Nova Micro
        nova_micro_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Evaluate this IELTS speaking response for band score: 'Hello, my name is Sarah and I am from Toronto, Canada. I have been living here for most of my life and I really enjoy the multicultural environment and friendly people in this city.'"
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            body=json.dumps(nova_micro_payload),
            contentType="application/json"
        )
        
        result = json.loads(response['body'].read())
        if 'output' in result:
            print("✅ Nova Micro working correctly")
            print(f"   Response: {result['output']['message']['content'][0]['text'][:100]}...")
        else:
            print("⚠️ Nova Micro unexpected response format")
            print(f"   Response: {result}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Nova Micro error: {error_code}")
        if error_code == "AccessDeniedException":
            print("   Need: bedrock:InvokeModel permission")
    except Exception as e:
        print(f"❌ Nova Micro test failed: {str(e)}")
    
    # Test Nova Sonic with correct format
    print("\n2. Testing Nova Sonic (Speech Processing)...")
    try:
        # Nova Sonic requires different format for speech synthesis
        nova_sonic_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment."
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.3
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-sonic-v1:0",
            body=json.dumps(nova_sonic_payload),
            contentType="application/json"
        )
        
        result = json.loads(response['body'].read())
        print("✅ Nova Sonic accessible")
        print(f"   Response format: {list(result.keys())}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Nova Sonic error: {error_code}")
    except Exception as e:
        print(f"❌ Nova Sonic test failed: {str(e)}")
    
    print("\n3. Testing Amazon Polly (Maya Voice)...")
    try:
        polly_client = boto3.client('polly', region_name='us-east-1')
        
        response = polly_client.synthesize_speech(
            Text="Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment.",
            OutputFormat='mp3',
            VoiceId='Amy',
            Engine='neural'
        )
        
        if 'AudioStream' in response:
            audio_size = len(response['AudioStream'].read())
            print("✅ Amazon Polly Amy voice working")
            print(f"   Audio size: {audio_size} bytes")
            print(f"   Voice: Amy (British Female)")
        else:
            print("❌ Polly synthesis failed")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ POLLY ACCESS DENIED")
            print("   🔑 ADD THIS PERMISSION TO YOUR IAM POLICY:")
            print("   polly:SynthesizeSpeech")
        else:
            print(f"❌ Polly error: {error_code}")
    except Exception as e:
        print(f"❌ Polly test failed: {str(e)}")
    
    return True

def generate_complete_iam_policy():
    """Generate complete IAM policy for IELTS platform"""
    
    print("\n📋 COMPLETE IAM POLICY FOR IELTS PLATFORM")
    print("=" * 60)
    
    complete_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetModel",
                    "bedrock:ListModels"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-sonic-v1:0",
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-micro-v1:0",
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-lite-v1:0"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "polly:SynthesizeSpeech",
                    "polly:GetSpeechSynthesisTask",
                    "polly:ListSpeechSynthesisTasks"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "apigateway:GET",
                    "apigateway:POST",
                    "execute-api:Invoke",
                    "execute-api:ManageConnections"
                ],
                "Resource": [
                    "arn:aws:apigateway:us-east-1::/apis/*",
                    "arn:aws:execute-api:us-east-1:*:*/*/POST/*",
                    "arn:aws:execute-api:us-east-1:*:*/*/@connections/*"
                ]
            }
        ]
    }
    
    print("🔑 ADD THIS TO YOUR IELTSGenAIPrepFullAccess POLICY:")
    print(json.dumps(complete_policy, indent=2))
    
    print("\n💡 CRITICAL ADDITION NEEDED:")
    print("Your current policy is missing Amazon Polly permissions.")
    print("Add the polly:SynthesizeSpeech permission for Maya's Amy voice.")

if __name__ == "__main__":
    test_corrected_nova_integration()
    generate_complete_iam_policy()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Add polly:SynthesizeSpeech to your IAM policy")
    print("2. Deploy corrected Nova integration")
    print("3. Test Maya voice synthesis with Amazon Polly Amy")