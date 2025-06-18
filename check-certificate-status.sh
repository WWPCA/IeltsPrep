#!/bin/bash

# Certificate Status Checker for ieltsaiprep.com
echo "🔍 Checking SSL certificate validation status..."

# Check if certificate is ready
echo "📋 Current certificate status:"
echo "   Certificate ID: b3d321c7-9017-49eb-b529-5228cd900cf4"
echo "   Domain: www.ieltsaiprep.com, ieltsaiprep.com"
echo "   Region: us-east-1"
echo ""

echo "💡 Next steps once certificate shows 'Issued':"
echo "1. Create custom domain in API Gateway"
echo "2. Add API mapping to Lambda function"
echo "3. Add DNS A record with target domain"
echo "4. Update mobile app configuration"
echo ""

echo "🎯 Expected timeline:"
echo "   DNS validation: 5-30 minutes"
echo "   Custom domain setup: 2-3 minutes"
echo "   DNS propagation: 24-48 hours"
echo ""

echo "📝 Manual check: Go to AWS Certificate Manager Console"
echo "   https://console.aws.amazon.com/acm/home?region=us-east-1"
echo "   Look for 'Issued' status instead of 'Pending validation'"