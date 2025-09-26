# IELTS GenAI Prep - Production Deployment Guide

## Architecture Overview

The IELTS GenAI Prep application uses a complete AWS Lambda serverless architecture with global multi-region deployment, QR code authentication, and bi-directional Nova Sonic streaming for real-time AI examiner conversations.

### Core Components

1. **AWS Lambda Functions** (Multi-region: us-east-1, eu-west-1, ap-southeast-1)
   - Authentication & QR management
   - Assessment processing with Nova Micro
   - Bi-directional Nova Sonic streaming (us-east-1 only)
   - Mobile app purchase verification

2. **DynamoDB Tables** (Global tables with cross-region replication)
   - QR tokens and sessions
   - User assessments and progress
   - Mobile app purchase records

3. **ElastiCache Redis** (Regional clusters)
   - Session storage and real-time data
   - WebSocket connection management

4. **API Gateway** (Regional endpoints)
   - REST API for mobile apps
   - WebSocket API for real-time streaming

## Pre-Deployment Setup

### 1. AWS Account Configuration

```bash
# Configure AWS CLI with appropriate permissions
aws configure set region us-east-1
aws configure set output json

# Verify Bedrock model access
aws bedrock list-foundation-models --region us-east-1
```

### 2. Required Environment Variables

```bash
# Core application settings
export STAGE=prod
export CORS_ORIGIN=https://ieltsaiprep.com
export NOVA_SONIC_REGION=us-east-1

# Database configuration
export DYNAMODB_QR_TOKENS_TABLE=ielts-genai-prep-qr-tokens-prod
export DYNAMODB_SESSIONS_TABLE=ielts-genai-prep-sessions-prod
export DYNAMODB_ASSESSMENTS_TABLE=ielts-genai-prep-assessments-prod
export DYNAMODB_USERS_TABLE=ielts-genai-prep-users-prod

# Cache configuration
export ELASTICACHE_CLUSTER=ielts-genai-prep-cache-prod
```

### 3. Mobile App Store Configuration

#### Apple App Store Connect
- Bundle ID: `com.ieltsaiprep.genai`
- In-App Purchases: 4 products at $36 each
  - `academic_speaking_assessment`
  - `academic_writing_assessment`
  - `general_speaking_assessment`
  - `general_writing_assessment`

#### Google Play Console
- Package Name: `com.ieltsaiprep.genai`
- In-App Products: Same 4 assessments as Apple
- Pricing: $36 USD (auto-converted globally)

## Regional Deployment Strategy

### Primary Region: us-east-1 (Virginia)
- **Purpose**: Nova Sonic streaming, primary database
- **Services**: All Lambda functions, DynamoDB global tables primary
- **Nova Models**: nova-sonic-1:0, nova-micro-1:0

### Secondary Region: eu-west-1 (Ireland)
- **Purpose**: European user base, GDPR compliance
- **Services**: Assessment functions, regional API Gateway
- **Database**: DynamoDB global table replica

### Tertiary Region: ap-southeast-1 (Singapore)
- **Purpose**: Asia-Pacific user base
- **Services**: Assessment functions, regional API Gateway
- **Database**: DynamoDB global table replica

## Deployment Commands

### 1. Deploy Infrastructure (Primary Region)

```bash
# Deploy to us-east-1 (Primary with Nova Sonic)
serverless deploy --region us-east-1 --stage prod

# Create DynamoDB global tables
aws dynamodb create-global-table \
    --global-table-name ielts-genai-prep-qr-tokens-prod \
    --replication-group RegionName=us-east-1 RegionName=eu-west-1 RegionName=ap-southeast-1

aws dynamodb create-global-table \
    --global-table-name ielts-genai-prep-sessions-prod \
    --replication-group RegionName=us-east-1 RegionName=eu-west-1 RegionName=ap-southeast-1

aws dynamodb create-global-table \
    --global-table-name ielts-genai-prep-assessments-prod \
    --replication-group RegionName=us-east-1 RegionName=eu-west-1 RegionName=ap-southeast-1
```

### 2. Deploy Regional Endpoints

```bash
# Deploy to Europe
serverless deploy --region eu-west-1 --stage prod

# Deploy to Asia-Pacific
serverless deploy --region ap-southeast-1 --stage prod
```

### 3. Configure ElastiCache Clusters

```bash
# Create Redis clusters in each region
aws elasticache create-replication-group \
    --replication-group-id ielts-genai-prep-cache-prod \
    --description "IELTS GenAI Prep Session Cache" \
    --node-type cache.r6g.large \
    --region us-east-1

aws elasticache create-replication-group \
    --replication-group-id ielts-genai-prep-cache-prod \
    --description "IELTS GenAI Prep Session Cache" \
    --node-type cache.r6g.large \
    --region eu-west-1

aws elasticache create-replication-group \
    --replication-group-id ielts-genai-prep-cache-prod \
    --description "IELTS GenAI Prep Session Cache" \
    --node-type cache.r6g.large \
    --region ap-southeast-1
```

## Mobile App Configuration

### iOS Configuration (Capacitor)

```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'com.ieltsaiprep.genai',
  appName: 'IELTS GenAI Prep',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    CapacitorHttp: {
      enabled: true
    },
    PurchaseConnector: {
      enabled: true,
      products: [
        'academic_speaking_assessment',
        'academic_writing_assessment', 
        'general_speaking_assessment',
        'general_writing_assessment'
      ]
    }
  }
};

export default config;
```

### Regional API Endpoints

```javascript
// mobile_api_client.js - Production endpoints
const REGIONAL_ENDPOINTS = {
  'us-east-1': 'https://api-us.ieltsaiprep.com',
  'eu-west-1': 'https://api-eu.ieltsaiprep.com',
  'ap-southeast-1': 'https://api-ap.ieltsaiprep.com'
};

// Nova Sonic always routes to us-east-1
const NOVA_SONIC_ENDPOINT = 'wss://streaming-us.ieltsaiprep.com/nova-sonic';
```

## DNS Configuration

### Route 53 Setup

```bash
# Create hosted zone
aws route53 create-hosted-zone --name ieltsaiprep.com --caller-reference $(date +%s)

# Configure regional API endpoints
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch '{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api-us.ieltsaiprep.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "abcd1234.execute-api.us-east-1.amazonaws.com"}]
      }
    },
    {
      "Action": "CREATE", 
      "ResourceRecordSet": {
        "Name": "api-eu.ieltsaiprep.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "efgh5678.execute-api.eu-west-1.amazonaws.com"}]
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api-ap.ieltsaiprep.com", 
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "ijkl9012.execute-api.ap-southeast-1.amazonaws.com"}]
      }
    }
  ]
}'
```

## Monitoring & Observability

### CloudWatch Dashboards

```bash
# Create monitoring dashboard
aws cloudwatch put-dashboard --dashboard-name IELTSGenAIPrepProd --dashboard-body '{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", "FunctionName", "ielts-genai-prep-prod-api"],
          ["AWS/Lambda", "Errors", "FunctionName", "ielts-genai-prep-prod-api"],
          ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "ielts-genai-prep-assessments-prod"],
          ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "ielts-genai-prep-cache-prod"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "IELTS GenAI Prep - Production Metrics"
      }
    }
  ]
}'
```

### Alerts Configuration

```bash
# Critical error alerts
aws cloudwatch put-metric-alarm \
    --alarm-name "IELTSGenAIPrep-HighErrorRate" \
    --alarm-description "High error rate in Lambda functions" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

## Security Configuration

### CORS Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:*:*:*/prod/*/*",
      "Condition": {
        "StringEquals": {
          "aws:Referer": "https://ieltsaiprep.com"
        }
      }
    }
  ]
}
```

### API Gateway Throttling

```bash
# Configure throttling limits
aws apigateway put-usage-plan \
    --usage-plan-id abc123 \
    --patch-ops op=replace,path=/throttle/rateLimit,value=1000 \
    --patch-ops op=replace,path=/throttle/burstLimit,value=2000
```

## Post-Deployment Verification

### 1. Health Checks

```bash
# Test all regional endpoints
curl -X GET https://api-us.ieltsaiprep.com/health
curl -X GET https://api-eu.ieltsaiprep.com/health  
curl -X GET https://api-ap.ieltsaiprep.com/health

# Test Nova Sonic streaming endpoint
wscat -c wss://streaming-us.ieltsaiprep.com/nova-sonic
```

### 2. QR Authentication Flow

```bash
# Test QR token generation
curl -X POST https://api-us.ieltsaiprep.com/auth/generate-qr \
    -H "Content-Type: application/json" \
    -d '{"user_email":"test@ieltsaiprep.com","purchase_verified":true}'

# Test mobile authentication
curl -X POST https://api-us.ieltsaiprep.com/mobile-authenticate \
    -H "Content-Type: application/json" \
    -d '{"token":"test-token","user_email":"test@ieltsaiprep.com"}'
```

### 3. Assessment Processing

```bash
# Test writing assessment
curl -X POST https://api-us.ieltsaiprep.com/assess-writing \
    -H "Content-Type: application/json" \
    -d '{"essay_text":"Sample essay text","prompt":"Academic writing prompt","assessment_type":"academic_writing"}'
```

## Maintenance & Updates

### Rolling Updates

```bash
# Deploy updates region by region
serverless deploy --region us-east-1 --stage prod
# Wait for health checks
serverless deploy --region eu-west-1 --stage prod  
# Wait for health checks
serverless deploy --region ap-southeast-1 --stage prod
```

### Database Migrations

```bash
# DynamoDB schema updates via Lambda functions
aws lambda invoke --function-name ielts-genai-prep-prod-migrate-db response.json
```

### Backup Strategy

```bash
# Enable point-in-time recovery
aws dynamodb put-backup-policy \
    --table-name ielts-genai-prep-assessments-prod \
    --backup-policy PointInTimeRecoveryEnabled=true
```

## Cost Optimization

### Reserved Capacity

```bash
# Purchase DynamoDB reserved capacity
aws dynamodb purchase-reserved-capacity-offerings \
    --reserved-capacity-offerings-id 12345678-1234-1234-1234-123456789012
```

### Lambda Provisioned Concurrency

```bash
# Configure for high-traffic regions
aws lambda put-provisioned-concurrency-config \
    --function-name ielts-genai-prep-prod-api \
    --provisioned-concurrency-settings ProvisionedConcurrencyLevel=50
```

This deployment guide ensures the IELTS GenAI Prep application scales globally while maintaining optimal performance for Nova Sonic streaming and assessment processing.