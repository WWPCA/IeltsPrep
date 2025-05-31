# Actual Error Scenarios for IELTS GenAI Prep

## Real Error Cases That Can Occur

### 1. Authentication & Security Issues (Keep as 'danger' alerts)
- **User not logged in**: Redirect to login
- **Email not verified**: "Please verify your email address before accessing assessments"
- **Account not activated**: "Please complete your account setup to access assessments"
- **Login failures**: "Invalid email or password"
- **Password validation**: Show specific validation errors
- **Security verification failures**: "Security verification failed. Please try again."

### 2. Navigation & URL Manipulation Issues
- **Direct URL manipulation**: User types assessment URLs manually
  - Message: "Assessment not available. Please start from your dashboard."
- **Accessing assessment without proper assignment flow**
  - Message: "Assessment not found. Please start an assessment from your dashboard."
- **Invalid assessment type in URL**
  - Message: "Assessment not found. Please start an assessment from your dashboard."

### 3. System/Technical Issues  
- **Assessment not found in database**: Data corruption or missing assessment
  - Message: "Assessment not available. Please start from your dashboard."
- **Database connection issues**: Connection timeout or failure
  - Message: "Service temporarily unavailable. Please try again."
- **AI service unavailable**: AWS Bedrock or other AI services down
  - Message: "Assessment service is temporarily down. Please try again later."

### 4. User Flow Edge Cases
- **User already completed their purchased assessment**: Trying to retake
  - Message: "You've already completed this assessment."
- **Session timeout during assessment**: User session expires
  - Message: "Your session has expired. Please log in again."
- **Attempting to access unassigned assessment**: Technical issue with assignment
  - Message: "Assessment not available. Please start from your dashboard."

## Error Cases That DON'T Occur (Due to System Design)

### ❌ No Package Purchased
- **Why it doesn't happen**: Users must purchase before creating accounts
- **System prevents**: No account creation without purchase

### ❌ Package Expired  
- **Why it doesn't happen**: Packages are one-time use, not time-based
- **System design**: No expiration dates, only usage tracking

### ❌ Wrong Assessment Type Access
- **Why it doesn't happen**: Users can only access what they purchased through cart
- **System prevents**: Assessment assignment only gives access to purchased types

## Updated Error Message Strategy

1. **Never mention purchasing** - users already purchased to get accounts
2. **Focus on navigation guidance** - direct users back to dashboard
3. **Keep security alerts prominent** - authentication issues need attention  
4. **Use 'info' level for navigation** - blue alerts for guidance
5. **Use 'danger' level for security** - red alerts for login/security issues
6. **Assume technical issues** - if user reaches wrong assessment, it's likely URL manipulation or system error

## Implementation
All error messages now reflect the actual user flow where:
- Users purchase → Create account → Access assigned assessments
- No scenarios exist for "buy more" since purchase happens before account creation
- Access control errors indicate technical issues or URL manipulation