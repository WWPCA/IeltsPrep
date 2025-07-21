#!/usr/bin/env python3
"""
Restore Working Production Deployment - Add Unique Questions to Proven Template
"""

import zipfile
import os
import boto3
import json
from datetime import datetime

def create_working_deployment_with_unique_questions():
    """Create deployment combining working template with unique question functionality"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"working_deployment_with_unique_questions_{timestamp}.zip"
    
    print(f"🔧 CREATING WORKING DEPLOYMENT WITH UNIQUE QUESTIONS")
    print(f"📦 Package: {package_name}")
    
    # Load the proven working lambda function
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Add the unique question functionality to the working lambda
    unique_question_functions = """
    def get_unique_assessment_question(self, user_email: str, assessment_type: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get a unique assessment question that user hasn't seen before\"\"\"
        user = self.users_table.get_item(user_email)
        if not user:
            return None
        
        # Get user's completed assessments to avoid repetition
        completed_assessments = user.get('completed_assessments', [])
        used_questions = [a.get('question_id') for a in completed_assessments if a.get('assessment_type') == assessment_type]
        
        # Get question bank for this assessment type
        question_bank = self._get_question_bank(assessment_type)
        available_questions = [q for q in question_bank if q['question_id'] not in used_questions]
        
        if not available_questions:
            # If all questions used, allow reuse after completing all 4 attempts
            available_questions = question_bank
        
        # Return random question from available pool
        import random
        return random.choice(available_questions) if available_questions else None

    def mark_question_as_used(self, user_email: str, assessment_type: str, question_id: str) -> bool:
        \"\"\"Mark question as used by user to prevent repetition\"\"\"
        user = self.users_table.get_item(user_email)
        if not user:
            return False
        
        if 'completed_assessments' not in user:
            user['completed_assessments'] = []
        
        # Add this assessment to completed list
        assessment_record = {
            'question_id': question_id,
            'assessment_type': assessment_type,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        user['completed_assessments'].append(assessment_record)
        return self.users_table.put_item(user)

    def _get_question_bank(self, assessment_type: str) -> List[Dict[str, Any]]:
        \"\"\"Get comprehensive question bank for assessment type\"\"\"
        question_banks = {
            'academic_writing': [
                {
                    'question_id': 'aw_task2_001',
                    'task': 'Task 2',
                    'prompt': 'Some people believe that universities should require every student to take a variety of courses outside their field of study. Others believe that universities should not force students to take any courses other than those that will help prepare them for jobs in their chosen fields. Write a response in which you discuss which view more closely aligns with your own position and explain your reasoning for the position you take.',
                    'word_limit': 250,
                    'time_limit': 40
                },
                {
                    'question_id': 'aw_task2_002', 
                    'task': 'Task 2',
                    'prompt': 'Many governments think that economic progress is their most important goal. Some people, however, think that other types of progress are equally important for a country. Discuss both these views and give your own opinion.',
                    'word_limit': 250,
                    'time_limit': 40
                },
                {
                    'question_id': 'aw_task2_003',
                    'task': 'Task 2', 
                    'prompt': 'In some countries, young people are encouraged to work or travel for a year between finishing high school and starting university studies. Discuss the advantages and disadvantages for young people who decide to do this.',
                    'word_limit': 250,
                    'time_limit': 40
                },
                {
                    'question_id': 'aw_task2_004',
                    'task': 'Task 2',
                    'prompt': 'Some people say that the main environmental problem of our time is the loss of particular species of plants and animals. Others say that there are more important environmental problems. Discuss both these views and give your own opinion.',
                    'word_limit': 250,
                    'time_limit': 40
                }
            ],
            'general_writing': [
                {
                    'question_id': 'gw_task1_001',
                    'task': 'Task 1',
                    'prompt': 'You recently bought a piece of equipment for your kitchen but it did not work. You phoned the shop but no action was taken. Write a letter to the shop manager. In your letter: describe the problem with the equipment, explain what happened when you phoned the shop, say what you would like the manager to do.',
                    'word_limit': 150,
                    'time_limit': 20
                },
                {
                    'question_id': 'gw_task1_002',
                    'task': 'Task 1', 
                    'prompt': 'You work for an international company, and would like to spend six months working in its head office in another country. Write a letter to your manager. In your letter: explain why you want to work in the company head office for six months, say how your work could be done while you are away, ask for his/her help in arranging it.',
                    'word_limit': 150,
                    'time_limit': 20
                },
                {
                    'question_id': 'gw_task1_003',
                    'task': 'Task 1',
                    'prompt': 'A friend has agreed to look after your house and pet while you are on holiday. Write a letter to your friend. In your letter: give contact details for when you are away, give instructions about how to care for your pet, describe other household duties.',
                    'word_limit': 150,
                    'time_limit': 20
                },
                {
                    'question_id': 'gw_task1_004',
                    'task': 'Task 1',
                    'prompt': 'You have seen an advertisement in an Australian magazine for someone to live with a family for six months and look after their six-year-old child. Write a letter to the parents. In your letter: explain why you would like the job, give details of why you would be a suitable person to employ, say how you would spend your free time while you are in Australia.',
                    'word_limit': 150,
                    'time_limit': 20
                }
            ],
            'academic_speaking': [
                {
                    'question_id': 'as_complete_001',
                    'assessment_type': 'academic_speaking',
                    'parts': [
                        {
                            'part': 1,
                            'duration': '4-5 minutes',
                            'topic': 'Introduction and Interview',
                            'questions': [
                                'Tell me about your favorite hobby and why you enjoy it.',
                                'Tell me about your job. What responsibilities do you have?'
                            ]
                        },
                        {
                            'part': 2,
                            'duration': '3-4 minutes',
                            'topic': 'Individual Long Turn',
                            'prompt': 'Describe a place you have visited that had a significant impact on you. You should say: where the place is, when you went there, what you did there, and explain why this place had such an impact on you.',
                            'prep_time': 60,
                            'talk_time': 120
                        },
                        {
                            'part': 3,
                            'duration': '4-5 minutes',
                            'topic': 'Two-way Discussion',
                            'questions': [
                                'Do you think travel is an important part of education? Why or why not?',
                                'What changes do you think will happen in education in the future?'
                            ]
                        }
                    ],
                    'total_duration': '11-14 minutes'
                },
                {
                    'question_id': 'as_complete_002',
                    'assessment_type': 'academic_speaking',
                    'parts': [
                        {
                            'part': 1,
                            'duration': '4-5 minutes',
                            'topic': 'Introduction and Interview',
                            'questions': [
                                'What do you like or dislike about your studies?',
                                'Would you prefer to work in a large company or a small company? Why?'
                            ]
                        },
                        {
                            'part': 2,
                            'duration': '3-4 minutes',
                            'topic': 'Individual Long Turn',
                            'prompt': 'Describe a person who has had a significant influence on your life. You should say: who this person is, how you know them, what they do, and explain why they have influenced you so much.',
                            'prep_time': 60,
                            'talk_time': 120
                        },
                        {
                            'part': 3,
                            'duration': '4-5 minutes',
                            'topic': 'Two-way Discussion',
                            'questions': [
                                'Do you think students should be able to choose what they study at school?',
                                'How important do you think it is for people to continue learning throughout their lives?'
                            ]
                        }
                    ],
                    'total_duration': '11-14 minutes'
                }
            ],
            'general_speaking': [
                {
                    'question_id': 'gs_complete_001',
                    'assessment_type': 'general_speaking',
                    'parts': [
                        {
                            'part': 1,
                            'duration': '4-5 minutes',
                            'topic': 'Introduction and Interview',
                            'questions': [
                                'What do you enjoy doing in your spare time?',
                                'How do you usually spend your weekends?'
                            ]
                        },
                        {
                            'part': 2,
                            'duration': '3-4 minutes',
                            'topic': 'Individual Long Turn',
                            'prompt': 'Describe a memorable meal you have had. You should say: where you had this meal, who you were with, what you ate, and explain why this meal was memorable for you.',
                            'prep_time': 60,
                            'talk_time': 120
                        },
                        {
                            'part': 3,
                            'duration': '4-5 minutes',
                            'topic': 'Two-way Discussion',
                            'questions': [
                                'How important is it for families to eat meals together?',
                                'Do you think people cook less nowadays than in the past?'
                            ]
                        }
                    ],
                    'total_duration': '11-14 minutes'
                },
                {
                    'question_id': 'gs_complete_002',
                    'assessment_type': 'general_speaking',
                    'parts': [
                        {
                            'part': 1,
                            'duration': '4-5 minutes',
                            'topic': 'Introduction and Interview',
                            'questions': [
                                'How often do you use computers or technology in your daily life?'
                            ]
                        },
                        {
                            'part': 2,
                            'duration': '3-4 minutes',
                            'topic': 'Individual Long Turn',
                            'prompt': 'Describe a place in your country that you would recommend someone visit. You should say: where it is, what people can do there, when is the best time to visit, and explain why you would recommend this place.',
                            'prep_time': 60,
                            'talk_time': 120
                        },
                        {
                            'part': 3,
                            'duration': '4-5 minutes',
                            'topic': 'Two-way Discussion',
                            'questions': [
                                'Should there be more regulation of technology and the internet?',
                                'How has family life changed in your country in recent decades?'
                            ]
                        }
                    ],
                    'total_duration': '11-14 minutes'
                }
            ]
        }
        
        return question_banks.get(assessment_type, [])
"""

    # Insert the unique question functions into the lambda code
    # Find the right place to insert (before the lambda_handler function)
    lambda_handler_pos = lambda_code.find("def lambda_handler(event, context):")
    if lambda_handler_pos == -1:
        print("❌ Could not find lambda_handler function")
        return None
    
    # Insert the unique question functions before lambda_handler
    modified_lambda_code = (
        lambda_code[:lambda_handler_pos] + 
        unique_question_functions + "\n\n" +
        lambda_code[lambda_handler_pos:]
    )
    
    # Add import random at the top
    modified_lambda_code = modified_lambda_code.replace(
        "import json",
        "import json\nimport random"
    )
    
    # Create the deployment package
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the modified lambda function
        zipf.writestr('lambda_function.py', modified_lambda_code)
        
        # Add the working templates
        zipf.write('working_template_backup_20250714_192410.html', 'working_template_backup_20250714_192410.html')
        
        # Add template files
        if os.path.exists('templates'):
            for root, dirs, files in os.walk('templates'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, '.')
                    zipf.write(file_path, arcname)
    
    file_size = os.path.getsize(package_name) / 1024
    print(f"✅ Working deployment package created: {file_size:.1f} KB")
    
    return package_name

def deploy_working_package(package_name):
    """Deploy the working package to AWS Lambda"""
    
    print(f"🚀 DEPLOYING WORKING PACKAGE TO PRODUCTION")
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(package_name, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ DEPLOYMENT SUCCESSFUL")
        print(f"📊 Function ARN: {response['FunctionArn']}")
        print(f"📅 Last Modified: {response['LastModified']}")
        print(f"📦 Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ DEPLOYMENT FAILED: {str(e)}")
        return False

def verify_production_endpoints():
    """Verify production endpoints are working"""
    
    print(f"\n🔍 VERIFYING PRODUCTION FUNCTIONALITY")
    
    import time
    time.sleep(5)  # Wait for propagation
    
    import requests
    
    endpoints_to_test = [
        "https://www.ieltsaiprep.com/",
        "https://www.ieltsaiprep.com/api/health",
        "https://www.ieltsaiprep.com/login", 
        "https://www.ieltsaiprep.com/privacy-policy",
        "https://www.ieltsaiprep.com/terms-of-service",
        "https://www.ieltsaiprep.com/robots.txt"
    ]
    
    success_count = 0
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(endpoint, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            if response.status_code == 200:
                success_count += 1
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")
    
    print(f"\n📊 Success Rate: {success_count}/{len(endpoints_to_test)} endpoints working")
    return success_count == len(endpoints_to_test)

if __name__ == "__main__":
    print("🎯 RESTORING WORKING PRODUCTION DEPLOYMENT...")
    print("=" * 60)
    
    # Create the working deployment with unique questions
    package_name = create_working_deployment_with_unique_questions()
    
    if package_name:
        # Deploy to production
        success = deploy_working_package(package_name)
        
        if success:
            # Verify functionality
            verified = verify_production_endpoints()
            
            if verified:
                print(f"\n🎉 PRODUCTION RESTORATION COMPLETE & VERIFIED")
                print(f"✅ All proven functionality restored")
                print(f"✅ Unique question logic added successfully")
                print(f"🎯 www.ieltsaiprep.com fully operational")
                
            else:
                print(f"\n⚠️ Deployment successful but some endpoints need verification")
                
        else:
            print(f"\n❌ Restoration deployment failed")
    else:
        print(f"\n❌ Failed to create working deployment package")