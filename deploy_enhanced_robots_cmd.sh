
# AWS CLI Deployment Command for Enhanced Robots.txt
aws lambda update-function-code \
    --function-name ielts-genai-prep-api \
    --zip-file fileb://production_enhanced_robots.zip \
    --region us-east-1

# Verify deployment
aws lambda get-function --function-name ielts-genai-prep-api --region us-east-1

# Test the enhanced robots.txt
curl -s https://www.ieltsaiprep.com/robots.txt
