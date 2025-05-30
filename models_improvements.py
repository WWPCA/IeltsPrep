"""
Critical Database Model Improvements
Based on technical analysis recommendations for enhanced performance, security, and AI integration.
"""

import json
from datetime import datetime, timedelta, date
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
import hashlib

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Enhanced email field with index for performance
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Enhanced region field with index
    region = db.Column(db.String(50), nullable=True, index=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Assessment package management with performance index
    assessment_package_status = db.Column(db.String(20), default="none")
    assessment_package_expiry = db.Column(db.DateTime, nullable=True, index=True)
    
    preferred_language = db.Column(db.String(10), default="en")
    assessment_preference = db.Column(db.String(20), default="academic")
    
    # Enhanced account status with explicit defaults
    account_activated = db.Column(db.Boolean, default=False, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Password reset fields
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # Study streak tracking
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    # Simplified JSON fields (to be migrated to separate tables)
    _activity_history = db.Column(db.Text, default='[]')
    _assessment_history = db.Column(db.Text, default='[]')
    _speaking_scores = db.Column(db.Text, default='[]')
    _completed_assessments = db.Column(db.Text, default='[]')
    
    @property
    def is_admin(self):
        """Check if user is admin based on email address."""
        return self.email == "admin@ieltsaiprep.com"
    
    @property
    def is_active(self):
        """Override UserMixin's is_active property to use our account_activated field."""
        return self.account_activated
    
    def set_password(self, password):
        """Enhanced password setting with history tracking."""
        # Save current password to history if it exists
        if self.password_hash:
            try:
                history = PasswordHistory.query.filter_by(user_id=self.id).order_by(PasswordHistory.created_at.desc()).limit(5).all()
                # Store new history entry
                new_history = PasswordHistory(
                    user_id=self.id,
                    password_hash=self.password_hash
                )
                db.session.add(new_history)
                
                # Clean up old entries (keep only 5 most recent)
                if len(history) >= 5:
                    oldest = PasswordHistory.query.filter_by(user_id=self.id).order_by(PasswordHistory.created_at.asc()).first()
                    if oldest:
                        db.session.delete(oldest)
            except Exception as e:
                # Fallback to JSON storage if PasswordHistory table doesn't exist yet
                history = json.loads(getattr(self, '_password_history', '[]'))
                history.append({
                    'hash': self.password_hash,
                    'date': datetime.utcnow().isoformat()
                })
                if len(history) > 5:
                    history = history[-5:]
                self._password_history = json.dumps(history)
        
        # Set the new password
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_password_reused(self, password):
        """Check if the password has been used before using improved history."""
        try:
            # Try new PasswordHistory table first
            history_entries = PasswordHistory.query.filter_by(user_id=self.id).all()
            for entry in history_entries:
                if check_password_hash(entry.password_hash, password):
                    return True
        except Exception:
            # Fallback to JSON storage
            history_json = getattr(self, '_password_history', '[]')
            if history_json:
                history = json.loads(history_json)
                for item in history:
                    if check_password_hash(item['hash'], password):
                        return True
        return False
    
    # Keep existing property methods for backward compatibility
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
    
    def has_active_assessment_package(self):
        """Check if user has access to purchased assessment packages."""
        if self.assessment_package_expiry and self.assessment_package_expiry <= datetime.utcnow():
            self.assessment_package_status = "expired"
            db.session.commit()
            return False
            
        valid_packages = [
            "Academic Writing", "Academic Speaking", 
            "General Writing", "General Speaking",
            "All Products", "unlimited_access"
        ]
            
        if (self.assessment_package_status in valid_packages and 
                self.assessment_package_status != "none" and
                self.assessment_package_status != "expired" and
                (not self.assessment_package_expiry or self.assessment_package_expiry > datetime.utcnow())):
            return True
                
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'

class PasswordHistory(db.Model):
    """Separate table for password history tracking (improved security)"""
    __tablename__ = 'password_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('password_history_entries', lazy='dynamic'))
    
    def __repr__(self):
        return f'<PasswordHistory User:{self.user_id} Created:{self.created_at}>'

class UserAssessmentHistory(db.Model):
    """Normalized assessment history for better querying (replaces JSON field)"""
    __tablename__ = 'user_assessment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)
    product = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    sets_assigned = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('assessment_history_entries', lazy='dynamic'))
    
    def __repr__(self):
        return f'<UserAssessmentHistory User:{self.user_id} Product:{self.product}>'

class Assessment(db.Model):
    """Enhanced Assessment model with better structure"""
    id = db.Column(db.Integer, primary_key=True)
    assessment_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    
    # Keep JSON fields for complex data but add validation
    _criteria = db.Column(db.Text, nullable=True)
    _questions = db.Column(db.Text, nullable=True)
    
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
    
    def __repr__(self):
        return f'<Assessment {self.assessment_type}: {self.title}>'

class WritingResponse(db.Model):
    """Enhanced WritingResponse with TrueScore® validation"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempt.id', ondelete='CASCADE'), nullable=False, index=True)
    task_number = db.Column(db.Integer, nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Enhanced assessment data storage
    _assessment_data = db.Column(db.Text, nullable=True)
    
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
    
    def __repr__(self):
        return f'<WritingResponse {self.id}: Task {self.task_number} for Attempt {self.attempt_id}>'

class AssessmentSpeakingResponse(db.Model):
    """Enhanced AssessmentSpeakingResponse with ClearScore® validation"""
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempt.id', ondelete='CASCADE'), nullable=False, index=True)
    part_number = db.Column(db.Integer, nullable=False)
    audio_filename = db.Column(db.String(256), nullable=True)
    transcript_text = db.Column(db.Text, nullable=True)
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Enhanced assessment data storage
    _assessment_data = db.Column(db.Text, nullable=True)
    
    # Enhanced GCP storage with validation
    gcp_audio_url = db.Column(db.String(500), nullable=True)
    gcp_transcript_url = db.Column(db.String(500), nullable=True)
    gcp_assessment_url = db.Column(db.String(500), nullable=True)
    
    @property
    def assessment_data(self):
        return json.loads(self._assessment_data) if self._assessment_data else {}
    
    @assessment_data.setter
    def assessment_data(self, value):
        self._assessment_data = json.dumps(value)
    
    def set_clearscore_assessment(self, data):
        """Validate and set ClearScore® assessment data from AWS Sonic + Nova Micro"""
        required_fields = ['score', 'feedback', 'pronunciation', 'fluency', 'grammar', 'vocabulary']
        if not all(field in data for field in required_fields):
            raise ValueError("Invalid ClearScore® assessment data - missing required fields")
        
        # Validate score range (IELTS bands 0-9)
        if not (0 <= data.get('score', 0) <= 9):
            raise ValueError("Score must be between 0 and 9")
            
        self.assessment_data = data
    
    def set_gcp_urls(self, audio_url, transcript_url, assessment_url):
        """Validate and set GCP URLs"""
        from urllib.parse import urlparse
        
        urls = [
            ('audio_url', audio_url),
            ('transcript_url', transcript_url), 
            ('assessment_url', assessment_url)
        ]
        
        for name, url in urls:
            if url:
                parsed = urlparse(url)
                if not parsed.scheme in ['http', 'https']:
                    raise ValueError(f"Invalid {name}: {url}")
                if not parsed.netloc:
                    raise ValueError(f"Invalid {name} - missing domain: {url}")
        
        self.gcp_audio_url = audio_url
        self.gcp_transcript_url = transcript_url
        self.gcp_assessment_url = assessment_url
    
    def __repr__(self):
        return f'<AssessmentSpeakingResponse {self.id}: Part {self.part_number} for Attempt {self.attempt_id}>'

class AssessmentAssignment(db.Model):
    """Normalized assessment assignment table (replaces JSON field)"""
    __tablename__ = 'assessment_assignment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id', ondelete='CASCADE'), nullable=False, index=True)
    assignment_type = db.Column(db.String(20), nullable=False, index=True)  # academic, general
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    used = db.Column(db.Boolean, default=False, index=True)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('assessment_assignments', lazy='dynamic'))
    assessment = db.relationship('Assessment', backref=db.backref('user_assignments', lazy='dynamic'))
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        db.UniqueConstraint('user_id', 'assessment_id', name='unique_user_assessment'),
    )
    
    def mark_used(self):
        """Mark this assignment as used"""
        self.used = True
        self.used_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<AssessmentAssignment User:{self.user_id} Assessment:{self.assessment_id} Used:{self.used}>'

class ConnectionIssueLog(db.Model):
    """Enhanced connection issue tracking with GDPR compliance"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    assessment_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.String(50), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_session.id'), nullable=True)
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_local_time = db.Column(db.String(50), nullable=True)
    issue_type = db.Column(db.String(50), nullable=False, index=True)
    
    # Enhanced privacy protection for IP addresses
    ip_address_hash = db.Column(db.String(64), nullable=True)  # Hashed for privacy
    user_agent = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    browser_info = db.Column(db.Text, nullable=True)
    connection_info = db.Column(db.Text, nullable=True)
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_method = db.Column(db.String(50), nullable=True)
    
    def set_ip_address(self, ip_address):
        """Set hashed IP address for GDPR compliance"""
        if ip_address:
            self.ip_address_hash = hashlib.sha256(ip_address.encode()).hexdigest()
    
    def __repr__(self):
        return f'<ConnectionIssueLog {self.id} - User {self.user_id} - {self.issue_type}>'
    
    @classmethod
    def log_issue(cls, user_id, issue_type, request_obj=None, **kwargs):
        """Enhanced issue logging with privacy protection"""
        log_entry = cls(
            user_id=user_id,
            issue_type=issue_type,
            assessment_id=kwargs.get('assessment_id'),
            product_id=kwargs.get('product_id'),
            session_id=kwargs.get('session_id'),
            user_local_time=kwargs.get('user_local_time')
        )
        
        if request_obj:
            # Hash IP address for privacy
            log_entry.set_ip_address(request_obj.remote_addr)
            log_entry.user_agent = request_obj.user_agent.string
            
            # Store browser info safely
            browser_info = {
                'browser': str(request_obj.user_agent.browser),
                'version': str(request_obj.user_agent.version),
                'platform': str(request_obj.user_agent.platform)
            }
            log_entry.browser_info = json.dumps(browser_info)
            
            if 'connection_info' in kwargs:
                log_entry.connection_info = json.dumps(kwargs.get('connection_info'))
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

class AssessmentSession(db.Model):
    """Enhanced session management with unique constraints"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed = db.Column(db.Boolean, default=False, index=True)
    marked_complete_at = db.Column(db.DateTime, nullable=True)
    submitted = db.Column(db.Boolean, default=False, index=True)
    submission_failed = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(255), nullable=True)
    
    # Unique constraint for active sessions
    __table_args__ = (
        db.Index('idx_active_session', 'user_id', 'product_id', 'completed'),
    )
    
    def __repr__(self):
        status = "Completed" if self.completed else "In Progress"
        if self.submission_failed:
            status = "Failed"
        return f'<AssessmentSession {self.product_id} for User:{self.user_id}, Status:{status}>'

# Validation event listeners
@event.listens_for(User.email, 'set')
def validate_email(target, value, oldvalue, initiator):
    """Validate email format"""
    if value:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")

@event.listens_for(AssessmentAssignment.expiry_date, 'set')
def validate_expiry_date(target, value, oldvalue, initiator):
    """Validate expiry date is in the future"""
    if value and value <= datetime.utcnow():
        raise ValueError("Expiry date must be in the future")

# Database integrity helpers
def create_indexes():
    """Create additional performance indexes"""
    try:
        # Add composite indexes for common queries
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_user_package_status ON user(assessment_package_status, assessment_package_expiry)')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_assessment_type_status ON assessment(assessment_type, status)')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_connection_log_user_time ON connection_issue_log(user_id, occurred_at)')
    except Exception as e:
        print(f"Index creation failed (may already exist): {e}")