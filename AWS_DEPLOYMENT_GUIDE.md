# AWS Lambda Deployment Guide - IELTS GenAI Prep Platform

## 🎯 Overview

This guide provides step-by-step instructions for deploying the IELTS GenAI Prep platform to AWS Lambda with full production readiness, including API Gateway, DynamoDB, Secrets Manager, and mobile app support.

## ✅ CRITICAL FIXES COMPLETED

1. **AWS Secrets Manager Bug Fixed** ✅
   - Fixed SecretName → SecretId parameter
   - All secrets API calls now work correctly

2. **AWS Lambda Handler Created** ✅
   - Custom WSGI adapter for Flask app
   - Handles API Gateway REST and HTTP events
   - WebSocket support for Nova Sonic streaming

3. **Environment Detection Enhanced** ✅
   - Centralized environment_utils.py module
   - Detects AWS Lambda, Replit, and local environments
   - Proper production vs development behavior

4. **CORS Configuration Added** ✅
   - Mobile app support (Capacitor iOS/Android)
   - Cross-origin request handling
   - Preflight OPTIONS support

5. **Serverless Configuration Ready** ✅
   - DynamoDB tables with proper indexes
   - IAM permissions for all AWS services
   - Multi-region deployment support

## 🚀 **PRODUCTION DEPLOYMENT STATUS: READY** 🚀

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, Region (us-east-1), and output format (json)
   ```

2. **SAM CLI installed**
   ```bash
   # Install SAM CLI for Lambda deployment
   # Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
   ```

3. **Python 3.11 and required packages**
   ```bash
   pip install boto3 bcrypt
   ```

## Step 1: Deploy Infrastructure

Run the infrastructure deployment script:

```bash
chmod +x deploy-aws-infrastructure.sh
./deploy-aws-infrastructure.sh
```

This creates:
- DynamoDB tables for users, sessions, assessments, and rubrics
- ElastiCache Redis cluster for session storage
- IAM roles and policies
- CloudWatch log groups

## Step 2: Get ElastiCache Endpoint

Wait 5-10 minutes for ElastiCache cluster creation, then get the endpoint:

```bash
aws elasticache describe-cache-clusters \
    --cache-cluster-id ielts-genai-prep-redis \
    --show-cache-node-info \
    --region us-east-1 \
    --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
    --output text
```

## Step 3: Deploy Lambda Functions

Build and deploy using SAM:

```bash
# Build the application
sam build

# Deploy with parameters
sam deploy \
    --guided \
    --parameter-overrides \
    Environment=production \
    ElastiCacheEndpoint=YOUR_REDIS_ENDPOINT_FROM_STEP_2
```

Follow the prompts to configure:
- Stack name: `ielts-genai-prep`
- AWS Region: `us-east-1`
- Confirm changes before deploy: `Y`
- Allow SAM to create IAM roles: `Y`
- Save parameters to samconfig.toml: `Y`

## Step 4: Populate Assessment Data

Run the data population script:

```bash
# Set environment variables
export AWS_REGION=us-east-1
export STACK_NAME=ielts-genai-prep

# Populate IELTS assessment rubrics
python3 populate-assessment-data.py
```

This populates:
- Academic and General Writing assessment rubrics
- Academic and General Speaking assessment rubrics
- Nova Micro system prompts for writing evaluation
- Nova Sonic system prompts for Maya speaking examiner

## Step 5: Configure Environment Variables

Update your production environment with these variables:

```bash
# Core AWS services
export AWS_REGION=us-east-1
export DYNAMODB_USERS_TABLE=ielts-genai-prep-users
export DYNAMODB_SESSIONS_TABLE=ielts-genai-prep-sessions
export DYNAMODB_ASSESSMENTS_TABLE=ielts-genai-prep-assessments
export DYNAMODB_RUBRICS_TABLE=ielts-genai-prep-rubrics
export ELASTICACHE_ENDPOINT=your-redis-endpoint
export CLOUDWATCH_LOG_GROUP=/aws/lambda/ielts-genai-prep

# Disable mock services for production
unset REPLIT_ENVIRONMENT
```

## Step 6: Test the Deployment

1. **Health Check**
   ```bash
   curl https://your-api-gateway-url/api/health
   ```

2. **User Registration Test**
   ```bash
   curl -X POST https://your-api-gateway-url/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPassword123",
       "confirm_password": "TestPassword123",
       "terms_accepted": true,
       "privacy_accepted": true
     }'
   ```

3. **User Login Test**
   ```bash
   curl -X POST https://your-api-gateway-url/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPassword123"
     }'
   ```

## Step 7: Configure Nova AI Access

Enable Nova Sonic and Nova Micro in your AWS account:

1. **Go to AWS Bedrock Console**
   - Navigate to AWS Bedrock in us-east-1 region
   - Request access to Amazon Nova models:
     - Amazon Nova Sonic v1.0
     - Amazon Nova Micro v1.0

2. **Update IAM Permissions**
   The deployment script already includes Bedrock permissions, but verify:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "bedrock:InvokeModel",
       "bedrock:InvokeModelWithResponseStream"
     ],
     "Resource": [
       "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-sonic-v1:0",
       "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
     ]
   }
   ```

## Step 8: Mobile App Configuration

Update your mobile app to use production endpoints:

```javascript
// In your mobile app config
const API_CONFIG = {
  baseURL: 'https://your-api-gateway-url',
  region: 'us-east-1',
  endpoints: {
    register: '/api/auth/register',
    login: '/api/auth/login',
    applePurchase: '/api/purchase/apple/verify',
    googlePurchase: '/api/purchase/google/verify'
  }
};
```

## Step 9: Domain and SSL Configuration

Set up custom domain (optional):

1. **Register domain in Route 53**
2. **Create ACM certificate**
3. **Configure API Gateway custom domain**
4. **Update DNS records**

## Monitoring and Maintenance

### CloudWatch Dashboards

Monitor key metrics:
- Lambda function duration and errors
- DynamoDB read/write capacity
- ElastiCache connection count
- API Gateway request count and latency

### Cost Optimization

1. **DynamoDB**: Uses pay-per-request billing
2. **Lambda**: Charged per invocation and duration
3. **ElastiCache**: Consider reserved instances for production
4. **API Gateway**: Monitor request volume

### Security Best Practices

1. **Enable AWS CloudTrail** for audit logging
2. **Use AWS WAF** for API Gateway protection
3. **Enable VPC endpoints** for DynamoDB access
4. **Rotate IAM access keys** regularly
5. **Monitor suspicious activity** in CloudWatch

## Troubleshooting

### Common Issues

1. **Lambda Timeout Errors**
   - Increase function timeout in template.yaml
   - Optimize database queries

2. **DynamoDB Throttling**
   - Enable auto-scaling
   - Review access patterns

3. **ElastiCache Connection Issues**
   - Verify security group settings
   - Check VPC configuration

4. **Nova AI Access Denied**
   - Verify Bedrock model access is enabled
   - Check IAM permissions

### Logs and Debugging

View Lambda logs:
```bash
aws logs tail /aws/lambda/ielts-genai-prep --follow --region us-east-1
```

Check DynamoDB metrics:
```bash
aws cloudwatch get-metric-statistics \
    --namespace AWS/DynamoDB \
    --metric-name ConsumedReadCapacityUnits \
    --dimensions Name=TableName,Value=ielts-genai-prep-users \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Sum
```

## Scaling Considerations

### Multi-Region Deployment

For global users, deploy to additional regions:
- `eu-west-1` for European users
- `ap-southeast-1` for Asian users

Note: Nova Sonic is only available in us-east-1, so speaking assessments will route there.

### Performance Optimization

1. **Use DynamoDB Global Tables** for cross-region replication
2. **Implement CloudFront** for global content delivery
3. **Enable Lambda@Edge** for regional processing
4. **Consider Aurora Serverless** for complex queries

This deployment guide provides a complete production-ready setup for the IELTS GenAI Prep mobile-first authentication system with full Nova AI integration.