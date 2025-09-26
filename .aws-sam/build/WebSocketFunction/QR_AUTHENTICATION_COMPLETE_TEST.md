# Complete User Testing Guide - QR Authentication Flow

## Testing Environment Setup
- **Website**: Your current .replit domain
- **Mobile App**: iOS Simulator with Apple Developer sandbox
- **Backend**: Current Flask development server
- **Purchase System**: Apple Developer sandbox testing

## User Journey Test Scenarios

### Scenario 1: New User Complete Flow
**User Perspective**: "I want to buy Academic Speaking Assessment and use it on the website"

#### Step 1: Mobile App Download & Registration
```
Action: User downloads IELTS GenAI Prep from TestFlight
Expected: App launches successfully
Test: Launch iOS app in simulator

Action: User creates account with email/password
Expected: Account created, user logged in
Test: Register with test.user@example.com
```

#### Step 2: Browse & Purchase Assessment
```
Action: User browses available assessments
Expected: Sees 4 assessment options at $36 each
Test: Navigate to assessment selection screen

Action: User taps "Purchase Academic Speaking Assessment"
Expected: iOS purchase dialog appears
Test: Tap purchase button, use sandbox Apple ID

Action: User completes purchase with Touch ID/Face ID
Expected: Purchase succeeds, QR code modal appears
Test: Complete sandbox purchase flow
```

#### Step 3: QR Code Generation & Display
```
Action: Purchase completes successfully
Expected: Modal shows QR code with instructions
Test: Verify QR code image displays properly

Action: User sees "Scan this code on ieltsaiprep.com"
Expected: Clear instructions with 10-minute expiry warning
Test: Check modal content and countdown timer
```

#### Step 4: Website Authentication
```
Action: User opens laptop/desktop browser
Expected: Can navigate to your .replit domain
Test: Open https://[your-replit-domain].replit.dev

Action: User navigates to QR login page
Expected: Sees "Scan QR Code to Login" interface
Test: Visit /qr-login route

Action: User holds phone QR code up to laptop camera
Expected: Website detects and scans QR code
Test: Use QR code scanner or manually enter token
```

#### Step 5: Automatic Website Login
```
Action: QR code scanned successfully
Expected: Automatic redirect to profile/assessments page
Test: Verify authentication happens within 3 seconds

Action: User sees "Welcome! Assessment unlocked"
Expected: Academic Speaking Assessment now available
Test: Check assessment list shows purchased item

Action: User clicks "Start Academic Speaking Assessment"
Expected: Assessment interface loads with Maya AI
Test: Verify assessment is accessible and functional
```

### Scenario 2: Returning User with Multiple Purchases
**User Perspective**: "I already bought Academic Speaking, now I want Academic Writing too"

#### Step 1: Restore Previous Purchases
```
Action: User opens app on new device
Expected: "Restore Purchases" option available
Test: Simulate new device installation

Action: User taps "Restore Purchases"
Expected: Previous Academic Speaking purchase restored
Test: Verify purchase restoration works

Action: User sees Academic Speaking already owned
Expected: "Purchased" badge shows instead of price
Test: Check UI reflects ownership status
```

#### Step 2: Additional Purchase
```
Action: User purchases Academic Writing Assessment
Expected: Second purchase completes normally
Test: Complete second sandbox purchase

Action: New QR code generated for website access
Expected: QR code includes both assessments
Test: Verify QR token includes all owned assessments
```

#### Step 3: Website Shows All Assessments
```
Action: User scans new QR code on website
Expected: Both Academic Speaking and Writing available
Test: Check assessment list shows both purchases

Action: User can access either assessment
Expected: Both work independently
Test: Navigate between different assessments
```

### Scenario 3: QR Code Expiry Testing
**User Perspective**: "What happens if I wait too long to scan the QR code?"

#### Step 1: Generate QR Code
```
Action: User completes purchase, gets QR code
Expected: QR code shows with 10-minute countdown
Test: Note the exact expiry time

Action: User waits 11 minutes before scanning
Expected: QR code should be expired
Test: Wait for expiry, then attempt scan
```

#### Step 2: Handle Expired QR Code
```
Action: User tries to scan expired QR code
Expected: Website shows "QR code expired" message
Test: Verify proper error handling

Action: User returns to mobile app
Expected: Option to generate new QR code
Test: Check if "Generate New QR" button appears

Action: User generates fresh QR code
Expected: New QR code works normally
Test: Complete fresh authentication flow
```

### Scenario 4: Cross-Platform Session Management
**User Perspective**: "I want to use assessments on multiple devices"

#### Step 1: Mobile Purchase
```
Action: User purchases on iPhone
Expected: Assessment unlocked on iPhone
Test: Complete purchase on mobile device

Action: User generates QR for website access
Expected: QR code works on any computer
Test: Use QR code on different computers
```

#### Step 2: Session Persistence
```
Action: User authenticates on laptop via QR
Expected: 1-hour session created on laptop
Test: Verify website session stays active

Action: User closes laptop, returns later
Expected: Session still active within 1 hour
Test: Check session persistence across browser restarts

Action: User tries to access after 1 hour
Expected: Prompted to scan new QR code
Test: Verify session expiry works correctly
```

### Scenario 5: Error Handling & Recovery
**User Perspective**: "What if something goes wrong?"

#### Step 1: Network Issues
```
Action: User purchases with poor internet
Expected: Purchase either completes or fails cleanly
Test: Simulate network interruption during purchase

Action: Purchase fails mid-transaction
Expected: Clear error message, retry option
Test: Verify graceful failure handling

Action: User retries purchase
Expected: Purchase completes on retry
Test: Ensure retry mechanism works
```

#### Step 2: QR Scanning Issues
```
Action: User has trouble scanning QR code
Expected: Clear troubleshooting instructions
Test: Try scanning from different angles/distances

Action: QR code appears blurry on phone
Expected: Option to view larger QR code
Test: Check QR code display options

Action: Website camera doesn't work
Expected: Manual token entry option
Test: Verify fallback authentication method
```

## Testing Checklist

### Pre-Test Setup
- [ ] Apple Developer sandbox account configured
- [ ] Test Apple ID created for purchases
- [ ] .replit development server running
- [ ] iOS Simulator with test app installed
- [ ] Camera/microphone permissions granted

### Core Flow Tests
- [ ] User registration and login works
- [ ] All 4 assessment products display correctly
- [ ] Purchase flow completes successfully
- [ ] QR code generates and displays properly
- [ ] Website QR scanner works reliably
- [ ] Authentication redirects to correct page
- [ ] Purchased assessments are accessible

### Edge Case Tests
- [ ] QR code expiry handling
- [ ] Session timeout behavior
- [ ] Purchase restoration functionality
- [ ] Multiple device authentication
- [ ] Network interruption recovery
- [ ] Invalid QR code handling

### User Experience Tests
- [ ] Instructions are clear at each step
- [ ] Error messages are helpful
- [ ] Loading states are informative
- [ ] Success confirmations are obvious
- [ ] Navigation flows logically

### Performance Tests
- [ ] QR code generation takes <3 seconds
- [ ] Website authentication takes <5 seconds
- [ ] Assessment loading takes <10 seconds
- [ ] No crashes during normal usage
- [ ] Smooth transitions between states

## Test Results Documentation

### Pass/Fail Criteria
- **PASS**: User completes full flow without confusion
- **FAIL**: User gets stuck or confused at any step
- **IMPROVEMENT NEEDED**: User completes but suggests enhancements

### Common Issues to Watch For
1. **QR Code Quality**: Ensure codes scan reliably
2. **Timing Issues**: Verify expiry warnings are clear
3. **Error Messages**: Check all error states have helpful text
4. **Navigation**: Ensure users always know next steps
5. **Performance**: Monitor loading times and responsiveness

This testing approach ensures the complete user experience works seamlessly before deploying to AWS production environment.