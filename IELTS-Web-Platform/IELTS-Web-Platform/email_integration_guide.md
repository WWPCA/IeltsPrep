# Email Service Integration Guide

## Overview
This guide shows how to integrate the welcome email service with your iOS and Android apps.

## AWS Lambda Function
The email service is deployed as `ielts-email-service` Lambda function that sends welcome emails via AWS SES.

### API Endpoint
```
POST https://your-api-gateway-url/prod/send-email
```

### Request Format
```json
{
  "type": "welcome",
  "email": "user@example.com",
  "name": "User Name" // optional
}
```

## iOS Integration (Swift)

### Add to your registration success handler:

```swift
import Foundation

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
            print("Error serializing JSON: \(error)")
            completion(false)
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Email service error: \(error)")
                completion(false)
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                completion(httpResponse.statusCode == 200)
            } else {
                completion(false)
            }
        }.resume()
    }
}

// Usage in your registration completion:
EmailService.shared.sendWelcomeEmail(to: userEmail, name: userName) { success in
    DispatchQueue.main.async {
        if success {
            print("Welcome email sent successfully")
        } else {
            print("Failed to send welcome email")
        }
    }
}
```

## Android Integration (Java)

### Add to your MainActivity.java or registration handler:

```java
import okhttp3.*;
import org.json.JSONObject;
import java.io.IOException;

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
            e.printStackTrace();
            callback.onResult(false);
        }
    }
    
    public interface EmailCallback {
        void onResult(boolean success);
    }
}

// Usage in your registration completion:
EmailService emailService = new EmailService();
emailService.sendWelcomeEmail(userEmail, userName, new EmailService.EmailCallback() {
    @Override
    public void onResult(boolean success) {
        runOnUiThread(() -> {
            if (success) {
                Log.d("EmailService", "Welcome email sent successfully");
            } else {
                Log.e("EmailService", "Failed to send welcome email");
            }
        });
    }
});
```

## Deployment Steps

1. **Deploy the Lambda function:**
   ```bash
   python deploy_backend_complete.py
   ```

2. **Update API Gateway URL:**
   - Replace `your-api-gateway-url` in the code above with your actual API Gateway endpoint
   - You can find this in the AWS Console under API Gateway

3. **Test the integration:**
   - Use the test scripts provided to verify email sending works
   - Check AWS SES sending statistics

## Required Dependencies

### iOS
- No additional dependencies required (uses URLSession)

### Android
- Add to `app/build.gradle`:
```gradle
implementation 'com.squareup.okhttp3:okhttp:4.10.0'
```

## Error Handling

The email service includes comprehensive error handling:
- Invalid email addresses
- AWS SES service errors
- Network connectivity issues
- Lambda function errors

Monitor CloudWatch logs for detailed error information.

## Testing

Use the provided test scripts to verify email functionality:
- `test_android_app.py` - Tests Android integration
- `test_ios_app.py` - Tests iOS integration

Both scripts include email service testing.