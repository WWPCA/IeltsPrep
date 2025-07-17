
# Deploy to AWS Lambda
aws lambda update-function-code \
    --function-name ielts-genai-prep-api \
    --zip-file fileb://recaptcha_fixed_lambda.zip \
    --region us-east-1

# Update environment variables
aws lambda update-function-configuration \
    --function-name ielts-genai-prep-api \
    --environment Variables='{
        "RECAPTCHA_V2_SITE_KEY": "6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ",
        "RECAPTCHA_V2_SECRET_KEY": "YOUR_SECRET_KEY_HERE"
    }' \
    --region us-east-1
