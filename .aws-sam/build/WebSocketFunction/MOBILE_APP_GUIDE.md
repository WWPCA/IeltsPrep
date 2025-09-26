# Mobile App Integration Guide
## Capacitor 7.3.0 with AWS Lambda Backend

### Architecture Overview
Your Capacitor mobile app now connects to AWS Lambda API Gateway endpoints instead of the Flask server. The app maintains native functionality while communicating with the serverless backend across multiple regions.

### Key Files Updated
- `capacitor.config.json` - Updated server configuration
- `mobile_api_client.js` - Regional API routing client
- `mobile_purchase_integration.js` - In-app purchase verification
- Native iOS/Android configurations for app store distribution

### Regional API Routing
The mobile app automatically detects user region and routes requests to the nearest Lambda endpoint:

```javascript
// Regional endpoints automatically selected
US/Americas: https://api-us-east-1.ieltsaiprep.com
Europe: https://api-eu-west-1.ieltsaiprep.com
Asia-Pacific: https://api-ap-southeast-1.ieltsaiprep.com
```

### Nova Sonic Global Access
All speech assessment requests route to us-east-1 regardless of user location:
- Extended timeout (20 seconds) for global latency
- Exponential backoff retry (1s, 2s, 4s)
- User notification about North America routing
- Only transcript stored (no voice data)

### In-App Purchase Integration
Products available at $36 each:
- `academic_speaking` - Academic Speaking Assessment
- `academic_writing` - Academic Writing Assessment  
- `general_speaking` - General Training Speaking
- `general_writing` - General Training Writing

### Apple App Store Setup
1. Configure products in App Store Connect:
   - Product IDs: `com.ieltsaiprep.academic_speaking`, etc.
   - Pricing: $36.00 USD
   - Availability: Global
2. Add shared secret to Replit Secrets: `APPLE_SHARED_SECRET`
3. Receipt verification handled by Lambda backend

### Google Play Store Setup
1. Configure products in Google Play Console:
   - Product IDs match Apple equivalents
   - Pricing: $36.00 USD equivalent
   - Global distribution enabled
2. Add service account JSON to Replit Secrets: `GOOGLE_SERVICE_ACCOUNT_JSON`
3. Purchase verification via Play Billing API

### Capacitor Configuration Changes
```json
{
  "server": {
    "url": "https://api.ieltsaiprep.com",
    "cleartext": false
  },
  "plugins": {
    "Device": { "enabled": true },
    "Network": { "enabled": true },
    "Toast": { "enabled": true }
  }
}
```

### Session Management
- Sessions stored in device localStorage
- Session tokens verified with Lambda backend
- Regional session synchronization via DynamoDB Global Tables

### Data Storage Policy
- User assessments: Written text only in DynamoDB
- Voice data: Processed by Nova Sonic but not stored
- Purchase receipts: Verified and logged for audit
- Session data: Cached in regional ElastiCache Redis

### Native Features Maintained
- Microphone access for speech assessments
- Device information and network detection
- Native splash screen and status bar
- Toast notifications for user feedback
- In-app purchase flows (Apple/Google)

### Testing Procedures
1. Test regional API routing with VPN from different countries
2. Verify Nova Sonic routing to us-east-1 from all regions
3. Test in-app purchase flows on both iOS and Android
4. Validate session persistence across app restarts
5. Check error handling for network issues and Lambda cold starts

### Performance Optimizations
- Automatic region detection based on device timezone
- Retry logic for Lambda cold starts
- Local caching of user preferences
- Progressive loading for assessment content
- Offline capability for completed assessments

### Security Features
- HTTPS-only communication with Lambda endpoints
- Receipt verification prevents purchase fraud
- Session tokens with expiration
- Input validation before API calls
- No sensitive data stored locally

### Deployment Checklist
- [ ] Configure regional API Gateway endpoints
- [ ] Set up app store product configurations
- [ ] Add payment verification secrets to environment
- [ ] Test purchase flows in sandbox environments
- [ ] Validate global Nova Sonic routing
- [ ] Submit apps to Apple App Store and Google Play
- [ ] Monitor CloudWatch logs for issues

Your mobile app now leverages the full power of AWS Lambda's global infrastructure while maintaining the native user experience expected from premium app store applications.