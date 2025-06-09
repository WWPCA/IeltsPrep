# IELTS GenAI Prep Mobile App Setup Guide

## Current Status
✅ Capacitor successfully installed and configured
✅ iOS and Android platforms added
✅ Mobile plugins integrated (splash screen, status bar, app, device, network)
✅ App icon created
✅ Configuration optimized for production

## App Configuration
- **App ID**: com.ieltsaiprep.app
- **App Name**: IELTS GenAI Prep
- **Server URL**: https://ieltsaiprep.com
- **Platform**: Capacitor 7.3.0

## Building Your Mobile Apps

### For iOS (Apple App Store)
```bash
# Sync latest changes
npx cap sync ios

# Open Xcode project
npx cap open ios
```

**In Xcode:**
1. Select your development team
2. Set deployment target to iOS 13.0+
3. Configure app signing & capabilities
4. Build and archive for App Store distribution

### For Android (Google Play Store)
```bash
# Sync latest changes
npx cap sync android

# Open Android Studio
npx cap open android
```

**In Android Studio:**
1. Build → Generate Signed Bundle/APK
2. Choose Android App Bundle (AAB)
3. Create/use your keystore
4. Select release build variant

## App Store Submission Requirements

### Apple App Store
1. **Developer Account**: $99/year
2. **App Store Connect**: Upload your .ipa file
3. **Required Info**:
   - App description highlighting Nova Sonic speech technology
   - Screenshots (6.7", 6.5", 5.5" iPhone sizes)
   - Privacy policy URL: https://ieltsaiprep.com/privacy-policy
   - Support URL: https://ieltsaiprep.com/contact
   - App category: Education
   - Age rating: 4+ (Educational content)

### Google Play Store
1. **Developer Account**: $25 one-time fee
2. **Play Console**: Upload your .aab file
3. **Required Info**:
   - App description emphasizing AI assessment features
   - Screenshots (Phone, 7" tablet, 10" tablet)
   - Privacy policy URL: https://ieltsaiprep.com/privacy-policy
   - Contact email: support@ieltsaiprep.com
   - Content rating: Everyone (Educational)

## App Store Optimization (ASO)

### Title & Description Template
**Title**: "IELTS GenAI Prep - AI Speaking & Writing Assessment"

**Description**:
"Master IELTS with the world's only GenAI-powered assessment platform featuring Nova Sonic speech-to-speech technology.

🎯 Features:
• TrueScore® & ClearScore® AI assessment technology
• Maya AI examiner for realistic speaking practice
• Real-time bidirectional speech conversations
• Detailed feedback for writing and speaking
• Academic and General Training modules

📱 Assessment Types:
• Academic Speaking with Maya AI examiner
• Academic Writing with instant AI feedback
• General Training Speaking practice
• General Training Writing assessment

🌟 Why Choose IELTS GenAI Prep:
• Industry-leading Nova Sonic speech technology
• Authentic IELTS test simulation
• Secure payment processing
• Progress tracking and analytics
• Mobile-optimized learning experience"

### Keywords
- IELTS preparation
- AI English assessment
- Speaking practice
- Writing feedback
- English test prep
- Language learning
- IELTS speaking
- IELTS writing

## Technical Features Maintained
- All Nova Sonic speech-to-speech functionality preserved
- Stripe payment processing works seamlessly
- User authentication and profiles
- Assessment recovery system
- Real-time progress tracking
- Particle globe visualization for speech

## Web App Independence
Your web application at https://ieltsaiprep.com continues to function independently. The mobile apps are essentially native containers that load your existing web platform.

## Next Steps for App Store Release
1. Set up Apple Developer and Google Play Developer accounts
2. Complete app store listing information
3. Generate production builds using the commands above
4. Submit for review (typically 1-7 days approval time)
5. Launch and monitor user feedback

## Support
For technical assistance with mobile app deployment, contact your development team or refer to Capacitor documentation at https://capacitorjs.com/docs