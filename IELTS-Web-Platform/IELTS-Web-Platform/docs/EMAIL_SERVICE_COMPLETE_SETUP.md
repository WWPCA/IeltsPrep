# IELTS AI Prep Email Service - Complete Setup Guide

## Overview
This guide sets up the complete email service for sending welcome emails to users when they register on your iOS or Android apps.

## 🎯 What You Get
- **Professional welcome email** with your exact content and branding
- **AWS SES integration** using donotreply@ieltsaiprep.com
- **Lambda function** for reliable email delivery
- **API Gateway endpoint** for mobile app integration
- **Cross-platform support** for both iOS and Android

## 📧 Email Details
- **From:** donotreply@ieltsaiprep.com
- **Subject:** 🎉 Welcome to IELTS AI Prep - Your Journey to Success Starts Now!
- **Format:** Professional HTML email with plain text fallback
- **Content:** Your exact welcome message with proper formatting

## 🚀 Quick Setup (3 Steps)

### Step 1: Deploy Backend Infrastructure
```bash
python deploy_backend_complete.py
```
This creates all AWS resources including IAM roles, DynamoDB tables, and Lambda functions.

### Step 2: Set Up Email Service
```bash
python setup_email_service.py
```
This configures AWS SES, deploys the email Lambda function, and sets up the API endpoint.

### Step 3: Test Email Service
```bash
python test_email_service.py
```
This verifies everything works and sends a test email to your address.

## 📱 Mobile App Integration

### iOS Integration
Add this code to your registration success handler:

```swift
class EmailService {
    static let shared = EmailService()
    private let apiEndpoint = "https://your-api-gateway-url/prod/send-email"
    
    func sendWelcomeEmail(to email: String, name: String? = nil, completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: apiEndpoint) else {
            completion(false)
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload: [String: Any] = [
            "type": "welcome",
            "email": email,
            "name": name ?? ""
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        } catch {
            completion(false)
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let httpResponse = response as? HTTPURLResponse {
                completion(httpResponse.statusCode == 200)
            } else {
                completion(false)
            }
        }.resume()
    }
}

// Usage after successful registration:
EmailService.shared.sendWelcomeEmail(to: userEmail, name: userName) { success in
    if success {
        print("Welcome email sent!")
    }
}
```

### Android Integration
Add this to your MainActivity.java or registration handler:

```java
// Add to app/build.gradle:
// implementation 'com.squareup.okhttp3:okhttp:4.10.0'

import okhttp3.*;
import org.json.JSONObject;

public class EmailService {
    private static final String API_ENDPOINT = "https://your-api-gateway-url/prod/send-email";
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    private OkHttpClient client = new OkHttpClient();
    
    public void sendWelcomeEmail(String email, String name, EmailCallback callback) {
        try {
            JSONObject payload = new JSONObject();
            payload.put("type", "welcome");
            payload.put("email", email);
            if (name != null && !name.isEmpty()) {
                payload.put("name", name);
            }
            
            RequestBody body = RequestBody.create(payload.toString(), JSON);
            Request request = new Request.Builder()
                    .url(API_ENDPOINT)
                    .post(body)
                    .build();
            
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    callback.onResult(false);
                }
                
                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    callback.onResult(response.isSuccessful());
                }
            });
            
        } catch (Exception e) {
            callback.onResult(false);
        }
    }
    
    public interface EmailCallback {
        void onResult(boolean success);
    }
}

// Usage after successful registration:
EmailService emailService = new EmailService();
emailService.sendWelcomeEmail(userEmail, userName, success -> {
    if (success) {
        Log.d("EmailService", "Welcome email sent!");
    }
});
```

## 🔧 Configuration Steps

### 1. AWS SES Domain Verification
After running the setup script, you'll receive verification emails:
1. Check your email for AWS SES verification links
2. Click the verification links for both domain and email
3. Wait for verification to complete (can take up to 72 hours)

### 2. Update API Endpoint URLs
After deployment, replace `your-api-gateway-url` in your mobile app code with the actual endpoint URL shown in the setup script output.

### 3. Test Integration
Use the test script to verify everything works before releasing your app.

## 📊 Email Content Preview

**Subject:** 🎉 Welcome to IELTS AI Prep - Your Journey to Success Starts Now!

**Content includes:**
- Welcome message with congratulations
- Cross-platform access information
- Feature highlights (AI assessments, personalized learning, 24/7 availability)
- Motivational content about their IELTS journey
- Call-to-action to visit www.ieltsaiprep.com
- Professional closing from "The IELTS AI Prep Team"

## 🛠️ Files Created

### Core Files
- `backend/lambda_functions/email_service.py` - Email service Lambda function
- `setup_email_service.py` - Email service deployment script
- `test_email_service.py` - Email service testing script
- `backend/email_integration_guide.md` - Detailed integration guide

### Updated Files
- `deploy_backend_complete.py` - Added email service deployment
- IAM role updated with SES permissions

## 🔍 Testing & Verification

### Automated Tests
```bash
python test_email_service.py
```

Tests include:
- SES configuration verification
- Lambda function testing
- Real email sending test
- API Gateway endpoint testing

### Manual Testing
1. Register a new user in your app
2. Check that the welcome email is received
3. Verify email formatting and content
4. Test on both iOS and Android

## 🚨 Troubleshooting

### Common Issues
1. **SES not verified:** Check email for verification links
2. **Lambda deployment failed:** Ensure IAM role exists
3. **API Gateway error:** Check Lambda permissions
4. **Email not received:** Check spam folder, verify SES status

### Debug Commands
```bash
# Check SES verification status
aws ses get-identity-verification-attributes --identities donotreply@ieltsaiprep.com

# Test Lambda function directly
aws lambda invoke --function-name ielts-email-service --payload '{"type":"welcome","email":"test@example.com"}' response.json

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix /aws/apigateway/
```

## 📈 Monitoring

### CloudWatch Metrics
- Lambda function invocations
- Email delivery success/failure rates
- API Gateway request counts
- Error logs and debugging information

### SES Statistics
- Bounce rates
- Complaint rates
- Delivery statistics
- Reputation monitoring

## 🔒 Security Features

- **No-reply email address** prevents spam responses
- **IAM role-based permissions** for secure AWS access
- **API Gateway throttling** prevents abuse
- **Input validation** in Lambda function
- **Error handling** without exposing sensitive information

## 🎉 Success Criteria

After setup completion, you should have:
- ✅ SES domain and email verified
- ✅ Lambda function deployed and working
- ✅ API Gateway endpoint accessible
- ✅ Test email successfully sent and received
- ✅ Mobile apps integrated and tested

Your users will now receive professional welcome emails immediately upon registration!