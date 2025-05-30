"""
Assessment Submission Routes for TrueScore® and ClearScore®
This module provides API endpoints for submitting writing and speaking assessments
with enhanced security and AWS API resilience.
"""

import time
from main import app
from flask import request, jsonify
from flask_login import login_required, current_user
from botocore.exceptions import ClientError, BotoCoreError
from models import db, UserAssessmentAssignment


def call_aws_api_with_retry(func, *args, **kwargs):
    """
    Call AWS API with retry logic for resilience against throttling and network issues.
    """
    retries = 3
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ThrottlingException' and attempt < retries - 1:
                app.logger.warning(f"AWS API throttling, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
                continue
            elif error_code in ['ServiceUnavailable', 'InternalServerError'] and attempt < retries - 1:
                app.logger.warning(f"AWS service error, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
                continue
            else:
                app.logger.error(f"AWS API error: {e}")
                raise
        except BotoCoreError as e:
            if attempt < retries - 1:
                app.logger.warning(f"AWS SDK error, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
                continue
            else:
                app.logger.error(f"AWS SDK error: {e}")
                raise
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            raise


@app.route('/api/submit-writing', methods=['POST'])
@login_required
def submit_writing():
    """Submit writing assessment for TrueScore® AI evaluation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        product_id = data.get('product_id')
        task_type = data.get('task_type')
        text = data.get('text')

        # Enhanced input validation
        if not all([product_id, task_type, text]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        if len(text) > 10000:  # Reasonable limit for IELTS writing
            return jsonify({'success': False, 'error': 'Text too long'}), 400

        if task_type not in ['task1', 'task2']:
            return jsonify({'success': False, 'error': 'Invalid task type'}), 400

        # Check if user has active assessment
        assignment = UserAssessmentAssignment.query.filter_by(
            user_id=current_user.id,
            assessment_type=product_id,
            status='active'
        ).first()
        
        if not assignment:
            return jsonify({'success': False, 'error': 'No active assessment available'}), 403

        if product_id in ['academic_writing', 'general_writing']:
            try:
                # Import TrueScore® assessment functions
                from enhanced_nova_assessment import assess_writing_task1, assess_writing_task2
                
                # Use retry logic for AWS API calls
                if task_type == 'task1':
                    result = call_aws_api_with_retry(assess_writing_task1, text, current_user.id)
                else:
                    result = call_aws_api_with_retry(assess_writing_task2, text, current_user.id)
                
                if result.get('success'):
                    # Mark assignment as used
                    assignment.status = 'completed'
                    db.session.commit()
                    app.logger.info(f"TrueScore® assessment completed for user {current_user.id}")
                    
                return jsonify(result), 200
                
            except ClientError as e:
                app.logger.error(f"TrueScore® AWS error: {e}")
                return jsonify({'success': False, 'error': 'TrueScore® service temporarily unavailable'}), 503
            except Exception as e:
                app.logger.error(f"TrueScore® assessment error: {e}")
                return jsonify({'success': False, 'error': 'TrueScore® evaluation failed'}), 500
                
        return jsonify({'success': False, 'error': 'Invalid product or task'}), 400
        
    except Exception as e:
        app.logger.error(f"Writing assessment error for user {current_user.id}: {e}")
        return jsonify({'success': False, 'error': 'Assessment failed'}), 500


@app.route('/api/submit-speaking', methods=['POST'])
@login_required
def submit_speaking():
    """Submit speaking assessment for ClearScore® AI evaluation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        product_id = data.get('product_id')
        audio_data = data.get('audio_data')

        # Enhanced input validation
        if not all([product_id, audio_data]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        if len(audio_data) > 50000000:  # 50MB limit for audio
            return jsonify({'success': False, 'error': 'Audio file too large'}), 400

        # Check if user has active assessment
        assignment = UserAssessmentAssignment.query.filter_by(
            user_id=current_user.id,
            assessment_type=product_id,
            status='active'
        ).first()
        
        if not assignment:
            return jsonify({'success': False, 'error': 'No active assessment available'}), 403

        if product_id in ['academic_speaking', 'general_speaking']:
            try:
                # Import ClearScore® services
                from enhanced_nova_assessment import analyze_speaking_response
                from aws_services import aws_nova_micro_client
                
                # AWS Sonic analysis with retry logic
                sonic_result = call_aws_api_with_retry(analyze_speaking_response, audio_data)
                if not sonic_result.get('success'):
                    return jsonify(sonic_result), 500

                # AWS Nova Micro feedback generation with retry logic
                nova_result = call_aws_api_with_retry(
                    aws_nova_micro_client.generate_feedback,
                    analysis=sonic_result['analysis'],
                    rubric='ielts_speaking'
                )
                
                if nova_result.get('success'):
                    # Mark assignment as used
                    assignment.status = 'completed'
                    db.session.commit()
                    app.logger.info(f"ClearScore® assessment completed for user {current_user.id}")
                    
                return jsonify({
                    'success': nova_result.get('success'),
                    'score': sonic_result.get('score'),
                    'feedback': nova_result.get('feedback')
                }), 200
                
            except ClientError as e:
                app.logger.error(f"ClearScore® AWS error: {e}")
                return jsonify({'success': False, 'error': 'ClearScore® service temporarily unavailable'}), 503
            except Exception as e:
                app.logger.error(f"ClearScore® assessment error: {e}")
                return jsonify({'success': False, 'error': 'ClearScore® evaluation failed'}), 500
                
        return jsonify({'success': False, 'error': 'Invalid product'}), 400
        
    except Exception as e:
        app.logger.error(f"Speaking assessment error for user {current_user.id}: {e}")
        return jsonify({'success': False, 'error': 'Assessment failed'}), 500


print("Assessment submission routes for TrueScore® and ClearScore® added successfully.")