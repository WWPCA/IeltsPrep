# IELTS GenAI Prep - Mobile App Deployment Guide

## Overview
This guide covers the complete deployment process for both iOS (Apple App Store) and Android (Google Play Store) versions of IELTS GenAI Prep.

## Prerequisites
✅ Apple Developer Account ($99/year)
✅ Google Play Console Account ($25 one-time)
✅ Production AWS Lambda Backend (LIVE: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod)

## Step 1: Install Required Dependencies

```bash
# Install Capacitor CLI
npm install -g @capacitor/cli

# Install iOS and Android platforms
npm install @capacitor/ios @capacitor/android

# Install Capacitor plugins
npm install @capacitor/app @capacitor/device @capacitor/network @capacitor/splash-screen @capacitor/status-bar @capacitor/toast
```

## Step 2: Build the Mobile App

```bash
# Create mobile platforms
npx cap add ios
npx cap add android

# Copy web assets to mobile platforms
npx cap copy

# Sync native dependencies
npx cap sync
```

## Step 3: iOS App Store Deployment

### 3.1 Open iOS Project
```bash
npx cap open ios
```

### 3.2 Configure iOS App in Xcode
1. **App Identity:**
   - Bundle Identifier: `com.ieltsgenaiprep.app`
   - Display Name: `IELTS GenAI Prep`
   - Version: `1.0.0`
   - Build: `1`

2. **Signing & Capabilities:**
   - Team: Select your Apple Developer Team
   - Enable "In-App Purchase" capability
   - Enable "Network" capability

3. **App Store Connect Setup:**
   - Create new app in App Store Connect
   - App Name: `IELTS GenAI Prep`
   - Bundle ID: `com.ieltsgenaiprep.app`
   - SKU: `ielts-genai-prep-ios`

### 3.3 Configure In-App Purchases
Create 4 products in App Store Connect:

1. **Academic Writing Assessment**
   - Product ID: `com.ieltsgenaiprep.academic.writing`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Name: `TrueScore® GenAI Writing Assessment (Academic)`

2. **General Writing Assessment**
   - Product ID: `com.ieltsgenaiprep.general.writing`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Name: `TrueScore® GenAI Writing Assessment (General)`

3. **Academic Speaking Assessment**
   - Product ID: `com.ieltsgenaiprep.academic.speaking`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Name: `ClearScore® GenAI Speaking Assessment (Academic)`

4. **General Speaking Assessment**
   - Product ID: `com.ieltsgenaiprep.general.speaking`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Name: `ClearScore® GenAI Speaking Assessment (General)`

### 3.4 App Metadata
```
App Name: IELTS GenAI Prep
Subtitle: AI-Powered IELTS Assessment
Category: Education
Keywords: IELTS, test preparation, AI assessment, writing, speaking

Description:
Master IELTS with the world's ONLY GenAI assessment platform. IELTS GenAI Prep delivers precise, examiner-aligned feedback through exclusive TrueScore® writing analysis and ClearScore® speaking assessment systems.

Features:
• TrueScore® GenAI Writing Assessment for Academic and General Training
• ClearScore® GenAI Speaking Assessment with Maya AI Examiner
• 4 unique assessments per purchase ($36 each)
• Official IELTS criteria alignment
• Real-time conversation analysis
• Detailed band score feedback
• Cross-platform access (mobile and web)

Privacy Policy URL: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/privacy-policy
Terms of Use URL: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/terms-of-service
```

### 3.5 Build and Upload
```bash
# Archive the app in Xcode
# Product > Archive
# Upload to App Store Connect
```

## Step 4: Android Google Play Store Deployment

### 4.1 Open Android Project
```bash
npx cap open android
```

### 4.2 Configure Android App
1. **App Details (android/app/build.gradle):**
```gradle
android {
    compileSdkVersion 34
    defaultConfig {
        applicationId "com.ieltsgenaiprep.app"
        minSdkVersion 22
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
}
```

2. **Permissions (android/app/src/main/AndroidManifest.xml):**
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
<uses-permission android:name="com.android.vending.BILLING" />
```

### 4.3 Generate Signed APK/AAB
1. **Create Keystore:**
```bash
keytool -genkey -v -keystore ielts-genai-prep.keystore -alias ielts-release -keyalg RSA -keysize 2048 -validity 10000
```

2. **Build Release:**
```bash
cd android
./gradlew bundleRelease
```

### 4.4 Google Play Console Setup
1. **Create App:**
   - App Name: `IELTS GenAI Prep`
   - Package Name: `com.ieltsgenaiprep.app`
   - Category: Education

2. **Configure In-App Products:**
   - `academic_writing_assessment` - $36.00
   - `general_writing_assessment` - $36.00
   - `academic_speaking_assessment` - $36.00
   - `general_speaking_assessment` - $36.00

### 4.5 App Listing
```
Short Description:
AI-powered IELTS preparation with TrueScore® writing and ClearScore® speaking assessments.

Full Description:
Master IELTS with the world's ONLY GenAI assessment platform featuring TrueScore® and ClearScore® technologies.

Our exclusive GenAI systems provide examiner-aligned feedback for both Academic and General Training IELTS preparation:

🎯 TrueScore® Writing Assessment
• Professional GenAI evaluation aligned with official IELTS band descriptors
• Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy
• 4 unique assessments per $36 purchase

🎤 ClearScore® Speaking Assessment  
• Revolutionary GenAI speaking assessment with Maya AI Examiner
• Real-time conversation analysis across all IELTS speaking criteria
• Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation
• 4 unique assessments per $36 purchase

Key Features:
✓ World's first standardized IELTS GenAI assessment system
✓ Official IELTS marking criteria alignment
✓ Cross-platform access (mobile and desktop)
✓ Detailed band score feedback and improvement recommendations
✓ Secure app store billing integration

Perfect for students and professionals preparing for IELTS Academic or General Training tests worldwide.

Privacy Policy: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/privacy-policy
```

## Step 5: Testing Before Submission

### 5.1 Test Production API Integration
```bash
# Test API connectivity
curl -X GET "https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/health"

# Test authentication endpoints
curl -X POST "https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/api/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

### 5.2 Test In-App Purchases
- Test all 4 product purchases in sandbox environments
- Verify receipt validation with AWS Lambda backend
- Confirm assessment access after purchase

## Step 6: App Store Review Preparation

### 6.1 Required Assets
- App Icon (1024x1024px)
- Screenshots for iPhone and Android
- App Preview videos (optional but recommended)

### 6.2 Review Guidelines Compliance
- No external payment systems (only app store billing)
- Clear privacy policy and terms of service
- Age-appropriate content (rated 4+ / Everyone)
- Functional app with all advertised features

## Step 7: Submission Checklist

### iOS App Store
- [ ] App built and uploaded via Xcode
- [ ] All 4 in-app purchases configured
- [ ] App metadata completed
- [ ] Screenshots uploaded
- [ ] Privacy policy and terms links working
- [ ] TestFlight testing completed
- [ ] Submitted for review

### Google Play Store
- [ ] AAB file uploaded
- [ ] All 4 in-app products configured
- [ ] Store listing completed
- [ ] Screenshots uploaded
- [ ] Privacy policy and terms links working
- [ ] Internal testing completed
- [ ] Submitted for review

## Step 8: Post-Submission

### App Store Review Times
- **iOS:** 24-48 hours (typical)
- **Android:** 1-3 days (typical)

### Launch Preparation
- Monitor review status in both consoles
- Prepare marketing materials
- Set up analytics and crash reporting
- Plan user acquisition strategy

## Production Configuration Summary

✅ **Backend:** AWS Lambda (https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod)
✅ **Authentication:** PBKDF2-HMAC-SHA256 with DynamoDB
✅ **In-App Products:** 4 assessments at $36 each
✅ **Cross-Platform:** Native mobile apps + responsive web access
✅ **Compliance:** Privacy policy, terms of service, age ratings

Your IELTS GenAI Prep mobile app is ready for App Store submission with full production backend integration.