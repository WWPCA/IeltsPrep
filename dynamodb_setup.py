"""
DynamoDB Table Setup for IELTS GenAI Prep
Global tables across multiple regions for low latency worldwide
"""

import boto3
import json
from botocore.exceptions import ClientError

def create_dynamodb_tables():
    """Create DynamoDB tables with global table configuration"""
    
    # Regions for global deployment
    regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']
    
    for region in regions:
        dynamodb = boto3.client('dynamodb', region_name=region)
        
        try:
            # Create IELTSUsers table
            users_table = dynamodb.create_table(
                TableName='IELTSUsers',
                KeySchema=[
                    {
                        'AttributeName': 'email',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'email',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                },
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'RegionIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'region',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ]
            )
            print(f"Created IELTSUsers table in {region}")
            
            # Create IELTSAssessments table
            assessments_table = dynamodb.create_table(
                TableName='IELTSAssessments',
                KeySchema=[
                    {
                        'AttributeName': 'assessment_id',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'assessment_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'user_email',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'assessment_type',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                },
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'UserEmailIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'user_email',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    },
                    {
                        'IndexName': 'AssessmentTypeIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'assessment_type',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ]
            )
            print(f"Created IELTSAssessments table in {region}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"Tables already exist in {region}")
            else:
                print(f"Error creating tables in {region}: {e}")

def setup_global_tables():
    """Set up global table replication across regions"""
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    try:
        # Create global table for IELTSUsers
        dynamodb.create_global_table(
            GlobalTableName='IELTSUsers',
            ReplicationGroup=[
                {'RegionName': 'us-east-1'},
                {'RegionName': 'eu-west-1'},
                {'RegionName': 'ap-southeast-1'}
            ]
        )
        print("Created global table for IELTSUsers")
        
        # Create global table for IELTSAssessments
        dynamodb.create_global_table(
            GlobalTableName='IELTSAssessments',
            ReplicationGroup=[
                {'RegionName': 'us-east-1'},
                {'RegionName': 'eu-west-1'},
                {'RegionName': 'ap-southeast-1'}
            ]
        )
        print("Created global table for IELTSAssessments")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'GlobalTableAlreadyExistsException':
            print("Global tables already exist")
        else:
            print(f"Error creating global tables: {e}")

if __name__ == "__main__":
    create_dynamodb_tables()
    setup_global_tables()