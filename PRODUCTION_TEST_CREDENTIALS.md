# Production Test Credentials

## Working Production Login Credentials

Based on the production DynamoDB scan, these users exist in the production database:

### Option 1: Simple Test Account
- **Email**: `simpletest@ieltsaiprep.com`
- **Password**: `test123`

### Option 2: Production Test Account
- **Email**: `prodtest@ieltsaiprep.com`
- **Password**: `test123`

### Option 3: Nova Test Account
- **Email**: `novatest@ieltsaiprep.com`
- **Password**: `test123`

### Option 4: Bcrypt Test Account
- **Email**: `bcrypttest@ieltsaiprep.com`
- **Password**: `test123`

## Important Notes:

1. **reCAPTCHA Required**: The production login requires completing the reCAPTCHA checkbox
2. **GDPR Checkboxes**: Both Privacy Policy and Terms of Service must be checked
3. **Production System**: These credentials are configured in the production DynamoDB
4. **Assessment Testing**: Once logged in, you can test all 4 assessment types:
   - Academic Writing
   - General Writing  
   - Academic Speaking
   - General Speaking

## If Login Still Fails:

The production system may have been updated since the last credential sync. In that case:

1. Try completing the reCAPTCHA verification carefully
2. Ensure both GDPR checkboxes are checked
3. Check that JavaScript is enabled in your browser
4. Clear browser cache and cookies for ieltsaiprep.com

## Testing Nova Micro and Nova Sonic:

Once logged in successfully:
- **Nova Micro**: Test writing assessments (Academic/General Writing)
- **Nova Sonic**: Test speaking assessments with Maya AI examiner
- **Session Duration**: 1 hour login session
- **Assessment Attempts**: 4 attempts per assessment type