# IELTS GenAI Prep Backend Deployment Script for Windows
# This script helps deploy your AWS Lambda functions

Write-Host "🚀 IELTS GenAI Prep Backend Deployment" -ForegroundColor Green
Write-Host "=" * 50

# Check prerequisites
Write-Host "`n📋 Checking Prerequisites..." -ForegroundColor Yellow

# Check if AWS CLI is installed
try {
    $awsVersion = aws --version 2>$null
    if ($awsVersion) {
        Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
    } else {
        throw "AWS CLI not found"
    }
} catch {
    Write-Host "❌ AWS CLI not installed" -ForegroundColor Red
    Write-Host "`nPlease install AWS CLI first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://aws.amazon.com/cli/"
    Write-Host "2. Run the installer"
    Write-Host "3. Configure with: aws configure"
    Write-Host "4. Enter your WWP user credentials"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python not installed" -ForegroundColor Red
    Write-Host "`nPlease install Python first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://www.python.org/downloads/"
    Write-Host "2. Run the installer (check 'Add to PATH')"
    Write-Host "3. Restart PowerShell"
    exit 1
}

# Check AWS credentials
Write-Host "`n📋 Checking AWS Configuration..." -ForegroundColor Yellow
try {
    $awsIdentity = aws sts get-caller-identity 2>$null | ConvertFrom-Json
    if ($awsIdentity) {
        Write-Host "✅ AWS credentials configured" -ForegroundColor Green
        Write-Host "   Account: $($awsIdentity.Account)" -ForegroundColor Gray
        Write-Host "   User: $($awsIdentity.Arn)" -ForegroundColor Gray
    } else {
        throw "AWS credentials not configured"
    }
} catch {
    Write-Host "❌ AWS credentials not configured" -ForegroundColor Red
    Write-Host "`nPlease configure AWS CLI:" -ForegroundColor Yellow
    Write-Host "1. Run: aws configure"
    Write-Host "2. Enter your WWP user Access Key ID"
    Write-Host "3. Enter your WWP user Secret Access Key"
    Write-Host "4. Set region to: us-east-1"
    Write-Host "5. Set output format to: json"
    exit 1
}

# Check DynamoDB tables
Write-Host "`n📋 Checking DynamoDB Tables..." -ForegroundColor Yellow
$requiredTables = @(
    "ielts-genai-prep-users",
    "ielts-genai-prep-assessments", 
    "ielts-genai-prep-auth-tokens"
)

foreach ($table in $requiredTables) {
    try {
        $tableInfo = aws dynamodb describe-table --table-name $table 2>$null | ConvertFrom-Json
        if ($tableInfo.Table.TableStatus -eq "ACTIVE") {
            Write-Host "✅ Table $table is active" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Table $table status: $($tableInfo.Table.TableStatus)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Table $table not found" -ForegroundColor Red
        Write-Host "   Please create this table in DynamoDB console" -ForegroundColor Yellow
    }
}

# Install Python dependencies
Write-Host "`n📋 Installing Python Dependencies..." -ForegroundColor Yellow
try {
    Set-Location backend
    pip install boto3 PyJWT requests -q
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

# Create deployment packages
Write-Host "`n📋 Creating Deployment Packages..." -ForegroundColor Yellow

$functions = @(
    @{name="auth_handler"; description="Authentication and user management"},
    @{name="purchase_handler"; description="Purchase verification and management"},
    @{name="nova_ai_handler"; description="Nova AI integration for assessments"},
    @{name="assessment_handler"; description="Assessment management"},
    @{name="user_handler"; description="User profile and dashboard"},
    @{name="qr_auth_handler"; description="QR code authentication"}
)

foreach ($func in $functions) {
    $funcName = $func.name
    $zipFile = "$funcName.zip"
    
    # Create zip file
    if (Test-Path $zipFile) {
        Remove-Item $zipFile
    }
    
    Compress-Archive -Path "lambda_functions/$funcName.py" -DestinationPath $zipFile
    Write-Host "✅ Created package: $zipFile" -ForegroundColor Green
}

# Create IAM role
Write-Host "`n📋 Creating IAM Role..." -ForegroundColor Yellow
$roleName = "ielts-lambda-execution-role"

$trustPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Principal = @{
                Service = "lambda.amazonaws.com"
            }
            Action = "sts:AssumeRole"
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $role = aws iam create-role --role-name $roleName --assume-role-policy-document $trustPolicy 2>$null | ConvertFrom-Json
    Write-Host "✅ Created IAM role: $roleName" -ForegroundColor Green
} catch {
    # Role might already exist
    $role = aws iam get-role --role-name $roleName 2>$null | ConvertFrom-Json
    if ($role) {
        Write-Host "✅ Using existing IAM role: $roleName" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create/get IAM role" -ForegroundColor Red
        exit 1
    }
}

$roleArn = $role.Role.Arn

# Attach policies to role
Write-Host "`n📋 Attaching Policies to Role..." -ForegroundColor Yellow

# Basic Lambda execution policy
aws iam attach-role-policy --role-name $roleName --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" 2>$null

# DynamoDB policy
$dynamoPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Action = @(
                "dynamodb:Query",
                "dynamodb:Scan", 
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            )
            Resource = @(
                "arn:aws:dynamodb:us-east-1:*:table/ielts-genai-prep-users",
                "arn:aws:dynamodb:us-east-1:*:table/ielts-genai-prep-assessments",
                "arn:aws:dynamodb:us-east-1:*:table/ielts-genai-prep-auth-tokens"
            )
        }
    )
} | ConvertTo-Json -Depth 10

aws iam put-role-policy --role-name $roleName --policy-name "DynamoDBAccess" --policy-document $dynamoPolicy 2>$null

# Bedrock policy
$bedrockPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Action = @(
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            )
            Resource = @(
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-sonic-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
            )
        }
    )
} | ConvertTo-Json -Depth 10

aws iam put-role-policy --role-name $roleName --policy-name "BedrockAccess" --policy-document $bedrockPolicy 2>$null

Write-Host "✅ Policies attached to role" -ForegroundColor Green

# Wait for role to propagate
Write-Host "`n⏳ Waiting for IAM role to propagate..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Deploy Lambda functions
Write-Host "`n📋 Deploying Lambda Functions..." -ForegroundColor Yellow

foreach ($func in $functions) {
    $funcName = $func.name
    $description = $func.description
    $zipFile = "$funcName.zip"
    $lambdaName = "ielts-$($funcName.Replace('_', '-'))"
    
    # Set memory and timeout based on function type
    $memory = 512
    $timeout = 30
    if ($funcName -eq "nova_ai_handler") {
        $memory = 1024
        $timeout = 300
    }
    
    try {
        # Try to create function
        $result = aws lambda create-function `
            --function-name $lambdaName `
            --runtime python3.11 `
            --role $roleArn `
            --handler "$funcName.lambda_handler" `
            --zip-file "fileb://$zipFile" `
            --description $description `
            --timeout $timeout `
            --memory-size $memory `
            --environment "Variables={DYNAMODB_USERS_TABLE=ielts-genai-prep-users,DYNAMODB_ASSESSMENTS_TABLE=ielts-genai-prep-assessments,DYNAMODB_TOKENS_TABLE=ielts-genai-prep-auth-tokens,JWT_SECRET=your-jwt-secret-key-here,STAGE=dev}" `
            2>$null | ConvertFrom-Json
            
        if ($result) {
            Write-Host "✅ Created Lambda function: $lambdaName" -ForegroundColor Green
        }
    } catch {
        # Function might exist, try to update
        try {
            aws lambda update-function-code --function-name $lambdaName --zip-file "fileb://$zipFile" 2>$null | Out-Null
            aws lambda update-function-configuration `
                --function-name $lambdaName `
                --runtime python3.11 `
                --role $roleArn `
                --handler "$funcName.lambda_handler" `
                --description $description `
                --timeout $timeout `
                --memory-size $memory `
                --environment "Variables={DYNAMODB_USERS_TABLE=ielts-genai-prep-users,DYNAMODB_ASSESSMENTS_TABLE=ielts-genai-prep-assessments,DYNAMODB_TOKENS_TABLE=ielts-genai-prep-auth-tokens,JWT_SECRET=your-jwt-secret-key-here,STAGE=dev}" `
                2>$null | Out-Null
                
            Write-Host "✅ Updated Lambda function: $lambdaName" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to deploy function: $lambdaName" -ForegroundColor Red
        }
    }
    
    # Clean up zip file
    Remove-Item $zipFile -ErrorAction SilentlyContinue
}

# Test deployment
Write-Host "`n📋 Testing Deployment..." -ForegroundColor Yellow
try {
    $testResult = aws lambda invoke --function-name "ielts-auth-handler" --payload '{"httpMethod":"GET","path":"/api/health"}' response.json 2>$null
    if (Test-Path "response.json") {
        $response = Get-Content "response.json" | ConvertFrom-Json
        if ($response.statusCode -eq 200) {
            Write-Host "✅ Health check passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Health check returned status: $($response.statusCode)" -ForegroundColor Yellow
        }
        Remove-Item "response.json" -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "⚠️  Health check failed (this might be normal)" -ForegroundColor Yellow
}

Write-Host "`n🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=" * 50

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Create API Gateway to expose your Lambda functions"
Write-Host "2. Test individual Lambda functions in AWS Console"
Write-Host "3. Update your mobile app with the API endpoints"
Write-Host "4. Configure custom domain (optional)"

Write-Host "`nLambda Functions Deployed:" -ForegroundColor Cyan
foreach ($func in $functions) {
    $lambdaName = "ielts-$($func.name.Replace('_', '-'))"
    Write-Host "  • $lambdaName - $($func.description)" -ForegroundColor Gray
}

Write-Host "`nTo test a function:" -ForegroundColor Yellow
Write-Host 'aws lambda invoke --function-name "ielts-auth-handler" --payload \'{"httpMethod":"GET","path":"/api/health"}\' response.json'

Set-Location ..
Write-Host "`n✅ Deployment script completed!" -ForegroundColor Green