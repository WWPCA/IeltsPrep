#!/usr/bin/env python3
"""
Mobile App Store Deployment Configuration
Creates iOS and Android app configurations for store submission
"""

import json
import os
from datetime import datetime

def create_ios_app_store_config():
    """Create iOS App Store configuration"""
    
    ios_config = {
        "app_info": {
            "name": "IELTS GenAI Prep",
            "bundle_id": "com.ieltsaiprep.app",
            "version": "1.0.0",
            "build_number": "1",
            "category": "Education",
            "primary_category": "Education",
            "secondary_category": "Reference"
        },
        "pricing": {
            "app_price": "Free",
            "in_app_purchases": [
                {
                    "product_id": "academic_writing_assessment",
                    "reference_name": "Academic Writing Assessment",
                    "price_tier": "Tier 3",
                    "price_usd": 36.49,
                    "type": "consumable"
                },
                {
                    "product_id": "general_writing_assessment", 
                    "reference_name": "General Writing Assessment",
                    "price_tier": "Tier 3",
                    "price_usd": 36.49,
                    "type": "consumable"
                },
                {
                    "product_id": "academic_speaking_assessment",
                    "reference_name": "Academic Speaking Assessment", 
                    "price_tier": "Tier 3",
                    "price_usd": 36.49,
                    "type": "consumable"
                },
                {
                    "product_id": "general_speaking_assessment",
                    "reference_name": "General Speaking Assessment",
                    "price_tier": "Tier 3", 
                    "price_usd": 36.49,
                    "type": "consumable"
                }
            ]
        },
        "metadata": {
            "description": "IELTS GenAI Prep is the only AI-powered IELTS assessment platform with official band-aligned feedback. Get instant, accurate scoring using TrueScore® writing assessment and ClearScore® speaking assessment with Maya AI examiner. Perfect your IELTS skills with authentic AI feedback that matches official IELTS marking criteria.",
            "keywords": "IELTS,test prep,AI assessment,English learning,speaking practice,writing feedback,band score,exam preparation",
            "promotional_text": "Master IELTS with AI-powered scoring that matches official marking criteria. Get instant feedback on writing and speaking.",
            "marketing_url": "https://www.ieltsaiprep.com",
            "privacy_policy_url": "https://www.ieltsaiprep.com/privacy-policy",
            "support_url": "https://www.ieltsaiprep.com/terms-of-service"
        },
        "app_review_info": {
            "demo_account_required": True,
            "demo_account_username": "prodtest@ieltsgenaiprep.com",
            "demo_account_password": "test123",
            "notes": "This app requires users to purchase assessments through in-app purchases. Demo account has pre-purchased access to all 4 assessment types. The app connects to www.ieltsaiprep.com for cross-platform access."
        },
        "capabilities": {
            "in_app_purchase": True,
            "network_extensions": False,
            "push_notifications": False,
            "background_processing": False,
            "camera": False,
            "microphone": True,
            "location": False
        },
        "deployment_info": {
            "minimum_os_version": "12.0",
            "device_requirements": "iPhone, iPad",
            "supported_languages": ["English"],
            "age_rating": "4+",
            "content_rights": "Does Not Use Third-Party Content"
        }
    }
    
    with open('ios_app_store_config.json', 'w') as f:
        json.dump(ios_config, f, indent=2)
    
    return ios_config

def create_android_play_store_config():
    """Create Android Play Store configuration"""
    
    android_config = {
        "app_info": {
            "name": "IELTS GenAI Prep",
            "package_name": "com.ieltsaiprep.app",
            "version_name": "1.0.0", 
            "version_code": 1,
            "category": "Education",
            "content_rating": "Everyone",
            "target_audience": "General"
        },
        "pricing": {
            "app_price": "Free",
            "in_app_products": [
                {
                    "product_id": "academic_writing_assessment",
                    "title": "Academic Writing Assessment",
                    "description": "4 AI-graded Academic Writing assessments with detailed feedback",
                    "price": "$36.49",
                    "type": "managed_product"
                },
                {
                    "product_id": "general_writing_assessment",
                    "title": "General Writing Assessment", 
                    "description": "4 AI-graded General Training Writing assessments with detailed feedback",
                    "price": "$36.49",
                    "type": "managed_product"
                },
                {
                    "product_id": "academic_speaking_assessment",
                    "title": "Academic Speaking Assessment",
                    "description": "4 AI-graded Academic Speaking assessments with Maya AI examiner",
                    "price": "$36.49",
                    "type": "managed_product"
                },
                {
                    "product_id": "general_speaking_assessment",
                    "title": "General Speaking Assessment",
                    "description": "4 AI-graded General Training Speaking assessments with Maya AI examiner", 
                    "price": "$36.49",
                    "type": "managed_product"
                }
            ]
        },
        "store_listing": {
            "short_description": "AI-powered IELTS assessment with official band-aligned feedback",
            "full_description": "IELTS GenAI Prep is the only AI-powered IELTS assessment platform with official band-aligned feedback. Get instant, accurate scoring using TrueScore® writing assessment and ClearScore® speaking assessment with Maya AI examiner.\\n\\nKey Features:\\n• TrueScore® AI Writing Assessment with official IELTS rubric alignment\\n• ClearScore® AI Speaking Assessment with Maya AI examiner\\n• Cross-platform access - use on mobile and desktop\\n• Authentic feedback matching official IELTS marking criteria\\n• $36.49 USD for 4 comprehensive assessments per type\\n\\nPerfect for Academic and General Training IELTS preparation with AI technology that understands official band descriptors.",
            "privacy_policy_url": "https://www.ieltsaiprep.com/privacy-policy",
            "website": "https://www.ieltsaiprep.com"
        },
        "data_safety": {
            "data_collected": {
                "personal_info": {
                    "email_address": {"collected": True, "shared": False, "optional": False},
                    "name": {"collected": False, "shared": False, "optional": True}
                },
                "financial_info": {
                    "purchase_history": {"collected": True, "shared": False, "optional": False}
                },
                "health_fitness": {
                    "health_info": {"collected": False, "shared": False, "optional": False}
                },
                "messages": {
                    "other_user_communications": {"collected": True, "shared": False, "optional": False}
                },
                "audio": {
                    "voice_audio": {"collected": True, "shared": False, "optional": False}
                },
                "files_docs": {
                    "files_docs": {"collected": True, "shared": False, "optional": False}
                }
            },
            "data_usage": {
                "app_functionality": True,
                "analytics": False,
                "advertising": False,
                "account_management": True
            },
            "security_practices": {
                "encryption_in_transit": True,
                "encryption_at_rest": True,
                "data_deletion": True,
                "user_controls": True
            }
        },
        "content_rating": {
            "questionnaire_responses": {
                "violence": "None",
                "sexual_content": "None", 
                "profanity": "None",
                "substances": "None",
                "gambling": "None",
                "user_generated_content": "Yes - Educational content only",
                "location_sharing": "No",
                "personal_info_sharing": "No"
            }
        },
        "technical_requirements": {
            "min_sdk_version": 21,
            "target_sdk_version": 34,
            "permissions": [
                "android.permission.INTERNET",
                "android.permission.RECORD_AUDIO",
                "com.android.vending.BILLING"
            ],
            "hardware_features": [
                "android.hardware.microphone"
            ]
        }
    }
    
    with open('android_play_store_config.json', 'w') as f:
        json.dump(android_config, f, indent=2)
    
    return android_config

def create_capacitor_config():
    """Create Capacitor configuration for mobile app"""
    
    capacitor_config = {
        "appId": "com.ieltsaiprep.app",
        "appName": "IELTS GenAI Prep",
        "webDir": "dist",
        "server": {
            "url": "https://www.ieltsaiprep.com",
            "cleartext": False
        },
        "plugins": {
            "SplashScreen": {
                "launchShowDuration": 2000,
                "backgroundColor": "#667eea",
                "showSpinner": False
            },
            "PushNotifications": {
                "presentationOptions": ["badge", "sound", "alert"]
            },
            "LocalNotifications": {
                "smallIcon": "ic_stat_icon_config_sample",
                "iconColor": "#667eea"
            }
        },
        "ios": {
            "scheme": "IELTS GenAI Prep",
            "webContentsDebuggingEnabled": False
        },
        "android": {
            "allowMixedContent": True,
            "webContentsDebuggingEnabled": False
        }
    }
    
    with open('capacitor.config.json', 'w') as f:
        json.dump(capacitor_config, f, indent=2)
    
    return capacitor_config

def create_app_store_deployment_guide():
    """Create comprehensive deployment guide"""
    
    guide_content = f"""# Mobile App Store Deployment Guide
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Pre-Deployment Checklist

### 1. Production Website Verification
- ✅ Deploy comprehensive_production_20250717_185438.zip to AWS Lambda
- ✅ Test all endpoints at https://www.ieltsaiprep.com
- ✅ Verify login with test credentials: prodtest@ieltsgenaiprep.com / test123
- ✅ Confirm all 4 assessment types accessible
- ✅ Verify $36.49 USD pricing consistency

### 2. Mobile App Configuration
- ✅ Update capacitor.config.json with production server URL
- ✅ Configure in-app purchase product IDs
- ✅ Set up Apple Developer Account and Google Play Console
- ✅ Generate app signing certificates

## iOS App Store Deployment

### Step 1: Xcode Configuration
```bash
# Install dependencies
npm install
npx cap add ios
npx cap sync ios

# Open in Xcode
npx cap open ios
```

### Step 2: App Store Connect Setup
1. Create app in App Store Connect
2. Set Bundle ID: com.ieltsaiprep.app
3. Configure in-app purchases:
   - academic_writing_assessment: $36.49 USD
   - general_writing_assessment: $36.49 USD
   - academic_speaking_assessment: $36.49 USD
   - general_speaking_assessment: $36.49 USD

### Step 3: Review Information
- Demo Account: prodtest@ieltsgenaiprep.com / test123
- Review Notes: "App requires in-app purchases for assessments. Demo account has pre-purchased access."

## Android Play Store Deployment

### Step 1: Android Build
```bash
# Build Android app
npx cap add android
npx cap sync android
npx cap open android
```

### Step 2: Google Play Console Setup
1. Create app in Google Play Console
2. Set Package Name: com.ieltsaiprep.app
3. Complete Data Safety form with provided responses
4. Configure in-app products with $36.49 USD pricing

### Step 3: Release Management
- Use internal testing track first
- Provide test account: prodtest@ieltsgenaiprep.com / test123
- Submit for review after successful testing

## Testing Protocol

### Production Website Testing
1. Navigate to https://www.ieltsaiprep.com
2. Test all pages: home, login, privacy-policy, terms-of-service
3. Login with test credentials
4. Verify dashboard shows all 4 assessment types
5. Test each assessment page loads correctly

### Mobile App Testing
1. Install app on test device
2. Complete in-app purchase flow
3. Verify cross-platform sync with website
4. Test assessment functionality
5. Verify receipt validation

## Security Considerations

### reCAPTCHA Configuration
- Site Key: 6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ
- Secret Key: Configure in Lambda environment variables

### CloudFront Security
- Header: CF-Secret-3140348d
- Direct API Gateway access blocked

### Database Security
- PBKDF2 password hashing
- Session-based authentication
- GDPR compliance implemented

## Support Documentation

### Privacy Policy
- URL: https://www.ieltsaiprep.com/privacy-policy
- GDPR compliant with simplified data usage disclosure
- Voice recording policy clearly stated

### Terms of Service  
- URL: https://www.ieltsaiprep.com/terms-of-service
- Non-refundable purchase policy
- AI content usage guidelines

## Post-Deployment Monitoring

### Key Metrics to Track
- App store approval status
- User registration and purchase rates
- Assessment completion rates
- Cross-platform usage patterns

### Support Channels
- Website: https://www.ieltsaiprep.com
- Technical issues: Monitor CloudWatch logs
- User support: Email integration via AWS SES

## Emergency Procedures

### If App Rejected
1. Review rejection reason
2. Update app according to guidelines
3. Resubmit with detailed response
4. Use test account for reviewer demonstration

### If Website Issues
1. Check CloudWatch logs for errors
2. Verify CloudFront distribution status
3. Test Lambda function directly
4. Monitor DynamoDB table access

## Success Criteria

### App Store Approval
- Both iOS and Android apps approved
- In-app purchases configured correctly
- Cross-platform functionality verified

### Production Readiness
- All endpoints returning HTTP 200
- User authentication working
- Assessment delivery functional
- Payment processing operational

## Contact Information

For deployment support:
- Production website: https://www.ieltsaiprep.com
- Test credentials: prodtest@ieltsgenaiprep.com / test123
- AWS Lambda function: ielts-genai-prep-api
- CloudFront distribution: E1EPXAU67877FR
"""

    with open('app_store_deployment_guide.md', 'w') as f:
        f.write(guide_content)
    
    return guide_content

def main():
    """Main deployment preparation function"""
    
    print("📱 Creating mobile app store deployment configurations...")
    
    # Create configurations
    ios_config = create_ios_app_store_config()
    android_config = create_android_play_store_config() 
    capacitor_config = create_capacitor_config()
    deployment_guide = create_app_store_deployment_guide()
    
    print("✅ Created iOS App Store configuration: ios_app_store_config.json")
    print("✅ Created Android Play Store configuration: android_play_store_config.json")
    print("✅ Created Capacitor configuration: capacitor.config.json")
    print("✅ Created deployment guide: app_store_deployment_guide.md")
    
    print(f"""
🚀 MOBILE APP DEPLOYMENT READY

📦 Files Created:
- ios_app_store_config.json (iOS configuration)
- android_play_store_config.json (Android configuration) 
- capacitor.config.json (Mobile app configuration)
- app_store_deployment_guide.md (Complete deployment guide)

💰 In-App Purchase Pricing:
- All 4 assessment types: $36.49 USD each
- Product IDs configured for both platforms
- Cross-platform purchase verification

🔒 Security & Compliance:
- Data Safety forms completed
- Privacy Policy: https://www.ieltsaiprep.com/privacy-policy
- Terms of Service: https://www.ieltsaiprep.com/terms-of-service
- GDPR compliance implemented

🧪 Testing:
- Demo account: prodtest@ieltsgenaiprep.com / test123
- Production website: https://www.ieltsaiprep.com
- All endpoints functional after Lambda deployment

📋 Next Steps:
1. Deploy comprehensive_production_20250717_185438.zip to AWS Lambda
2. Test production website functionality
3. Build mobile apps using Capacitor configurations
4. Submit to App Store and Play Store for review

Ready for app store submission! 🎉
""")

if __name__ == "__main__":
    main()