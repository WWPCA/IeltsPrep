#!/usr/bin/env python3
"""
Check current DynamoDB questions count and redeploy all 80 comprehensive questions
"""

import boto3
from create_comprehensive_questions import (
    create_academic_writing_questions,
    create_general_writing_questions,
    create_academic_speaking_questions,
    create_general_speaking_questions
)

def check_current_questions():
    """Check current questions in DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        response = table.scan()
        items = response['Items']
        
        print(f"📊 Current DynamoDB Status:")
        print(f"   Total questions: {len(items)}")
        
        # Count by type
        type_counts = {}
        for item in items:
            assessment_type = item.get('assessment_type', 'unknown')
            type_counts[assessment_type] = type_counts.get(assessment_type, 0) + 1
        
        print(f"   By assessment type:")
        for type_name, count in type_counts.items():
            print(f"     • {type_name}: {count}")
        
        return len(items), type_counts
        
    except Exception as e:
        print(f"❌ Error checking DynamoDB: {e}")
        return 0, {}

def clear_and_redeploy_questions():
    """Clear existing questions and redeploy all 80 comprehensive questions"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        print("🧹 Clearing existing questions...")
        
        # Scan and delete all existing items
        response = table.scan()
        items = response['Items']
        
        for item in items:
            table.delete_item(Key={'question_id': item['question_id']})
        
        print(f"✅ Cleared {len(items)} existing questions")
        
        # Create all comprehensive questions
        print("🚀 Creating comprehensive questions...")
        academic_writing = create_academic_writing_questions()
        general_writing = create_general_writing_questions()
        academic_speaking = create_academic_speaking_questions()
        general_speaking = create_general_speaking_questions()
        
        all_questions = academic_writing + general_writing + academic_speaking + general_speaking
        
        print(f"📝 Deploying {len(all_questions)} comprehensive questions:")
        print(f"   • Academic Writing: {len(academic_writing)}")
        print(f"   • General Writing: {len(general_writing)}")
        print(f"   • Academic Speaking: {len(academic_speaking)}")
        print(f"   • General Speaking: {len(general_speaking)}")
        
        # Upload all questions
        success_count = 0
        for question in all_questions:
            try:
                table.put_item(Item=question)
                success_count += 1
            except Exception as e:
                print(f"❌ Error uploading {question['question_id']}: {e}")
        
        print(f"✅ Successfully uploaded {success_count} questions")
        
        # Verify final count
        final_count, final_types = check_current_questions()
        
        if final_count == 80:
            print("🎉 SUCCESS: All 80 comprehensive questions deployed!")
        else:
            print(f"⚠️  WARNING: Expected 80 questions, got {final_count}")
        
        return success_count == 80
        
    except Exception as e:
        print(f"❌ Error during redeployment: {e}")
        return False

def main():
    """Main function"""
    print("🔍 CHECKING DYNAMODB QUESTIONS STATUS")
    print("=" * 50)
    
    # Check current status
    current_count, current_types = check_current_questions()
    
    if current_count < 80:
        print(f"\n⚠️  ISSUE DETECTED: Only {current_count} questions found (expected 80)")
        print("🔧 Initiating complete redeployment...")
        
        success = clear_and_redeploy_questions()
        
        if success:
            print("\n🎉 REDEPLOYMENT COMPLETE!")
            print("✅ All 80 comprehensive questions now in DynamoDB")
        else:
            print("\n❌ REDEPLOYMENT FAILED")
            print("🔧 Check AWS permissions and try again")
    else:
        print(f"\n✅ Questions count looks good: {current_count}")
        print("🎯 No redeployment needed")

if __name__ == "__main__":
    main()