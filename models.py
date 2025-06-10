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

    # Enhanced email field with index for performance
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    # Enhanced region field with index
    region = db.Column(db.String(50), nullable=True, index=True)    # Assessment package management with performance index
    assessment_package_status = db.Column(db.String(20), default="none")
    assessment_package_expiry = db.Column(db.DateTime, nullable=True, index=True)
    # App only available in English - preferred_language column retained for database compatibility
    # but not used in UI    # Enhanced account status with explicit defaults and nullability
    account_activated = db.Column(db.Boolean, default=False, nullable=False)  # Renamed from is_active to avoid UserMixin conflict
    # Email verification fields with enhanced defaults
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Password reset fields
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # Account deletion fields
    deletion_requested = db.Column(db.Boolean, default=False, nullable=False)
    deletion_requested_at = db.Column(db.DateTime, nullable=True)
    deletion_scheduled_for = db.Column(db.DateTime, nullable=True)
    reactivation_token = db.Column(db.String(255), nullable=True)
    
    # Account cleanup tracking
    deletion_warning_sent = db.Column(db.Boolean, default=False, nullable=False)
    deletion_warning_date = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
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
        return json.loads(self._assessment_history) if self._assessment_history else []
    
    @assessment_history.setter
    def assessment_history(self, value):
        self._assessment_history = json.dumps(value)
    
    @property
    def speaking_scores(self):
        return json.loads(self._speaking_scores) if self._speaking_scores else []
    
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
    
    def has_mobile_assessment_access(self, assessment_type):
        """
        Check if user has access to specific assessment via mobile app purchase.
        """
        from assessment_assignment_service import has_package_access
        return has_package_access(self.id, assessment_type)
    
    def has_package_access(self, package_name):
        """
        Check if user has access to a specific package type.
        
        Args:
            package_name (str): Package name like "Academic Speaking"
            
        Returns:
            bool: True if user has active access to this package
        """
        # Check legacy system first
        if hasattr(self, 'assessment_package_status') and self.assessment_package_status:
            if (self.assessment_package_status == package_name or 
                self.assessment_package_status == "All Products" or
                package_name in self.assessment_package_status):
                if not self.assessment_package_expiry or self.assessment_package_expiry > datetime.utcnow():
                    return True
        
        # Check new UserPackage table
        active_package = UserPackage.query.filter_by(
            user_id=self.id,
            package_name=package_name,
            status='active'
        ).filter(
            db.or_(
                UserPackage.expiry_date.is_(None),
                UserPackage.expiry_date > datetime.utcnow()
            )
        ).filter(
            UserPackage.quantity_remaining > 0
        ).first()
        
        return active_package is not None
    
    def get_package_quantity_remaining(self, package_name):
        """Get the number of remaining packages for a specific type."""
        package = UserPackage.query.filter_by(
            user_id=self.id,
            package_name=package_name,
            status='active'
        ).first()
        
        if package and package.is_active:
            return package.quantity_remaining
        return 0
        
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
        return f'<User {self.email}>'

# Model for assessment structure information pages
class AssessmentStructure(db.Model):
    __tablename__ = 'test_structure'  # Keep the table name for database compatibility
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    format_details = db.Column(db.Text, nullable=False)
    sample_image_url = db.Column(db.String(256), nullable=True)
    
    
class Assessment(db.Model):
    """Enhanced model for IELTS assessments with validation"""
    id = db.Column(db.Integer, primary_key=True)
    assessment_type = db.Column(db.String(50), nullable=False, index=True)  # academic_writing, academic_speaking, general_writing, general_speaking
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)  # active, inactive
    _criteria = db.Column(db.Text, nullable=True)  # JSON string with assessment criteria
    _questions = db.Column(db.Text, nullable=True)  # JSON string with assessment questions/content
    
    @property
    def criteria(self):
        return json.loads(self._criteria) if self._criteria else []
    
    @criteria.setter
    def criteria(self, value):
        if value and not isinstance(value, (list, dict)):
            raise ValueError("Criteria must be a list or dictionary")
        self._criteria = json.dumps(value)
        
    @property
    def questions(self):
        return json.loads(self._questions) if self._questions else []
    
    @questions.setter
    def questions(self, value):
        if value and not isinstance(value, (list, dict)):
            raise ValueError("Questions must be a list or dictionary")
        self._questions = json.dumps(value)
    
    
class UserAssessmentAttempt(db.Model):
    """Enhanced model for user assessment attempts with indexes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_type = db.Column(db.String(50), nullable=False, index=True)  # listening, reading, writing, speaking
    status = db.Column(db.String(20), nullable=False, default="in_progress", index=True)  # in_progress, completed, cancelled
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
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
    
    
# UserPackage model removed - mobile app store purchases only
class WritingResponse(db.Model):
    """Enhanced model for IELTS writing responses with TrueScore® validation"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempt.id', ondelete='CASCADE'), nullable=False, index=True)
    task_number = db.Column(db.Integer, nullable=False)  # 1 or 2
    response_text = db.Column(db.Text, nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Store GenAI assessment data for this specific writing task
    _assessment_data = db.Column(db.Text, nullable=True)  # JSON string with detailed GenAI assessment
    
    @property
    def assessment_data(self):
        return json.loads(self._assessment_data) if self._assessment_data else {}
    
    @assessment_data.setter
    def assessment_data(self, value):
        self._assessment_data = json.dumps(value)
    
    def set_truescore_assessment(self, data):
        """Validate and set TrueScore® assessment data from AWS Nova Micro"""
        required_fields = ['score', 'feedback', 'coherence', 'lexical_resource', 'grammar', 'task_achievement']
        if not all(field in data for field in required_fields):
            raise ValueError("Invalid TrueScore® assessment data - missing required fields")
        
        # Validate score range (IELTS bands 0-9)
        if not (0 <= data.get('score', 0) <= 9):
            raise ValueError("Score must be between 0 and 9")
            
        self.assessment_data = data
    
    
class AssessmentSpeakingResponse(db.Model):
    """Enhanced model for IELTS speaking responses with ClearScore® validation"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempt.id', ondelete='CASCADE'), nullable=False, index=True)
    part_number = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    audio_filename = db.Column(db.String(256), nullable=True)  # Local audio filename
    transcript_text = db.Column(db.Text, nullable=True)  # Transcription of audio
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Enhanced GCP storage with validation
    gcp_audio_url = db.Column(db.String(500), nullable=True)
    gcp_transcript_url = db.Column(db.String(500), nullable=True)
    gcp_assessment_url = db.Column(db.String(500), nullable=True)
    
    # Store GenAI assessment data for this specific speaking part
    _assessment_data = db.Column(db.Text, nullable=True)  # JSON string with detailed GenAI assessment
    
    @property
    def assessment_data(self):
        """Get assessment data as dictionary"""
        if self._assessment_data:
            return json.loads(self._assessment_data)
        return {}
    
    @assessment_data.setter
    def assessment_data(self, value):
        """Set assessment data from dictionary"""
        self._assessment_data = json.dumps(value) if value else None

class UserAssessmentAssignment(db.Model):
    """Enhanced assessment assignment tracking with normalized structure"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_type = db.Column(db.String(20), nullable=False, index=True)  # academic or general
    assigned_assessment_ids = db.Column(db.Text, nullable=False)  # JSON array of assigned assessment IDs
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    
    @property
    def assessment_ids(self):
        """Get the list of assigned assessment IDs"""
        return json.loads(self.assigned_assessment_ids)
    
    @assessment_ids.setter
    def assessment_ids(self, value):
        """Set the list of assigned assessment IDs"""
        if value and not isinstance(value, list):
            raise ValueError("Assessment IDs must be a list")
        self.assigned_assessment_ids = json.dumps(value)
        
    
class UserTestAttempt(db.Model):
    """Model for tracking assessment attempts with recovery capabilities"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.String(100), nullable=False)  # Unique assessment identifier
    assessment_name = db.Column(db.String(100), nullable=True)  # Human-readable name
    assessment_type = db.Column(db.String(50), nullable=False)  # speaking, writing, etc.
    status = db.Column(db.String(20), nullable=False, default="in_progress")  # in_progress, completed, cancelled, expired
    
    # Timing information
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    
    # Recovery system fields
    recovery_data = db.Column(db.Text, nullable=True)  # JSON string with recovery information
    recovery_used = db.Column(db.Boolean, default=False)  # Whether recovery was used
    resumed_at = db.Column(db.DateTime, nullable=True)  # When assessment was resumed
    restarted_at = db.Column(db.DateTime, nullable=True)  # When assessment was restarted
    
    # GCP storage references for transcripts and assessments
    gcp_transcript_path = db.Column(db.String(255), nullable=True)
    gcp_assessment_path = db.Column(db.String(255), nullable=True)
    transcript_expiry_date = db.Column(db.DateTime, nullable=True)
    
    # Results storage
    _results = db.Column(db.Text, nullable=True)  # JSON string with assessment results
    _conversation_transcript = db.Column(db.Text, nullable=True)  # JSON string with conversation history
    
    @property
    def results(self):
        """Get results as dictionary"""
        if self._results:
            return json.loads(self._results)
        return {}
    
    @results.setter
    def results(self, value):
        """Set results from dictionary"""
        self._results = json.dumps(value) if value else None

class ConnectionIssueLog(db.Model):
    """Enhanced connection issue tracking with GDPR compliance"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    assessment_id = db.Column(db.Integer, nullable=True)  # ID of the assessment being taken
    product_id = db.Column(db.String(50), nullable=True)  # academic_writing, academic_speaking, etc.
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_session.id'), nullable=True)
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_local_time = db.Column(db.String(50), nullable=True)  # Stored as string to preserve client timezone info
    issue_type = db.Column(db.String(50), nullable=False, index=True)  # disconnect, reconnect, session_restart, etc.
    
    # Enhanced privacy protection for IP addresses
    ip_address_hash = db.Column(db.String(64), nullable=True)  # Hashed for GDPR compliance
    user_agent = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    browser_info = db.Column(db.Text, nullable=True)  # JSON string with browser details
    connection_info = db.Column(db.Text, nullable=True)  # JSON string with connection details
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_method = db.Column(db.String(50), nullable=True)  # auto_restart, admin_intervention, etc.
    
    def set_ip_address(self, ip_address):
        """Set hashed IP address for GDPR compliance"""
        if ip_address:
            import hashlib
            self.ip_address_hash = hashlib.sha256(ip_address.encode()).hexdigest()
    
    
class AssessmentSession(db.Model):
    """Enhanced session management with unique constraints and indexes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)  # academic_writing, academic_speaking, etc.
    assessment_id = db.Column(db.Integer, nullable=True)  # ID of the assessment currently being taken
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed = db.Column(db.Boolean, default=False, index=True)
    marked_complete_at = db.Column(db.DateTime, nullable=True)
    submitted = db.Column(db.Boolean, default=False, index=True)
    submission_failed = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(255), nullable=True)
    
    # Composite index for active sessions
    __table_args__ = (
        db.Index('idx_active_session', 'user_id', 'product_id', 'completed'),
    )
    
    
class PaymentRecord(db.Model):
    """Tracks payment details and transaction records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    package_name = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    # stripe_session_id removed - using mobile in-app purchases only
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
    
    
class SpeakingPrompt(db.Model):
    """Enhanced speaking prompts for ClearScore® assessments with indexing"""
    id = db.Column(db.Integer, primary_key=True)
    part = db.Column(db.Integer, nullable=False, index=True)  # IELTS Speaking Part 1, 2, or 3
    prompt_text = db.Column(db.Text, nullable=False, unique=True)  # Ensure unique prompts
    difficulty_level = db.Column(db.String(20), default="standard")  # beginner, standard, advanced
    topic_category = db.Column(db.String(50), nullable=True, index=True)  # family, work, education, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True, index=True)
    
    
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
    
    
class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=True)  # Null means global
    api_endpoint = db.Column(db.String(256), nullable=True)
    display_order = db.Column(db.Integer, default=2)  # 1 for regional, 2 for global
    
    
class ConsentRecord(db.Model):
    """GDPR-compliant consent tracking with versioning and audit trails"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    consent_type = db.Column(db.String(50), nullable=False, index=True)
    consent_given = db.Column(db.Boolean, nullable=False)
    version = db.Column(db.String(10), nullable=False, default='1.0')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address_hash = db.Column(db.String(64), nullable=True)  # Privacy-compliant hashed IP
    user_agent_hash = db.Column(db.String(64), nullable=True)  # Privacy-compliant hashed user agent
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('consent_records', lazy=True))
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_user_consent_type', 'user_id', 'consent_type'),
    )
    
    
class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False)
    element = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    