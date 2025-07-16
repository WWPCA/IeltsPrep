#!/usr/bin/env python3
"""
Analyze Production User Accounts to Understand Differences
"""

import boto3
import json
from datetime import datetime

def analyze_production_accounts():
    """Analyze the specific accounts to understand their differences"""
    try:
        # Connect to production DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.Table('ielts-genai-prep-users')
        
        # Target accounts to analyze
        target_accounts = [
            'simpletest@ieltsaiprep.com',
            'prodtest@ieltsaiprep.com', 
            'novatest@ieltsaiprep.com',
            'bcrypttest@ieltsaiprep.com'
        ]
        
        print("🔍 Analyzing production user accounts...")
        
        for email in target_accounts:
            try:
                # Try different possible key structures
                possible_keys = [
                    {'email': email},
                    {'user_id': email},
                    {'id': email}
                ]
                
                user_found = False
                for key in possible_keys:
                    try:
                        response = users_table.get_item(Key=key)
                        if 'Item' in response:
                            user = response['Item']
                            user_found = True
                            
                            print(f"\n📧 {email}:")
                            print(f"  Created: {user.get('created_at', 'Unknown')}")
                            print(f"  Password hash: {user.get('password_hash', 'None')[:20]}...")
                            print(f"  Active: {user.get('active', 'Unknown')}")
                            print(f"  Assessment attempts: {user.get('assessment_attempts', 'Unknown')}")
                            print(f"  GDPR consent: {user.get('gdpr_consent', 'Unknown')}")
                            print(f"  Purchase verified: {user.get('purchase_verified', 'Unknown')}")
                            
                            # Check password hash length and format
                            password_hash = user.get('password_hash', '')
                            if password_hash:
                                if len(password_hash) > 60:
                                    print(f"  Hash type: Likely PBKDF2 (length: {len(password_hash)})")
                                elif len(password_hash) == 60:
                                    print(f"  Hash type: Likely bcrypt (length: {len(password_hash)})")
                                else:
                                    print(f"  Hash type: Unknown (length: {len(password_hash)})")
                            
                            break
                    except Exception as e:
                        continue
                
                if not user_found:
                    print(f"\n❌ {email}: Not found or inaccessible")
                    
            except Exception as e:
                print(f"❌ Error analyzing {email}: {e}")
        
        # Also scan the table to understand structure
        print("\n🔍 Scanning table structure...")
        try:
            response = users_table.scan(Limit=5)
            items = response.get('Items', [])
            
            if items:
                print(f"📊 Sample user structure:")
                sample_user = items[0]
                for key, value in sample_user.items():
                    if key == 'password_hash':
                        print(f"  {key}: {str(value)[:20]}... (length: {len(str(value))})")
                    else:
                        print(f"  {key}: {value}")
            else:
                print("❌ No users found in table scan")
                
        except Exception as e:
            print(f"❌ Error scanning table: {e}")
            
    except Exception as e:
        print(f"❌ Error connecting to production database: {e}")

if __name__ == "__main__":
    analyze_production_accounts()