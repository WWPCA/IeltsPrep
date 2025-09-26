#!/usr/bin/env python3
"""
Check Available Nova Models in AWS Bedrock
Identify correct model IDs and supported features
"""

import boto3
import json
from botocore.exceptions import ClientError

def check_available_models():
    """Check what Nova models are actually available"""
    
    print("🔍 Checking Available Nova Models in AWS Bedrock")
    print("=" * 50)
    
    try:
        # Initialize Bedrock client
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        
        # List all foundation models
        response = bedrock_client.list_foundation_models()
        
        nova_models = []
        all_models = response.get('modelSummaries', [])
        
        print(f"📊 Total models available: {len(all_models)}")
        print("\n🔍 Filtering for Nova models...")
        
        for model in all_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            
            if 'nova' in model_id.lower() or 'nova' in model_name.lower():
                nova_models.append(model)
                print(f"✅ Found: {model_id}")
                print(f"   Name: {model_name}")
                print(f"   Provider: {model.get('providerName', 'N/A')}")
                print(f"   Modalities: {model.get('inputModalities', [])} → {model.get('outputModalities', [])}")
                print(f"   Streaming: {model.get('responseStreamingSupported', False)}")
                print("")
        
        if not nova_models:
            print("❌ No Nova models found")
            print("💡 Checking for alternative voice synthesis models...")
            
            # Look for other voice/audio models
            voice_models = []
            for model in all_models:
                modalities = model.get('inputModalities', []) + model.get('outputModalities', [])
                if 'AUDIO' in modalities or 'SPEECH' in modalities:
                    voice_models.append(model)
            
            if voice_models:
                print(f"🎵 Found {len(voice_models)} voice/audio models:")
                for model in voice_models:
                    print(f"   - {model.get('modelId', 'N/A')}: {model.get('modelName', 'N/A')}")
            else:
                print("❌ No voice synthesis models found")
        
        # Check model access specifically
        print("\n🔐 Testing Model Access...")
        
        # Test common Nova model IDs
        test_models = [
            "amazon.nova-sonic-v1:0",
            "amazon.nova-micro-v1:0", 
            "amazon.nova-lite-v1:0",
            "amazon.nova-pro-v1:0"
        ]
        
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        for model_id in test_models:
            try:
                # Test with minimal payload
                response = bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps({"messages": [{"role": "user", "content": "test"}]}),
                    contentType="application/json"
                )
                print(f"✅ {model_id}: Access granted")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == "ValidationException":
                    print(f"⚠️ {model_id}: Model exists but requires different format")
                elif error_code == "AccessDeniedException":
                    print(f"❌ {model_id}: Access denied")
                elif error_code == "ResourceNotFoundException":
                    print(f"❌ {model_id}: Model not found")
                else:
                    print(f"❓ {model_id}: {error_code}")
            except Exception as e:
                print(f"❓ {model_id}: {str(e)}")
        
        return nova_models
        
    except Exception as e:
        print(f"❌ Error checking models: {str(e)}")
        return []

def test_polly_alternative():
    """Test Amazon Polly as alternative for voice synthesis"""
    
    print("\n🎵 Testing Amazon Polly Alternative (Amy Voice)")
    print("=" * 40)
    
    try:
        polly_client = boto3.client('polly', region_name='us-east-1')
        
        # Test Amy voice synthesis
        response = polly_client.synthesize_speech(
            Text="Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment.",
            OutputFormat='mp3',
            VoiceId='Amy',
            Engine='neural'
        )
        
        if 'AudioStream' in response:
            print("✅ Amazon Polly Amy voice synthesis successful")
            print("   Voice: Amy (British Female)")
            print("   Engine: Neural")
            print("   Format: MP3")
            print("   📝 Recommendation: Use Polly for Maya voice synthesis")
            return True
        else:
            print("❌ Polly synthesis failed")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ Polly access denied - need polly:SynthesizeSpeech permission")
        else:
            print(f"❌ Polly error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Polly test failed: {str(e)}")
        return False

if __name__ == "__main__":
    nova_models = check_available_models()
    polly_works = test_polly_alternative()
    
    print("\n" + "=" * 50)
    print("📋 RECOMMENDATIONS:")
    
    if nova_models:
        print("✅ Nova models available - use for assessment evaluation")
    else:
        print("⚠️ Nova models not found - check model availability")
    
    if polly_works:
        print("✅ Use Amazon Polly Amy voice for Maya examiner speech")
        print("   Required permission: polly:SynthesizeSpeech")
    else:
        print("❌ Need Polly permissions for voice synthesis")
    
    print("\n🎯 Final Architecture Recommendation:")
    print("   • Amazon Polly Amy → Maya voice synthesis")
    print("   • Amazon Nova Micro → IELTS assessment evaluation")
    print("   • WebSocket API → Real-time audio streaming")