import json
from datetime import datetime, timedelta, date
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Phone field removed as it doesn't exist in database
    region = db.Column(db.String(50), nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    assessment_package_status = db.Column(db.String(20), default="none")
    assessment_package_expiry = db.Column(db.DateTime, nullable=True)
    # App only available in English - preferred_language column retained for database compatibility
    # but not used in UI
    preferred_language = db.Column(db.String(10), default="en")
    assessment_preference = db.Column(db.String(20), default="academic")  # Options: academic, general
    # Account activation flag - only true after successful payment
    account_activated = db.Column(db.Boolean, default=False)  # Renamed from is_active to avoid UserMixin conflict
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    # target_score field removed as it doesn't exist in database
    # Admin check based on email address
    @property
    def is_admin(self):
        """Check if user is admin based on email address."""
        return self.email == "admin@ieltsaiprep.com"
    
    # Study streak tracking
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    # Store study activity history as JSON string
    _activity_history = db.Column(db.Text, default='[]')
    
    # Store assessment history as JSON string
    _assessment_history = db.Column(db.Text, default='[]')
    # Store speaking scores as JSON string
    _speaking_scores = db.Column(db.Text, default='[]')
    # Store completed assessments as JSON string
    _completed_assessments = db.Column(db.Text, default='[]')
    
    # Store password history as JSON string (stores hashed passwords only)
    _password_history = db.Column(db.Text, default='[]')
    
    @property
    def is_active(self):
        """
        Override UserMixin's is_active property to use our account_activated field.
        This ensures backward compatibility with code that expects is_active to work.
        """
        return self.account_activated
    
    def set_password(self, password):
        # Save current password to history if it exists
        if self.password_hash:
            history = json.loads(self._password_history) if self._password_history else []
            history.append({
                'hash': self.password_hash,
                'date': datetime.utcnow().isoformat()
            })
            # Keep only the last 5 passwords in history
            if len(history) > 5:
                history = history[-5:]
            self._password_history = json.dumps(history)
            
        # Set the new password
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_password_reused(self, password):
        """Check if the password has been used before"""
        if not self._password_history:
            return False
            
        history = json.loads(self._password_history)
        for item in history:
            if check_password_hash(item['hash'], password):
                return True
                
        return False
    
    @property
    def assessment_history(self):
        return json.loads(self._assessment_history)
    
    @assessment_history.setter
    def assessment_history(self, value):
        self._assessment_history = json.dumps(value)
    
    @property
    def speaking_scores(self):
        return json.loads(self._speaking_scores)
    
    @speaking_scores.setter
    def speaking_scores(self, value):
        self._speaking_scores = json.dumps(value)
    
    @property
    def activity_history(self):
        return json.loads(self._activity_history)
    
    @activity_history.setter
    def activity_history(self, value):
        self._activity_history = json.dumps(value)
        
    @property
    def completed_assessments(self):
        return json.loads(self._completed_assessments)
    
    @completed_assessments.setter
    def completed_assessments(self, value):
        self._completed_assessments = json.dumps(value)
    
    def has_taken_assessment(self, assessment_id, assessment_type=None):
        """Check if user has already taken a specific assessment"""
        for assessment in self.completed_assessments:
            if assessment['assessment_id'] == assessment_id:
                if assessment_type is None or assessment['assessment_type'] == assessment_type:
                    # Check if taken during current assessment package period
                    if self.assessment_package_expiry:
                        assessment_date = datetime.fromisoformat(assessment['date'])
                        # Get assessment package duration from assessment_history
                        package_days = 30  # Default to 30 days
                        
                        for history_item in self.assessment_history:
                            if "assessment_purchase" in history_item:
                                purchase_data = history_item["assessment_purchase"]
                                if "expiry_date" in purchase_data:
                                    # Calculate days between purchase and expiry
                                    purchase_date = datetime.fromisoformat(purchase_data["purchase_date"])
                                    expiry_date = datetime.fromisoformat(purchase_data["expiry_date"])
                                    package_days = (expiry_date - purchase_date).days
                                    break
                            elif "assessment_package_data" in history_item:
                                package_data = history_item["assessment_package_data"]
                                if "plan" in package_data:
                                    # Value pack (4 assessments) = 30 days, others = 15 days
                                    package_days = 30 if "pro" in package_data["plan"] else 15
                                    break
                        
                        # If assessment was taken before current assessment package started, allow retaking
                        package_start = self.assessment_package_expiry - timedelta(days=package_days)
                        if assessment_date < package_start:
                            return False
                    return True
        return False
        
    def mark_assessment_completed(self, assessment_id, assessment_type):
        """Mark an assessment as completed by this user"""
        completed = self.completed_assessments
        completed.append({
            'assessment_id': assessment_id,
            'assessment_type': assessment_type,
            'date': datetime.utcnow().isoformat()
        })
        self.completed_assessments = completed
    
    def update_streak(self):
        """Update the user's study streak based on their activity"""
        today = date.today()
        
        # If this is the first activity ever
        if not self.last_activity_date:
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = today
            
            # Add today to activity history
            history = self.activity_history
            history.append(today.isoformat())
            self.activity_history = history
            return
        
        # If already logged activity today, no need to update
        if self.last_activity_date == today:
            return
            
        # Check if the last activity was yesterday
        yesterday = today - timedelta(days=1)
        if self.last_activity_date == yesterday:
            # Continuing the streak
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        elif self.last_activity_date < yesterday:
            # Streak broken - start a new one
            self.current_streak = 1
            
        # Update last activity date
        self.last_activity_date = today
        
        # Add to activity history
        history = self.activity_history
        history.append(today.isoformat())
        self.activity_history = history
    
    def get_streak_data(self):
        """Get formatted streak data for visualization"""
        # Get last 30 days of activity for visualization
        today = date.today()
        last_30_days = []
        
        # Create a list of the last 30 days with activity status
        for i in range(30):
            day_date = today - timedelta(days=29-i)
            active = day_date.isoformat() in self.activity_history
            last_30_days.append({
                'date': day_date.isoformat(),
                'active': active,
                'day_name': day_date.strftime('%a')[:1]  # First letter of day name
            })
            
        return {
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_30_days': last_30_days
        }
    
    def has_active_assessment_package(self):
        """
        Check if user has access to purchased assessment packages.
        """
        # Check if assessment package has expired first
        if self.assessment_package_expiry and self.assessment_package_expiry <= datetime.utcnow():
            # Assessment package has expired - update status
            self.assessment_package_status = "expired"
            db.session.commit()
            return False
            
        # Check for assessment purchases in assessment_history
        for history_item in self.assessment_history:
            if "assessment_purchase" in history_item:
                purchase_data = history_item["assessment_purchase"]
                if "expiry_date" in purchase_data:
                    # Check if purchase is still valid
                    expiry_date = datetime.fromisoformat(purchase_data["expiry_date"])
                    if expiry_date > datetime.utcnow():
                        return True
            
        # Simple list of all possible assessment package types
        valid_packages = [
            "Academic Writing", "Academic Speaking", 
            "General Writing", "General Speaking"
        ]
            
        # Verify that assessment package status is valid and hasn't expired
        if (self.assessment_package_status in valid_packages and 
                self.assessment_package_status != "none" and
                self.assessment_package_status != "expired" and
                (not self.assessment_package_expiry or self.assessment_package_expiry > datetime.utcnow())):
            return True
                
        return False
        
    def is_speaking_only_user(self):
        """
        Check if user has a speaking-only assessment package.
        """
        # Check if current assessment package is a speaking-only type
        speaking_packages = ["Academic Speaking", "General Speaking"]
        
        return self.assessment_package_status in speaking_packages
        
    def get_remaining_speaking_assessments(self):
        """
        Get the number of speaking assessments remaining for users with speaking packages.
        """
        # Default to 0 if not a speaking-only user
        if not self.is_speaking_only_user():
            return 0
            
        # All speaking assessment packages include 4 assessments
        if self.assessment_package_status in ["Academic Speaking", "General Speaking"]:
            return 4
            
        return 0
        
    def is_email_verified(self):
        """
        Check if the user's email is verified.
        
        Returns:
            bool: True if the email is verified, False otherwise
        """
        return self.email_verified
        
    def verify_email(self, token):
        """
        Verify the user's email with the provided token.
        
        Args:
            token (str): The verification token to check
            
        Returns:
            bool: True if verification was successful, False otherwise
        """
        if not self.email_verification_token or not token:
            return False
            
        if self.email_verification_token == token:
            self.email_verified = True
            self.email_verification_token = None
            db.session.commit()
            return True
            
        return False
    
    def use_speaking_assessment(self):
        """
        Mark that a speaking assessment has been used for speaking assessment packages.
        """
        if not self.is_speaking_only_user():
            return False
            
        # All speaking packages now use a fixed number of assessments (4)
        # Simply record usage in assessment history
        history = self.assessment_history
        
        # Create new speaking usage record
        usage_record = {
            "speaking_usage": {
                "date": datetime.utcnow().isoformat(),
                "package": self.assessment_package_status
            }
        }
        
        history.append(usage_record)
        self.assessment_history = history
        return True
    
    def __repr__(self):
        return f'<User {self.username}>'

# Model for assessment structure information pages
class AssessmentStructure(db.Model):
    __tablename__ = 'test_structure'  # Keep the table name for database compatibility
    
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50), nullable=False)  # Keeping "test_type" column name for database compatibility
    description = db.Column(db.Text, nullable=False)
    format_details = db.Column(db.Text, nullable=False)
    sample_image_url = db.Column(db.String(256), nullable=True)
    
    def __repr__(self):
        return f'<AssessmentStructure {self.test_type}>'  # test_type is the database column name

class Assessment(db.Model):
    """Model for IELTS assessments"""
    id = db.Column(db.Integer, primary_key=True)
    assessment_type = db.Column(db.String(50), nullable=False)  # academic_writing, academic_speaking, general_writing, general_speaking
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="active")  # active, inactive
    _criteria = db.Column(db.Text, nullable=True)  # JSON string with assessment criteria
    _questions = db.Column(db.Text, nullable=True)  # JSON string with assessment questions/content
    
    @property
    def criteria(self):
        return json.loads(self._criteria) if self._criteria else []
    
    @criteria.setter
    def criteria(self, value):
        self._criteria = json.dumps(value)
        
    @property
    def questions(self):
        return json.loads(self._questions) if self._questions else []
    
    @questions.setter
    def questions(self, value):
        self._questions = json.dumps(value)
    
    def __repr__(self):
        return f'<Assessment {self.assessment_type}: {self.title}>'

class UserAssessmentAttempt(db.Model):
    """Model for user assessment attempts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # listening, reading, writing, speaking
    status = db.Column(db.String(20), nullable=False, default="in_progress")  # in_progress, completed, cancelled
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    
    # Store results as JSON string
    _results = db.Column(db.Text, nullable=True)  # JSON string with assessment results
    
    # Store GenAI assessment data (band scores, feedback, etc.)
    _genai_assessment = db.Column(db.Text, nullable=True)  # JSON string with GenAI assessment data
    
    # Cloud storage references
    gcp_audio_url = db.Column(db.String(256), nullable=True)  # Speaking recording GCP URL
    gcp_transcript_url = db.Column(db.String(256), nullable=True)  # Speaking transcript GCP URL
    gcp_assessment_url = db.Column(db.String(256), nullable=True)  # Full assessment data GCP URL
    
    @property
    def results(self):
        return json.loads(self._results) if self._results else {}
    
    @results.setter
    def results(self, value):
        self._results = json.dumps(value)
        
    @property
    def genai_assessment(self):
        return json.loads(self._genai_assessment) if self._genai_assessment else {}
    
    @genai_assessment.setter
    def genai_assessment(self, value):
        self._genai_assessment = json.dumps(value)
    
    def __repr__(self):
        return f'<UserAssessmentAttempt {self.id}: {self.assessment_type} by User {self.user_id}>'

class WritingResponse(db.Model):
    """Model for IELTS writing responses"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempt.id'), nullable=False)
    task_number = db.Column(db.Integer, nullable=False)  # 1 or 2
    response_text = db.Column(db.Text, nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Store GenAI assessment data for this specific writing task
    _assessment_data = db.Column(db.Text, nullable=True)  # JSON string with detailed GenAI assessment
    
    @property
    def assessment_data(self):
        return json.loads(self._assessment_data) if self._assessment_data else {}
    
    @assessment_data.setter
    def assessment_data(self, value):
        self._assessment_data = json.dumps(value)
    
    def __repr__(self):
        return f'<WritingResponse {self.id}: Task {self.task_number} for Attempt {self.attempt_id}>'

class AssessmentSpeakingResponse(db.Model):
    """Model for IELTS speaking assessment responses"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempt.id'), nullable=False)
    part_number = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    audio_filename = db.Column(db.String(256), nullable=True)  # Local audio filename
    transcript_text = db.Column(db.Text, nullable=True)  # Transcription of audio
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Store GenAI assessment data for this specific speaking part
    _assessment_data = db.Column(db.Text, nullable=True)  # JSON string with detailed GenAI assessment
    
    @property
    def assessment_data(self):
        return json.loads(self._assessment_data) if self._assessment_data else {}
    
    @assessment_data.setter
    def assessment_data(self, value):
        self._assessment_data = json.dumps(value)
    
    def __repr__(self):
        return f'<AssessmentSpeakingResponse {self.id}: Part {self.part_number} for Attempt {self.attempt_id}>'


class UserAssessmentAssignment(db.Model):
    """Track which assessments are assigned to each user to ensure no repeats"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type = db.Column(db.String(20), nullable=False)  # academic or general
    assigned_assessment_ids = db.Column(db.Text, nullable=False)  # JSON array of assigned assessment IDs
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    
    @property
    def assessment_ids(self):
        """Get the list of assigned assessment IDs"""
        return json.loads(self.assigned_assessment_ids)
    
    @assessment_ids.setter
    def assessment_ids(self, value):
        """Set the list of assigned assessment IDs"""
        self.assigned_assessment_ids = json.dumps(value)
        
    def __repr__(self):
        return f'<UserAssessmentAssignment User:{self.user_id} Type:{self.assessment_type} Assessments:{self.assigned_assessment_ids}>'

# UserTestAssignment class has been removed - no backward compatibility needed

class ConnectionIssueLog(db.Model):
    """Track connection issues for monitoring and support purposes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, nullable=True)  # ID of the assessment being taken
    product_id = db.Column(db.String(50), nullable=True)  # academic_writing, academic_speaking, etc.
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_session.id'), nullable=True)
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_local_time = db.Column(db.String(50), nullable=True)  # Stored as string to preserve client timezone info
    issue_type = db.Column(db.String(50), nullable=False)  # disconnect, reconnect, session_restart, etc.
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    browser_info = db.Column(db.Text, nullable=True)  # JSON string with browser details
    connection_info = db.Column(db.Text, nullable=True)  # JSON string with connection details
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_method = db.Column(db.String(50), nullable=True)  # auto_restart, admin_intervention, etc.
    
    def __repr__(self):
        return f'<ConnectionIssueLog {self.id} - User {self.user_id} - {self.issue_type}>'
    
    @classmethod
    def log_issue(cls, user_id, issue_type, request_obj=None, **kwargs):
        """Log a connection issue with details from request and additional data"""
        log_entry = cls(
            user_id=user_id,
            issue_type=issue_type,
            assessment_id=kwargs.get('assessment_id'),
            product_id=kwargs.get('product_id'),
            session_id=kwargs.get('session_id'),
            user_local_time=kwargs.get('user_local_time')
        )
        
        # Capture request data if available
        if request_obj:
            log_entry.ip_address = request_obj.remote_addr
            log_entry.user_agent = request_obj.user_agent.string
            
            # Extract and store browser info
            browser_info = {
                'browser': request_obj.user_agent.browser,
                'version': request_obj.user_agent.version,
                'platform': request_obj.user_agent.platform,
                'language': request_obj.accept_languages.best
            }
            log_entry.browser_info = json.dumps(browser_info)
            
            # Store connection info if provided
            if 'connection_info' in kwargs:
                log_entry.connection_info = json.dumps(kwargs.get('connection_info'))
        
        # Try to get location data from IP using geoip if available
        try:
            if log_entry.ip_address and hasattr(request_obj, 'geoip'):
                log_entry.city = request_obj.geoip.get('city')
                log_entry.country = request_obj.geoip.get('country_name')
        except:
            pass  # Ignore geoip errors
            
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
        
    @classmethod
    def mark_resolved(cls, issue_id, resolution_method="auto_restart"):
        """Mark a connection issue as resolved"""
        log_entry = cls.query.get(issue_id)
        if log_entry:
            log_entry.resolved = True
            log_entry.resolved_at = datetime.utcnow()
            log_entry.resolution_method = resolution_method
            db.session.add(log_entry)
            db.session.commit()
        return log_entry

class AssessmentSession(db.Model):
    """Track assessment sessions for products to allow restarts when connection issues occur"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.String(50), nullable=False)  # academic_writing, academic_speaking, etc.
    assessment_id = db.Column(db.Integer, nullable=True)  # ID of the assessment currently being taken
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    marked_complete_at = db.Column(db.DateTime, nullable=True)
    submitted = db.Column(db.Boolean, default=False)
    submission_failed = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        status = "Completed" if self.completed else "In Progress"
        if self.submission_failed:
            status = "Failed"
        return f'<AssessmentSession {self.product_id} for User:{self.user_id}, Status:{status}>'
    
    def update_last_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def mark_complete(self):
        """Mark this session as completed"""
        self.completed = True
        self.marked_complete_at = datetime.utcnow()
        db.session.commit()
    
    def mark_submitted(self):
        """Mark this session as submitted"""
        self.submitted = True
        db.session.commit()
    
    def mark_failed(self, reason=None):
        """Mark this session as failed with an optional reason"""
        self.submission_failed = True
        self.failure_reason = reason
        db.session.commit()
    
    @classmethod
    def get_active_session(cls, user_id, product_id):
        """Get the active session for a user and product"""
        return cls.query.filter_by(
            user_id=user_id,
            product_id=product_id,
            completed=False,
            submitted=False
        ).order_by(cls.started_at.desc()).first()
    
    @classmethod
    def has_unfinished_session(cls, user_id, product_id):
        """Check if a user has an unfinished session for a product"""
        return cls.query.filter_by(
            user_id=user_id,
            product_id=product_id,
            completed=False
        ).count() > 0
    
    @classmethod
    def create_session(cls, user_id, product_id, assessment_id=None):
        """Create a new session for a user and product"""
        session = cls(
            user_id=user_id,
            product_id=product_id,
            assessment_id=assessment_id
        )
        db.session.add(session)
        db.session.commit()
        return session


# CompleteTestProgress model has been removed
# Assessment results are now stored directly in the User model's assessment_history

class PaymentRecord(db.Model):
    """Tracks payment details and transaction records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    package_name = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    stripe_session_id = db.Column(db.String(100), nullable=True)
    is_successful = db.Column(db.Boolean, default=True)
    transaction_details = db.Column(db.Text, nullable=True)
    
    # Customer address information
    address_line1 = db.Column(db.String(255), nullable=True)
    address_line2 = db.Column(db.String(255), nullable=True)
    address_city = db.Column(db.String(100), nullable=True)
    address_state = db.Column(db.String(100), nullable=True)
    address_postal_code = db.Column(db.String(20), nullable=True)
    address_country = db.Column(db.String(2), nullable=True)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('payment_records', lazy=True))
    
    def __repr__(self):
        return f'<PaymentRecord {self.id} User:{self.user_id} Amount:{self.amount}>'

# UserTestAttempt model has been removed
# Assessment results are now stored in the User model's assessment_history

class SpeakingPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part = db.Column(db.Integer, nullable=False)  # IELTS Speaking Part 1, 2, or 3
    prompt_text = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<SpeakingPrompt Part:{self.part}>'

# SpeakingResponse model has been replaced by AssessmentSpeakingResponse
# Keeping as a commented reference for backward compatibility
"""
class SpeakingResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey('speaking_prompt.id'), nullable=False)
    audio_url = db.Column(db.String(256), nullable=True)
    transcription = db.Column(db.Text, nullable=True)
    _scores = db.Column(db.Text, nullable=True)  # JSON string with fluency, coherence, etc.
    feedback_audio_url = db.Column(db.String(256), nullable=True)
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def scores(self):
        return json.loads(self._scores) if self._scores else None
    
    @scores.setter
    def scores(self, value):
        self._scores = json.dumps(value) if value else None
    
    def __repr__(self):
        return f'<SpeakingResponse User:{self.user_id} Prompt:{self.prompt_id}>'
"""

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=True)  # Null means global
    api_endpoint = db.Column(db.String(256), nullable=True)
    display_order = db.Column(db.Integer, default=2)  # 1 for regional, 2 for global
    
    def __repr__(self):
        return f'<PaymentMethod {self.name} Region:{self.region or "Global"}>'

class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False)
    element = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Translation {self.language}:{self.page}.{self.element}>'


# CountryPricing model removed - we no longer use country-specific pricing tiers
