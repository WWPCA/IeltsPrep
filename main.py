"""
Entry point for AWS Lambda deployment
This file exists only for Replit compatibility - actual deployment uses lambda_handler.py
"""

from lambda_handler import lambda_handler

# For local testing only
if __name__ == '__main__':
    print("AWS Lambda handler ready for deployment")
    print("Use 'sls deploy' to deploy to AWS")
    print("Local Flask server no longer used - pure serverless architecture")