# Custom Domain Setup - ieltsaiprep.com

## Domain Configuration

Your purchased domain: **ieltsaiprep.com**
AWS Lambda Backend: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod

## Step 1: Configure Custom Domain in AWS API Gateway

1. **Go to AWS API Gateway Console**
   - Navigate to API Gateway in AWS Console
   - Click on "Custom domain names"
   - Click "Create domain name"

2. **Domain Configuration:**
   - Domain name: `ieltsaiprep.com`
   - Certificate: Request or import SSL certificate
   - Endpoint type: Regional
   - API mappings: Map to your existing API Gateway

## Step 2: Update DNS Records

In your domain registrar (where you bought ieltsaiprep.com):

### A Record
```
Type: A
Name: @
Value: [AWS API Gateway IP - will be provided after custom domain creation]
TTL: 300
```

### CNAME Record  
```
Type: CNAME
Name: www
Value: ieltsaiprep.com
TTL: 300
```

## Step 3: SSL Certificate

AWS will automatically provision an SSL certificate for ieltsaiprep.com through ACM (AWS Certificate Manager).

## Step 4: Mobile App Configuration Update

Update mobile app endpoints to use custom domain:

### iOS Configuration (ios/App/App/capacitor.config.json)
```json
{
  "server": {
    "url": "https://ieltsaiprep.com"
  }
}
```

### Android Configuration (android/app/src/main/assets/capacitor.config.json)
```json
{
  "server": {
    "url": "https://ieltsaiprep.com"
  }
}
```

## Expected Timeline

- DNS propagation: 24-48 hours
- SSL certificate validation: 5-10 minutes
- Custom domain active: After DNS propagation

## Testing Custom Domain

Once configured, test these endpoints:
- https://ieltsaiprep.com (homepage)
- https://ieltsaiprep.com/login (login page)
- https://ieltsaiprep.com/privacy-policy (privacy policy)
- https://ieltsaiprep.com/terms-of-service (terms of service)

Your mobile app will then use the professional ieltsaiprep.com domain instead of the AWS Lambda URL.