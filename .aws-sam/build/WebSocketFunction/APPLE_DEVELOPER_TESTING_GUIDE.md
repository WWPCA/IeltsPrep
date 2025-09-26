# Apple Developer Account - Complete Setup & Testing Guide

## Phase 1: Apple Developer Account Setup

### Account Registration Steps
1. **Visit Apple Developer Portal**: https://developer.apple.com/account/
2. **Choose Account Type**: Individual ($99/year) or Organization ($99/year)
3. **Complete Enrollment**: Provide legal entity information and payment details
4. **Account Activation**: Usually takes 24-48 hours for approval

### Required Information
- **Legal Entity Name**: Your legal name or company name
- **D-U-N-S Number**: Required for organizations (obtain from Dun & Bradstreet)
- **Payment Method**: Credit card for annual fee ($99 USD)
- **Contact Information**: Primary contact details for the account

## Phase 2: App Store Connect Configuration

### Create New App
1. **Navigate to App Store Connect**: https://appstoreconnect.apple.com/
2. **Select "My Apps"** → **"+" button** → **"New App"**
3. **Configure App Details**:
   - **Platforms**: iOS
   - **Name**: IELTS GenAI Prep
   - **Primary Language**: English (U.S.)
   - **Bundle ID**: com.ieltsaiprep.genai
   - **SKU**: ielts-genai-prep-ios

### App Information Setup
```
General Information:
- Category: Education > Language Learning
- Content Rights: Original or Licensed
- Age Rating: 4+ (Educational content)
- Copyright: 2025 IELTS GenAI Prep

Localizations:
- Primary: English (United States)
- Additional: English (United Kingdom), Spanish, French, German, Japanese, Korean, Chinese (Simplified)

App Review Information:
- Contact Email: support@ieltsaiprep.com
- Phone Number: Your contact number
- Review Notes: "Educational IELTS preparation app with AI-powered assessments"
```

## Phase 3: In-App Purchase Configuration

### Product Setup Checklist
For each of the 4 assessment products, create:

#### Academic Speaking Assessment
```
Product Details:
- Product ID: academic_speaking_assessment
- Reference Name: Academic Speaking Assessment
- Type: Non-Consumable
- Price: Tier 36 ($36.00 USD)

Localized Information:
- Display Name: Academic Speaking Assessment
- Description: "Complete IELTS Academic Speaking assessment with AI examiner Maya. Practice natural conversation, receive instant feedback, and get detailed band score evaluation with personalized improvement recommendations."

Review Information:
- Screenshot: Show speaking interface with Maya
- Review Notes: "Unlocks full speaking assessment module with AI conversation practice"
```

#### Academic Writing Assessment
```
Product Details:
- Product ID: academic_writing_assessment
- Reference Name: Academic Writing Assessment
- Type: Non-Consumable
- Price: Tier 36 ($36.00 USD)

Localized Information:
- Display Name: Academic Writing Assessment
- Description: "IELTS Academic Writing Tasks 1 & 2 with comprehensive AI evaluation. Get detailed feedback on task achievement, coherence and cohesion, lexical resource, and grammatical range and accuracy."

Review Information:
- Screenshot: Show writing interface and feedback system
- Review Notes: "Unlocks academic writing assessment with detailed AI feedback"
```

#### General Speaking Assessment
```
Product Details:
- Product ID: general_speaking_assessment
- Reference Name: General Training Speaking Assessment
- Type: Non-Consumable
- Price: Tier 36 ($36.00 USD)

Localized Information:
- Display Name: General Training Speaking
- Description: "IELTS General Training Speaking assessment focusing on everyday topics and practical communication. Practice with AI examiner Maya and receive comprehensive feedback on fluency, pronunciation, and vocabulary usage."

Review Information:
- Screenshot: Show general speaking scenarios
- Review Notes: "Unlocks general training speaking module"
```

#### General Writing Assessment
```
Product Details:
- Product ID: general_writing_assessment
- Reference Name: General Training Writing Assessment
- Type: Non-Consumable
- Price: Tier 36 ($36.00 USD)

Localized Information:
- Display Name: General Training Writing
- Description: "IELTS General Training Writing assessment covering letter writing and essay composition. Receive expert AI feedback on task response, coherence, vocabulary, and grammar with band score predictions."

Review Information:
- Screenshot: Show writing tasks and scoring
- Review Notes: "Unlocks general training writing assessment"
```

### Tax and Banking Setup
1. **Agreements, Tax, and Banking**: Complete all required agreements
2. **Tax Information**: Provide tax documentation for your jurisdiction
3. **Banking Information**: Add bank account for revenue collection (required even for testing)

## Phase 4: Xcode Project Configuration

### Bundle Identifier Setup
1. **Open Xcode** → **Create New Project** → **iOS App**
2. **Set Bundle Identifier**: `com.ieltsaiprep.genai`
3. **Team Selection**: Choose your Developer Account team
4. **Capabilities Configuration**:
   - In-App Purchase: Enable
   - Background Modes: Audio, Background Processing
   - Camera: Enable (for QR scanning)
   - Microphone: Enable (for speaking assessments)

### Signing & Capabilities
```
Automatic Signing: Enabled
Team: [Your Developer Team]
Bundle Identifier: com.ieltsaiprep.genai

Required Capabilities:
✓ In-App Purchase
✓ Background Modes (Audio, Background Processing)
✓ Camera Usage
✓ Microphone Usage
✓ Speech Recognition
```

## Phase 5: Testing Configuration

### Sandbox Testing Environment
1. **Create Sandbox Testers**:
   - Go to App Store Connect → Users and Access → Sandbox Testers
   - Add test accounts with different regions
   - Use format: test.us@ieltsaiprep.com, test.eu@ieltsaiprep.com, etc.

### Test Account Configuration
```
Sandbox Test Accounts:
- test.us@ieltsaiprep.com (United States)
- test.uk@ieltsaiprep.com (United Kingdom)  
- test.ca@ieltsaiprep.com (Canada)
- test.au@ieltsaiprep.com (Australia)
- test.eu@ieltsaiprep.com (Germany - EU testing)
- test.jp@ieltsaiprep.com (Japan)

Password: TestIELTS2025!
Region: Set appropriate regions for each account
```

### TestFlight Beta Configuration
1. **Create Beta Groups**:
   - Internal Testing: Development team (up to 100 users)
   - External Testing: Beta users (up to 10,000 users)

2. **Beta Information**:
   - **Test Information**: "Testing IELTS GenAI Prep mobile app with QR authentication and in-app purchases"
   - **What to Test**: "Purchase flow, QR authentication, speaking assessments with Maya AI"
   - **Feedback Email**: beta@ieltsaiprep.com

## Phase 6: Complete Testing Scenarios

### Scenario 1: In-App Purchase Flow
```
Test Steps:
1. Launch app in iOS Simulator/Device
2. Create user account or log in
3. Navigate to assessment selection
4. Tap "Purchase Academic Speaking Assessment"
5. Complete purchase using sandbox account
6. Verify purchase completion and QR code generation
7. Test QR code scanning on ieltsaiprep.com
8. Verify website access to purchased assessment

Expected Results:
✓ Purchase completes successfully
✓ QR code appears in modal
✓ Website authenticates user via QR
✓ Assessment unlocked on website
```

### Scenario 2: Cross-Device Authentication
```
Test Steps:
1. Complete purchase on iPhone
2. Generate QR code
3. Open ieltsaiprep.com on laptop/desktop
4. Scan QR code from iPhone
5. Verify automatic login on website
6. Access purchased assessment

Expected Results:
✓ QR code scans successfully
✓ Website detects authentication
✓ User logged in within 10 seconds
✓ Assessment accessible immediately
```

### Scenario 3: Purchase Restoration
```
Test Steps:
1. Complete purchase on device A
2. Install app on device B (same Apple ID)
3. Tap "Restore Purchases"
4. Verify all purchased assessments restored
5. Generate new QR code for website access

Expected Results:
✓ All purchases restored correctly
✓ Assessment modules unlocked
✓ QR generation works for restored purchases
```

### Scenario 4: Regional API Testing
```
Test Steps:
1. Test app from different geographic locations
2. Verify API routing to optimal region
3. Confirm Nova Sonic streaming performance
4. Test assessment submission and feedback

Expected Results:
✓ App connects to nearest regional API
✓ Speech streaming maintains quality
✓ Assessment results sync globally
✓ Consistent user experience across regions
```

## Phase 7: Production Deployment Checklist

### Pre-Submission Requirements
- [ ] All 4 in-app products created and approved
- [ ] Sandbox testing completed successfully
- [ ] TestFlight beta testing completed
- [ ] App screenshots captured for all device sizes
- [ ] App Store description finalized
- [ ] Privacy Policy published at https://ieltsaiprep.com/privacy
- [ ] Terms of Service published at https://ieltsaiprep.com/terms
- [ ] Customer support contact configured

### App Store Review Preparation
```
Review Information:
- App Review Contact: support@ieltsaiprep.com
- Phone Number: Your support phone number
- Review Notes: "IELTS preparation app with AI assessments. In-app purchases unlock individual assessment modules. QR authentication connects mobile purchases to web platform for seamless experience."

Demo Account (if needed):
- Username: reviewer@ieltsaiprep.com
- Password: ReviewAccess2025!
- Instructions: "Complete any in-app purchase to test QR authentication flow"
```

### Expected Review Timeline
- **Initial Submission**: 24-48 hours for review
- **If Rejected**: Address issues and resubmit (usually 24 hours)
- **Approval**: App becomes available immediately after approval

## Phase 8: Launch Monitoring

### Post-Launch Metrics to Track
1. **Purchase Conversion**: Rate of users completing purchases
2. **QR Authentication**: Success rate of QR code scanning
3. **Regional Performance**: API response times by region
4. **Assessment Completion**: User engagement with purchased content
5. **Support Tickets**: Common issues requiring assistance

### Critical Success Indicators
- **Purchase Flow**: >95% completion rate
- **QR Authentication**: >98% success rate
- **API Performance**: <2 second response times globally
- **User Rating**: Maintain >4.5 stars
- **Revenue**: Track individual assessment sales

This comprehensive testing approach ensures your Apple Developer account setup leads to a successful app launch with seamless QR authentication and reliable in-app purchase functionality.