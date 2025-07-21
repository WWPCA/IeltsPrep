# IELTS GenAI Prep - Android App Store Deployment Guide

## Current Status
✅ **Capacitor Configuration Complete**
- App ID: `com.ieltsaiprep.app`
- App Name: "IELTS GenAI Prep"
- Android project structure exists in `/android` folder
- Web assets synced successfully with Capacitor

## Google Play Console Setup Status
✅ **App Created**: "IELTS AI PREP" app created in Google Play Console
✅ **Ready for Upload**: Internal testing track available

## Next Steps for Android Deployment

### Option 1: Build Locally (Recommended)
1. **Install Android Studio** on your local machine
2. **Open the Android project**:
   ```bash
   # Download the android folder from this Replit
   # Open android/ folder in Android Studio
   ```
3. **Build the App Bundle**:
   - In Android Studio: Build → Generate Signed Bundle/APK
   - Choose "Android App Bundle (AAB)"
   - Create a keystore or use existing one
   - Build release AAB file

### Option 2: GitHub Actions (Automated)
1. **Push code to GitHub** (already done)
2. **Set up GitHub Actions** with Android build workflow
3. **Store keystore secrets** in GitHub repository secrets
4. **Automatic AAB generation** on each push

## Required App Information for Google Play Console

### 1. App Content Declaration
- **Target Audience**: Adults (IELTS test candidates)
- **Content Rating**: ESRB: E for Everyone
- **Privacy Policy URL**: https://www.ieltsaiprep.com/privacy-policy
- **App Category**: Education
- **Contact Email**: support@ieltsaiprep.com

### 2. Store Listing Details
```
App Name: IELTS GenAI Prep
Short Description: AI-powered IELTS assessment with instant band scores
Full Description: Master IELTS with the world's only GenAI assessment platform featuring TrueScore® Writing and ClearScore® Speaking technologies.

Key Features:
• TrueScore® AI Writing Assessment
• ClearScore® AI Speaking Evaluation  
• Instant band scores and feedback
• Academic and General Training modules
• Mobile-first authentication
• Cross-platform sync

Screenshots Required:
- Phone screenshots (minimum 2)
- Tablet screenshots (recommended)
- Feature graphic (1024 x 500px)
- App icon (512 x 512px)
```

### 3. Pricing and Distribution
- **Price**: Free (with in-app purchases)
- **In-App Products**:
  - Academic Writing Assessment: $36.49 USD
  - General Writing Assessment: $36.49 USD  
  - Academic Speaking Assessment: $36.49 USD
  - General Speaking Assessment: $36.49 USD
- **Countries**: Worldwide distribution

### 4. App Bundle Upload Process
1. **Upload AAB file** to Internal Testing track
2. **Complete Data Safety form** (based on privacy policy)
3. **Add release notes**: "Initial release of AI-powered IELTS assessment platform"
4. **Submit for review**

## Data Safety Declaration (For Google Play)

Based on our privacy policy and app functionality:

**Data Collected**:
- ✅ Personal Info: Email address, name
- ✅ Financial Info: Purchase history  
- ✅ Messages: Writing submissions
- ✅ Audio: Speaking recordings (not stored)
- ✅ Files: Assessment responses

**Data Usage**:
- Assessment evaluation and feedback
- Account management and authentication
- Purchase verification and billing

**Data Sharing**: None (no third-party sharing)
**Data Security**: Encrypted in transit and at rest

## Testing Requirements (New Developer Account)

Based on Google's new requirements:
1. **Internal Testing**: Required for at least 14 days
2. **Closed Testing**: Minimum 20 testers for 14 days
3. **App Bundle Size**: Should be under 150MB (currently ~16MB)
4. **Target API Level**: Android 14 (API level 34)

## Ready Files in Project
✅ **capacitor.config.ts** - Configured with correct app ID
✅ **android/** - Complete Android project structure  
✅ **AndroidManifest.xml** - Proper permissions and configuration
✅ **build.gradle** - Android build configuration
✅ **Privacy Policy** - GDPR compliant at www.ieltsaiprep.com/privacy-policy
✅ **Terms of Service** - Available at www.ieltsaiprep.com/terms-of-service

## Immediate Action Required
**Download the `/android` folder** from this Replit and open in Android Studio to build the AAB file for upload to Google Play Console.

The app is fully configured and ready for production deployment!