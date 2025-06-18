#!/bin/bash
# Setup Custom Domain for ieltsaiprep.com

echo "🌐 Setting up custom domain: ieltsaiprep.com"

# Get API Gateway ID
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`ielts-genai-prep-api`].id' --output text)

if [ -z "$API_ID" ]; then
    echo "❌ API Gateway not found. Please deploy your Lambda function first."
    exit 1
fi

echo "✅ Found API Gateway: $API_ID"

# Request SSL Certificate
echo "🔒 Requesting SSL certificate for ieltsaiprep.com..."
CERT_ARN=$(aws acm request-certificate \
    --domain-name ieltsaiprep.com \
    --subject-alternative-names www.ieltsaiprep.com \
    --validation-method DNS \
    --query 'CertificateArn' \
    --output text)

echo "✅ Certificate requested: $CERT_ARN"
echo "⏳ Please validate the certificate in ACM console"
echo "   Go to AWS Certificate Manager and complete DNS validation"

# Create custom domain name (will need to run after certificate validation)
echo ""
echo "🔧 After certificate validation, run this command:"
echo "aws apigateway create-domain-name \\"
echo "    --domain-name ieltsaiprep.com \\"
echo "    --certificate-arn $CERT_ARN \\"
echo "    --security-policy TLS_1_2"

echo ""
echo "📋 DNS Configuration Required:"
echo "In your domain registrar for ieltsaiprep.com:"
echo "1. Add A record: @ -> [API Gateway IP from custom domain]"
echo "2. Add CNAME record: www -> ieltsaiprep.com"
echo ""
echo "📖 Full guide: See CUSTOM_DOMAIN_SETUP.md"