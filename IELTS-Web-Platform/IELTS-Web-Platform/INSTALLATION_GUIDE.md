# Installation Guide for IELTS GenAI Prep Backend Deployment

## Prerequisites Installation (Windows)

### 1. Install Python

1. **Download Python**:
   - Go to https://www.python.org/downloads/
   - Download Python 3.11 or later
   - **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
   ```powershell
   python --version
   pip --version
   ```

### 2. Install AWS CLI

1. **Download AWS CLI**:
   - Go to https://aws.amazon.com/cli/
   - Download AWS CLI for Windows
   - Run the installer

2. **Verify Installation**:
   ```powershell
   aws --version
   ```

3. **Configure AWS CLI**:
   ```powershell
   aws configure
   ```
   
   Enter your WWP user credentials:
   - **Access Key ID**: [Your WWP Access Key]
   - **Secret Access Key**: [Your WWP Secret Key]
   - **Default region**: `us-east-1`
   - **Default output format**: `json`

### 3. Verify Your DynamoDB Tables

Make sure these tables exist in your AWS account:
- `ielts-genai-prep-users`
- `ielts-genai-prep-assessments`
- `ielts-genai-prep-auth-tokens`

## Quick Deployment

Once prerequisites are installed:

1. **Open PowerShell as Administrator**
2. **Navigate to your project**:
   ```powershell
   cd "path\to\your\project"
   ```

3. **Run the deployment script**:
   ```powershell
   .\backend\Deploy-Backend.ps1
   ```

## Manual Deployment (Alternative)

If the PowerShell script doesn't work, you can deploy manually:

### Step 1: Install Python Dependencies
```powershell
cd backend
pip install boto3 PyJWT requests
```

### Step 2: Create IAM Role
```powershell
aws iam create-role --role-name ielts-lambda-execution-role --assume-role-policy-document file://trust-policy.json
```

### Step 3: Deploy Each Lambda Function
```powershell
# Create deployment package
Compress-Archive -Path "lambda_functions/auth_handler.py" -DestinationPath "auth_handler.zip"

# Deploy function
aws lambda create-function \
  --function-name ielts-auth-handler \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/ielts-lambda-execution-role \
  --handler auth_handler.lambda_handler \
  --zip-file fileb://auth_handler.zip
```

## Testing Your Deployment

### Test Lambda Function Directly
```powershell
aws lambda invoke \
  --function-name ielts-auth-handler \
  --payload '{"httpMethod":"GET","path":"/api/health"}' \
  response.json

# View response
Get-Content response.json
```

### Expected Response
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"status\":\"healthy\",\"timestamp\":\"2024-01-15T10:30:00Z\"}"
}
```

## Troubleshooting

### Common Issues

1. **"aws command not found"**
   - Restart PowerShell after installing AWS CLI
   - Check if AWS CLI is in your PATH

2. **"python command not found"**
   - Restart PowerShell after installing Python
   - Ensure "Add to PATH" was checked during installation

3. **AWS credentials error**
   - Run `aws configure` again
   - Verify your WWP user has the correct permissions

4. **DynamoDB access denied**
   - Check if your tables exist: `aws dynamodb list-tables`
   - Verify WWP user has DynamoDB permissions

5. **Lambda deployment fails**
   - Check IAM role exists: `aws iam get-role --role-name ielts-lambda-execution-role`
   - Verify role has correct policies attached

### Debug Commands

```powershell
# Check AWS configuration
aws sts get-caller-identity

# List your DynamoDB tables
aws dynamodb list-tables

# List your Lambda functions
aws lambda list-functions

# Check Lambda function logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/ielts"
```

## Next Steps After Deployment

1. **Create API Gateway** (optional for direct testing)
2. **Test each Lambda function individually**
3. **Update your mobile app configuration**
4. **Set up monitoring and logging**

## Support

If you encounter issues:
1. Check the AWS CloudWatch logs for your Lambda functions
2. Verify all prerequisites are properly installed
3. Ensure your WWP user has the necessary permissions
4. Test individual components step by step

## Security Notes

- Keep your AWS credentials secure
- Use environment variables for sensitive data in production
- Enable CloudTrail for audit logging
- Set up proper IAM policies with least privilege access