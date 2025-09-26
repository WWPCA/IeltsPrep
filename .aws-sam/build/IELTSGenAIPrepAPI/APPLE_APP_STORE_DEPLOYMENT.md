# Apple App Store Deployment Guide for IELTS GenAI Prep

## Current Configuration Status

### Mobile App Configuration ✓
- **App ID**: com.ieltsgenaiprep.app
- **App Name**: IELTS GenAI Prep
- **Server URL**: https://www.ieltsaiprep.com (updated for new domain)
- **Deep Link Hostname**: www.ieltsaiprep.com
- **Capacitor Version**: 7.3.0

### iOS Project Structure ✓
- iOS project exists in `/ios/App/`
- Xcode project: `App.xcodeproj`
- Xcode workspace: `App.xcworkspace`
- Podfile configured for Capacitor plugins

## Apple App Store Deployment Steps

### Step 1: Apple Developer Account Requirements
You need an active Apple Developer Program membership ($99/year):
1. Sign up at https://developer.apple.com/programs/
2. Complete enrollment process
3. Verify your developer account status

### Step 2: App Store Connect Configuration
1. **Create App Record**:
   - Login to App Store Connect
   - Create new app with Bundle ID: `com.ieltsgenaiprep.app`
   - App Name: "IELTS GenAI Prep"
   - Primary Language: English
   - SKU: `ielts-genai-prep-ios`

2. **App Information**:
   - Category: Education
   - Subcategory: Education
   - Content Rights: Own or license all content
   - Age Rating: 4+ (Educational content)

### Step 3: Pricing and Availability
- **Price**: Free (with In-App Purchases)
- **Availability**: All Countries and Regions
- **Release**: Manual Release

### Step 4: In-App Purchase Products
Configure 4 assessment products at $36.00 USD each:

1. **Academic Writing Assessment** (`academic_writing_assessment`)
   - Product ID: `com.ieltsgenaiprep.app.academic.writing`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Display Name: "TrueScore® Academic Writing Assessment"
   - Description: "AI-powered writing assessment for Academic IELTS with 4 unique tests"

2. **Academic Speaking Assessment** (`academic_speaking_assessment`)
   - Product ID: `com.ieltsgenaiprep.app.academic.speaking`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Display Name: "ClearScore® Academic Speaking Assessment"
   - Description: "AI conversation-based speaking assessment for Academic IELTS with 4 unique tests"

3. **General Writing Assessment** (`general_writing_assessment`)
   - Product ID: `com.ieltsgenaiprep.app.general.writing`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Display Name: "TrueScore® General Writing Assessment"
   - Description: "AI-powered writing assessment for General Training IELTS with 4 unique tests"

4. **General Speaking Assessment** (`general_speaking_assessment`)
   - Product ID: `com.ieltsgenaiprep.app.general.speaking`
   - Type: Non-Consumable
   - Price: $36.00 USD
   - Display Name: "ClearScore® General Speaking Assessment"
   - Description: "AI conversation-based speaking assessment for General Training IELTS with 4 unique tests"

### Step 5: App Metadata

#### App Store Description
```
🎯 IELTS GenAI Prep - World's ONLY AI-Powered IELTS Assessment Platform

Prepare for IELTS with cutting-edge AI technology featuring TrueScore® and ClearScore® assessments.

🤖 REVOLUTIONARY AI TECHNOLOGY
• Amazon Nova Sonic: Real-time AI conversation for speaking practice
• Amazon Nova Micro: Advanced text analysis for writing evaluation
• Instant feedback with official IELTS criteria alignment

📝 TRUESCORE® WRITING ASSESSMENT
• Academic and General Training Writing Tasks
• Comprehensive feedback on all 4 IELTS criteria
• Detailed improvement suggestions
• 4 unique assessments per purchase

🎤 CLEARSCORE® SPEAKING ASSESSMENT
• Interactive AI conversations with virtual examiner
• Real-time speech analysis and scoring
• Part 1, 2, and 3 speaking test simulation
• 4 unique speaking scenarios per purchase

✨ KEY FEATURES
• Mobile-first design for on-the-go practice
• Cross-platform access (mobile + desktop)
• Secure purchase through App Store
• Permanent access to completed assessments
• Global availability with multi-region support

💡 PERFECT FOR
• IELTS test preparation
• Academic English improvement
• Professional English development
• Immigration requirements preparation

🏆 ASSESSMENT PACKAGES
Each $36 package includes 4 unique, high-quality assessments with personalized AI feedback.

Download now and experience the future of IELTS preparation!
```

#### Keywords
IELTS, English test, speaking practice, writing assessment, AI tutor, test preparation, academic English, immigration, study abroad, language learning

#### App Store Categories
- Primary: Education
- Secondary: Productivity

### Step 6: App Screenshots and Assets

#### Required Screenshots (all must be provided):
1. **iPhone 6.7" Display** (1290 x 2796 pixels) - 3 to 10 screenshots
2. **iPhone 6.5" Display** (1242 x 2688 pixels) - 3 to 10 screenshots
3. **iPhone 5.5" Display** (1242 x 2208 pixels) - 3 to 10 screenshots
4. **iPad Pro 12.9" Display** (2048 x 2732 pixels) - 3 to 10 screenshots
5. **iPad Pro 11" Display** (1668 x 2388 pixels) - 3 to 10 screenshots

#### App Icon Requirements:
- **App Store Icon**: 1024 x 1024 pixels (PNG, no transparency)
- **iOS App Icon**: Multiple sizes generated by Xcode

#### Preview Videos (Optional but Recommended):
- 30-second app preview video
- Same dimensions as screenshots
- Showcase key features and user flow

### Step 7: Privacy Policy and Terms
- **Privacy Policy URL**: https://www.ieltsaiprep.com/privacy-policy
- **Terms of Service URL**: https://www.ieltsaiprep.com/terms-of-service
- **Support URL**: https://www.ieltsaiprep.com/

### Step 8: Build and Upload Process

#### Code Signing and Provisioning
1. Create iOS Distribution Certificate
2. Create App Store Provisioning Profile
3. Configure Xcode project with proper signing

#### Build Commands
```bash
# Sync Capacitor with updated config
npx cap sync ios

# Open Xcode project
npx cap open ios

# In Xcode:
# 1. Select "Any iOS Device" as target
# 2. Archive the project (Product > Archive)
# 3. Upload to App Store Connect
```

### Step 9: App Review Information
- **Demo Account**: Not required (no login needed for basic app review)
- **Contact Information**: Provide support email
- **Notes for Review**: 
  ```
  This app requires in-app purchases to access assessment features. 
  The AI-powered assessments use Amazon Web Services for processing.
  Cross-platform functionality allows users to access purchased content on both mobile and web (www.ieltsaiprep.com).
  ```

### Step 10: Submission Checklist
- [ ] Apple Developer Account active
- [ ] App Store Connect app record created
- [ ] In-app purchase products configured
- [ ] App metadata completed
- [ ] Screenshots and app icon uploaded
- [ ] Privacy policy and terms accessible
- [ ] iOS app built and uploaded via Xcode
- [ ] App submitted for review

## Post-Submission

### Review Timeline
- Initial review: 24-48 hours
- App review: 1-7 days
- In-app purchase review: Additional 2-7 days

### After Approval
1. Release app manually or automatically
2. Monitor App Store Connect analytics
3. Respond to user reviews
4. Plan updates and feature releases

## Technical Notes

### Server Configuration
- Backend: AWS Lambda serverless architecture
- Domain: www.ieltsaiprep.com (SSL enabled)
- AI Services: Amazon Nova Sonic/Micro (us-east-1)
- Payment: Apple App Store In-App Purchases

### Cross-Platform Access
- Users register and purchase in mobile app
- Same credentials work on website
- Assessment results sync across platforms

This deployment guide ensures your IELTS GenAI Prep app meets all Apple App Store requirements and provides a smooth submission process.