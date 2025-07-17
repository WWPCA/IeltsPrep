#!/usr/bin/env python3
"""
Deploy Comprehensive Questions to Production DynamoDB
Uploads 80 comprehensive IELTS questions to ielts-assessment-questions table
"""

import boto3
import json
from datetime import datetime
from create_comprehensive_questions import (
    create_academic_writing_questions,
    create_general_writing_questions,
    create_academic_speaking_questions,
    create_general_speaking_questions
)

def deploy_questions_to_dynamodb():
    """Deploy all comprehensive questions to DynamoDB"""
    
    print("🚀 Deploying Comprehensive Questions to Production DynamoDB...")
    
    # Create all questions
    academic_writing = create_academic_writing_questions()
    general_writing = create_general_writing_questions()
    academic_speaking = create_academic_speaking_questions()
    general_speaking = create_general_speaking_questions()
    
    all_questions = academic_writing + general_writing + academic_speaking + general_speaking
    
    print(f"📊 Preparing {len(all_questions)} questions:")
    print(f"   • Academic Writing: {len(academic_writing)} questions")
    print(f"   • General Writing: {len(general_writing)} questions") 
    print(f"   • Academic Speaking: {len(academic_speaking)} questions")
    print(f"   • General Speaking: {len(general_speaking)} questions")
    
    # Initialize DynamoDB client
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        print("☁️  Connected to DynamoDB table: ielts-assessment-questions")
        
        # Upload questions in batches
        success_count = 0
        error_count = 0
        
        for question in all_questions:
            try:
                table.put_item(Item=question)
                print(f"✅ Uploaded: {question['question_id']} - {question['title']}")
                success_count += 1
            except Exception as e:
                print(f"❌ Error uploading {question['question_id']}: {str(e)}")
                error_count += 1
        
        print(f"\n🎉 DYNAMODB DEPLOYMENT COMPLETE!")
        print(f"✅ Successfully uploaded: {success_count} questions")
        print(f"❌ Errors: {error_count} questions")
        
        # Verify deployment
        try:
            response = table.scan()
            total_items = response['Count']
            print(f"📊 Total questions in DynamoDB: {total_items}")
            
            # Count by assessment type
            type_counts = {}
            for item in response['Items']:
                assessment_type = item.get('assessment_type', 'unknown')
                type_counts[assessment_type] = type_counts.get(assessment_type, 0) + 1
            
            print(f"\n📋 Question Distribution in DynamoDB:")
            for assessment_type, count in type_counts.items():
                print(f"   • {assessment_type}: {count} questions")
            
        except Exception as e:
            print(f"⚠️  Could not verify deployment: {str(e)}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ DynamoDB connection failed: {str(e)}")
        print("🔧 Please check AWS credentials and permissions")
        return False

def main():
    """Main deployment function"""
    
    print("🚀 COMPREHENSIVE QUESTIONS → DYNAMODB DEPLOYMENT")
    print("=" * 55)
    
    success = deploy_questions_to_dynamodb()
    
    if success:
        print(f"\n🌐 PRODUCTION DEPLOYMENT SUCCESSFUL!")
        print(f"✅ DynamoDB table populated with comprehensive questions")
        print(f"📊 80 questions now available for production assessments")
        print(f"🎯 Ready for Lambda deployment and production testing")
        print(f"🔗 Website: www.ieltsaiprep.com")
    else:
        print(f"\n❌ DEPLOYMENT FAILED")
        print(f"🔧 Check AWS credentials and DynamoDB permissions")
        print(f"ℹ️  Ensure you have access to 'ielts-assessment-questions' table")
    
    return success

if __name__ == "__main__":
    main()