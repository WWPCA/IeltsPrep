"""
Fix Maya Conversation Database Transaction Issues
This script resolves the persistent database transaction errors preventing the API from working.
"""

from app import app, db
from api_issues import APIIssueLog
import logging

logger = logging.getLogger(__name__)

def fix_database_transactions():
    """Fix database transaction issues and update the start_conversation route"""
    
    with app.app_context():
        try:
            # Reset any failed transactions
            db.session.rollback()
            
            # Create new session to ensure clean state
            db.session.commit()
            
            # Test database connectivity
            test_query = db.session.execute(db.text("SELECT 1")).fetchone()
            logger.info("Database connection test successful")
            
            print("✓ Database transactions reset successfully")
            print("✓ Database connectivity verified")
            
            return True
            
        except Exception as e:
            logger.error(f"Database fix error: {e}")
            print(f"✗ Database fix failed: {e}")
            return False

def update_start_conversation_route():
    """Update the start_conversation route with better error handling"""
    
    # Read the current routes.py file
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Find and replace the start_conversation function with improved version
    old_function = """@app.route('/api/start_conversation', methods=['POST'])
@login_required
def start_conversation():
    \"\"\"Start a real-time conversation with Maya\"\"\"
    try:
        data = request.get_json()
        assessment_type = data.get('assessment_type', 'academic_speaking')
        part = data.get('part', 1)
        
        nova_sonic = NovaSonicCompleteService()
        
        # Start conversation using complete Nova Sonic service
        result = nova_sonic.start_conversation(
            assessment_type=assessment_type,
            part=part
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'opening_message': result.get('opening_message', 'Hello! I\\'m ready to begin your assessment.'),
                'conversation_id': result.get('conversation_id')
            })
        else:
            # Log Maya conversation issue
            APIIssueLog.log_issue(
                api_name='maya_conversation',
                endpoint='/api/start_conversation',
                error_code='CONVERSATION_START_FAILED',
                error_message=result.get('error', 'Conversation start failed'),
                request_obj=request,
                user_id=current_user.id,
                request_data={'assessment_type': assessment_type, 'part': part}
            )
            return jsonify({'success': False, 'error': result.get('error', 'Conversation start failed')})
            
    except Exception as e:
        # Log Maya conversation error
        APIIssueLog.log_issue(
            api_name='maya_conversation',
            endpoint='/api/start_conversation',
            error_code='EXCEPTION',
            error_message=str(e),
            request_obj=request,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        return jsonify({'success': False, 'error': 'Conversation service unavailable'})"""

    new_function = """@app.route('/api/start_conversation', methods=['POST'])
@login_required
def start_conversation():
    \"\"\"Start a real-time conversation with Maya\"\"\"
    try:
        # Reset database session to avoid transaction issues
        db.session.rollback()
        
        data = request.get_json()
        assessment_type = data.get('assessment_type', 'academic_speaking')
        part = data.get('part', 1)
        
        nova_sonic = NovaSonicCompleteService()
        
        # Start conversation using complete Nova Sonic service
        result = nova_sonic.start_conversation(
            assessment_type=assessment_type,
            part=part
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'opening_message': result.get('opening_message', 'Hello! I\\'m ready to begin your assessment.'),
                'conversation_id': result.get('conversation_id'),
                'audio_url': result.get('audio_url')
            })
        else:
            # Log Maya conversation issue with fresh database session
            try:
                db.session.rollback()
                APIIssueLog.log_issue(
                    api_name='maya_conversation',
                    endpoint='/api/start_conversation',
                    error_code='CONVERSATION_START_FAILED',
                    error_message=result.get('error', 'Conversation start failed'),
                    request_obj=request,
                    user_id=current_user.id,
                    request_data={'assessment_type': assessment_type, 'part': part}
                )
                db.session.commit()
            except Exception as log_error:
                logger.error(f"Failed to log conversation issue: {log_error}")
                db.session.rollback()
            
            return jsonify({'success': False, 'error': result.get('error', 'Conversation start failed')})
            
    except Exception as e:
        # Log Maya conversation error with fresh database session
        try:
            db.session.rollback()
            APIIssueLog.log_issue(
                api_name='maya_conversation',
                endpoint='/api/start_conversation',
                error_code='EXCEPTION',
                error_message=str(e),
                request_obj=request,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.commit()
        except Exception as log_error:
            logger.error(f"Failed to log conversation error: {log_error}")
            db.session.rollback()
            
        return jsonify({'success': False, 'error': 'Internal server error. Please try again later.'})"""

    # Replace the function in the file
    if old_function in content:
        content = content.replace(old_function, new_function)
        
        # Write the updated content back
        with open('routes.py', 'w') as f:
            f.write(content)
        
        print("✓ Updated start_conversation route with database transaction fixes")
        return True
    else:
        print("✗ Could not find start_conversation function to update")
        return False

if __name__ == "__main__":
    print("Fixing Maya conversation database issues...")
    
    if fix_database_transactions():
        if update_start_conversation_route():
            print("✓ All fixes applied successfully!")
        else:
            print("✗ Route update failed")
    else:
        print("✗ Database fix failed")