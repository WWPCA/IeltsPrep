import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('ielts-genai-prep-users')
assessments_table = dynamodb.Table('ielts-genai-prep-assessments')

def lambda_handler(event, context):
    """
    Main Lambda handler for user management endpoints
    """
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # Validate authentication for all endpoints
        auth_result = validate_auth_token(event)
        if auth_result['statusCode'] != 200:
            return auth_result
        
        user_data = json.loads(auth_result['body'])
        
        if http_method == 'GET' and path == '/dashboard':
            return handle_dashboard(user_data)
        elif http_method == 'GET' and path == '/my-profile':
            return handle_my_profile(user_data)
        elif http_method == 'GET' and path == '/api/user-profile':
            return handle_api_user_profile(user_data)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error in user lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_dashboard(user_data):
    """
    Get user dashboard data with assessment history and progress
    """
    try:
        user_id = user_data['user_id']
        
        # Get user profile
        user_response = users_table.get_item(Key={'email': user_data['email']})
        if 'Item' not in user_response:
            return create_response(404, {'error': 'User not found'})
        
        user_profile = user_response['Item']
        
        # Get user's assessment history
        assessments = get_user_assessments(user_id)
        
        # Calculate statistics
        stats = calculate_user_stats(assessments)
        
        # Get recent activity
        recent_activity = get_recent_activity(user_id, assessments)
        
        dashboard_data = {
            'user': {
                'user_id': user_profile['user_id'],
                'email': user_profile['email'],
                'created_at': user_profile.get('created_at'),
                'last_login': user_profile.get('last_login'),
                'subscription_status': user_profile.get('subscription_status', 'inactive'),
                'assessments_remaining': user_profile.get('assessments_remaining', 0)
            },
            'statistics': stats,
            'recent_assessments': assessments[:5],  # Last 5 assessments
            'recent_activity': recent_activity,
            'progress': {
                'total_assessments': len(assessments),
                'completed_assessments': len([a for a in assessments if a.get('status') == 'completed']),
                'average_band_score': stats.get('average_band_score', 0),
                'improvement_trend': calculate_improvement_trend(assessments)
            }
        }
        
        return create_response(200, {
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:
        print(f"Error in handle_dashboard: {str(e)}")
        return create_response(500, {'error': 'Failed to load dashboard'})

def handle_my_profile(user_data):
    """
    Get detailed user profile information
    """
    try:
        user_response = users_table.get_item(Key={'email': user_data['email']})
        if 'Item' not in user_response:
            return create_response(404, {'error': 'User not found'})
        
        user_profile = user_response['Item']
        
        # Get assessment summary
        assessments = get_user_assessments(user_data['user_id'])
        assessment_summary = get_assessment_summary(assessments)
        
        profile_data = {
            'personal_info': {
                'user_id': user_profile['user_id'],
                'email': user_profile['email'],
                'created_at': user_profile.get('created_at'),
                'last_login': user_profile.get('last_login'),
                'platform': user_profile.get('platform', 'web')
            },
            'subscription': {
                'status': user_profile.get('subscription_status', 'inactive'),
                'assessments_remaining': user_profile.get('assessments_remaining', 0),
                'purchase_method': user_profile.get('purchase_method', 'unknown')
            },
            'assessment_history': assessment_summary,
            'preferences': {
                'notification_enabled': user_profile.get('notification_enabled', True),
                'language_preference': user_profile.get('language_preference', 'en'),
                'timezone': user_profile.get('timezone', 'UTC')
            }
        }
        
        return create_response(200, {
            'success': True,
            'profile': profile_data
        })
        
    except Exception as e:
        print(f"Error in handle_my_profile: {str(e)}")
        return create_response(500, {'error': 'Failed to load profile'})

def handle_api_user_profile(user_data):
    """
    API endpoint for user profile (mobile app compatible)
    """
    try:
        user_response = users_table.get_item(Key={'email': user_data['email']})
        if 'Item' not in user_response:
            return create_response(404, {'error': 'User not found'})
        
        user_profile = user_response['Item']
        
        # Simplified profile data for API
        api_profile = {
            'user_id': user_profile['user_id'],
            'email': user_profile['email'],
            'subscription_status': user_profile.get('subscription_status', 'inactive'),
            'assessments_remaining': user_profile.get('assessments_remaining', 0),
            'last_login': user_profile.get('last_login'),
            'platform': user_profile.get('platform', 'web')
        }
        
        return create_response(200, {
            'success': True,
            'user': api_profile
        })
        
    except Exception as e:
        print(f"Error in handle_api_user_profile: {str(e)}")
        return create_response(500, {'error': 'Failed to load user profile'})

def get_user_assessments(user_id):
    """
    Get all assessments for a user
    """
    try:
        # Query assessments table by user_id
        # Note: This assumes you have a GSI on user_id
        response = assessments_table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        assessments = response.get('Items', [])
        
        # Sort by timestamp (most recent first)
        assessments.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        
        return assessments
        
    except Exception as e:
        print(f"Error getting user assessments: {str(e)}")
        return []

def calculate_user_stats(assessments):
    """
    Calculate user statistics from assessments
    """
    try:
        if not assessments:
            return {
                'total_assessments': 0,
                'completed_assessments': 0,
                'average_band_score': 0,
                'best_band_score': 0,
                'assessment_types': {}
            }
        
        completed = [a for a in assessments if a.get('status') == 'completed']
        
        # Calculate band scores
        band_scores = []
        for assessment in completed:
            if 'ai_evaluation' in assessment and isinstance(assessment['ai_evaluation'], dict):
                band_score = assessment['ai_evaluation'].get('overall_band', 0)
                if band_score > 0:
                    band_scores.append(band_score)
        
        # Count by assessment type
        type_counts = {}
        for assessment in assessments:
            assessment_type = assessment.get('assessment_type', 'unknown')
            type_counts[assessment_type] = type_counts.get(assessment_type, 0) + 1
        
        return {
            'total_assessments': len(assessments),
            'completed_assessments': len(completed),
            'average_band_score': sum(band_scores) / len(band_scores) if band_scores else 0,
            'best_band_score': max(band_scores) if band_scores else 0,
            'assessment_types': type_counts
        }
        
    except Exception as e:
        print(f"Error calculating user stats: {str(e)}")
        return {}

def get_recent_activity(user_id, assessments):
    """
    Get recent user activity
    """
    try:
        recent_activity = []
        
        for assessment in assessments[:10]:  # Last 10 activities
            activity = {
                'type': 'assessment',
                'assessment_type': assessment.get('assessment_type'),
                'status': assessment.get('status'),
                'timestamp': assessment.get('submitted_at'),
                'description': f"Completed {assessment.get('assessment_type', 'assessment')}"
            }
            recent_activity.append(activity)
        
        return recent_activity
        
    except Exception as e:
        print(f"Error getting recent activity: {str(e)}")
        return []

def get_assessment_summary(assessments):
    """
    Get assessment summary by type
    """
    try:
        summary = {}
        
        for assessment in assessments:
            assessment_type = assessment.get('assessment_type', 'unknown')
            
            if assessment_type not in summary:
                summary[assessment_type] = {
                    'total': 0,
                    'completed': 0,
                    'average_score': 0,
                    'best_score': 0,
                    'last_attempt': None
                }
            
            summary[assessment_type]['total'] += 1
            
            if assessment.get('status') == 'completed':
                summary[assessment_type]['completed'] += 1
                
                # Update last attempt
                if not summary[assessment_type]['last_attempt'] or \
                   assessment.get('submitted_at', '') > summary[assessment_type]['last_attempt']:
                    summary[assessment_type]['last_attempt'] = assessment.get('submitted_at')
                
                # Update scores if available
                if 'ai_evaluation' in assessment and isinstance(assessment['ai_evaluation'], dict):
                    band_score = assessment['ai_evaluation'].get('overall_band', 0)
                    if band_score > 0:
                        if summary[assessment_type]['best_score'] < band_score:
                            summary[assessment_type]['best_score'] = band_score
        
        return summary
        
    except Exception as e:
        print(f"Error getting assessment summary: {str(e)}")
        return {}

def calculate_improvement_trend(assessments):
    """
    Calculate improvement trend over time
    """
    try:
        if len(assessments) < 2:
            return 'insufficient_data'
        
        # Get completed assessments with scores
        scored_assessments = []
        for assessment in assessments:
            if (assessment.get('status') == 'completed' and 
                'ai_evaluation' in assessment and 
                isinstance(assessment['ai_evaluation'], dict)):
                
                band_score = assessment['ai_evaluation'].get('overall_band', 0)
                if band_score > 0:
                    scored_assessments.append({
                        'score': band_score,
                        'date': assessment.get('submitted_at', '')
                    })
        
        if len(scored_assessments) < 2:
            return 'insufficient_data'
        
        # Sort by date
        scored_assessments.sort(key=lambda x: x['date'])
        
        # Compare first half with second half
        mid_point = len(scored_assessments) // 2
        first_half_avg = sum(a['score'] for a in scored_assessments[:mid_point]) / mid_point
        second_half_avg = sum(a['score'] for a in scored_assessments[mid_point:]) / (len(scored_assessments) - mid_point)
        
        if second_half_avg > first_half_avg + 0.2:
            return 'improving'
        elif first_half_avg > second_half_avg + 0.2:
            return 'declining'
        else:
            return 'stable'
            
    except Exception as e:
        print(f"Error calculating improvement trend: {str(e)}")
        return 'unknown'

def validate_auth_token(event):
    """
    Validate authentication token from request headers
    """
    try:
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Invalid authorization header'})
        
        # For now, mock validation - integrate with auth_handler in production
        return create_response(200, {
            'user_id': 'mock_user_id',
            'email': 'user@example.com'
        })
        
    except Exception as e:
        return create_response(401, {'error': 'Authentication failed'})

def create_response(status_code, body):
    """
    Create standardized API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }