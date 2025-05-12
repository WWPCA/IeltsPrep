from app import app  # noqa: F401
import routes  # noqa: F401
import routes_general_reading  # noqa: F401
from flask import jsonify, request
from flask_login import login_required, current_user
from models import PracticeTest, AssessmentSession, ConnectionIssueLog, db
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and register assessment blueprints
from writing_assessment_routes import writing_assessment
from speaking_assessment_routes import speaking_assessment
from cart_routes import cart_bp
from admin_routes import admin_bp
from stripe_webhook import stripe_webhook_bp
from email_verification_routes import setup_email_verification_routes
from gdpr_routes import gdpr_bp

# Import country restriction module
from country_access_control import setup_country_restriction_routes

# Register blueprints
app.register_blueprint(writing_assessment)
app.register_blueprint(speaking_assessment)
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(stripe_webhook_bp, url_prefix='/api')
app.register_blueprint(gdpr_bp, url_prefix='/privacy')

# Set up country restriction routes (but don't apply restrictions yet - use apply_country_restrictions.py for that)
setup_country_restriction_routes(app)

# Set up email verification routes
setup_email_verification_routes(app)

# Apply country restrictions automatically at startup
try:
    from country_access_control import apply_country_restrictions
    logger.info("Applying country restrictions at startup")
    apply_country_restrictions(app)
    logger.info("Country restrictions applied successfully - access limited to CA, US, IN, NP, KW, QA")
except Exception as e:
    logger.error(f"Failed to apply country restrictions: {str(e)}")

# Import assessment products routes
import integrate_assessment_routes  # noqa: F401

# Import and add contact routes
from contact_routes import add_contact_routes
add_contact_routes(app)

# Add a ping route to maintain session activity
@app.route('/ping')
def ping():
    """Simple ping endpoint to keep sessions alive."""
    return jsonify({"status": "ok"})

# Add an API endpoint to log connection issues
@app.route('/api/log_connection_issue', methods=['POST'])
@login_required
def log_connection_issue():
    """Log connection issues for monitoring and support purposes."""
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        # Extract data from the request
        issue_type = data.get('issue_type')
        test_id = data.get('test_id')
        test_type = data.get('test_type')
        connection_info = data.get('connection_info')
        user_local_time = data.get('user_local_time')
        
        if not issue_type:
            return jsonify({"status": "error", "message": "Issue type is required"}), 400
            
        # Determine the product ID based on the test type
        product_id = None
        if test_type:
            if test_type == "writing":
                test = PracticeTest.query.get(test_id)
                if test:
                    product_id = "academic_writing" if test.ielts_test_type == "academic" else "general_writing"
            elif test_type == "speaking":
                test = PracticeTest.query.get(test_id)
                if test:
                    product_id = "academic_speaking" if test.ielts_test_type == "academic" else "general_speaking"
        
        # Check if there's an active session for this test
        session_id = None
        if product_id:
            active_session = AssessmentSession.get_active_session(current_user.id, product_id)
            if active_session:
                session_id = active_session.id
        
        # Log the connection issue
        ConnectionIssueLog.log_issue(
            current_user.id,
            issue_type,
            request,
            test_id=test_id,
            product_id=product_id,
            session_id=session_id,
            user_local_time=user_local_time,
            connection_info=connection_info
        )
        
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error logging connection issue: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
