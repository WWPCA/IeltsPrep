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
    test_preference = db.Column(db.String(20), default="academic")  # Options: academic, general
    # Account activation flag - only true after successful payment
    account_activated = db.Column(db.Boolean, default=False)  # Renamed from is_active to avoid UserMixin conflict
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    # target_score field removed as it doesn't exist in database
    # is_admin field removed as it doesn't exist in database
    
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
    # Store completed tests as JSON string
    _completed_tests = db.Column(db.Text, default='[]')
    
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
    def completed_tests(self):
        return json.loads(self._completed_tests)
    
    @completed_tests.setter
    def completed_tests(self, value):
        self._completed_tests = json.dumps(value)
    
    def has_taken_test(self, test_id, test_type=None):
        """Check if user has already taken a specific test"""
        for test in self.completed_tests:
            if test['test_id'] == test_id:
                if test_type is None or test['test_type'] == test_type:
                    # Check if taken during current assessment package period
                    if self.assessment_package_expiry:
                        test_date = datetime.fromisoformat(test['date'])
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
                                    # Value pack (4 tests) = 30 days, others = 15 days
                                    package_days = 30 if "pro" in package_data["plan"] else 15
                                    break
                        
                        # If test was taken before current assessment package started, allow retaking
                        package_start = self.assessment_package_expiry - timedelta(days=package_days)
                        if test_date < package_start:
                            return False
                    return True
        return False
        
    def mark_test_completed(self, test_id, test_type):
        """Mark a test as completed by this user"""
        completed = self.completed_tests
        completed.append({
            'test_id': test_id,
            'test_type': test_type,
            'date': datetime.utcnow().isoformat()
        })
        self.completed_tests = completed
    
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

class TestStructure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    format_details = db.Column(db.Text, nullable=False)
    sample_image_url = db.Column(db.String(256), nullable=True)
    
    def __repr__(self):
        return f'<TestStructure {self.test_type}>'

class CompletePracticeTest(db.Model):
    """Model for a complete IELTS practice test with all sections"""
    id = db.Column(db.Integer, primary_key=True)
    ielts_test_type = db.Column(db.String(20), nullable=False, default="academic")  # academic, general
    test_number = db.Column(db.Integer, nullable=True)  # Test 1, Test 2, etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_free = db.Column(db.Boolean, default=False)  # Free sample test
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    product_type = db.Column(db.String(50), nullable=True)  # academic_writing, academic_speaking, general_writing, general_speaking
    status = db.Column(db.String(20), nullable=False, default="active")  # active, inactive
    _tests = db.Column(db.Text, nullable=True)  # JSON string with test IDs or prompt IDs
    
    @property
    def tests(self):
        return json.loads(self._tests) if self._tests else []
    
    @tests.setter
    def tests(self, value):
        self._tests = json.dumps(value)
    
    def __repr__(self):
        if self.test_number:
            return f'<CompletePracticeTest {self.ielts_test_type} Test {self.test_number}: {self.title}>'
        else:
            return f'<CompletePracticeTest {self.title}>'

class PracticeTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complete_test_id = db.Column(db.Integer, db.ForeignKey('complete_practice_test.id'), nullable=True)  # Link to complete test
    test_type = db.Column(db.String(20), nullable=False)  # listening, reading, writing, speaking
    ielts_test_type = db.Column(db.String(20), nullable=False, default="academic")  # academic, general
    section = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    _content = db.Column(db.Text, nullable=True)  # Text content or passage
    _questions = db.Column(db.Text, nullable=False)  # JSON string
    _answers = db.Column(db.Text, nullable=False)  # JSON string
    _features = db.Column(db.Text, nullable=True)  # JSON string for matching features
    audio_url = db.Column(db.String(256), nullable=True)  # For listening tests
    is_free = db.Column(db.Boolean, default=False)  # Free sample test
    time_limit = db.Column(db.Integer, nullable=True)  # Time limit in minutes
    
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, value):
        self._content = value
    
    @property
    def questions(self):
        return json.loads(self._questions)
    
    @questions.setter
    def questions(self, value):
        self._questions = json.dumps(value)
    
    @property
    def answers(self):
        return json.loads(self._answers)
    
    @answers.setter
    def answers(self, value):
        self._answers = json.dumps(value)
    
    @property
    def features(self):
        return json.loads(self._features) if self._features else []
    
    @features.setter
    def features(self, value):
        self._features = json.dumps(value)
        
    def __repr__(self):
        return f'<PracticeTest {self.test_type} {self.section}: {self.title}>'

class UserTestAssignment(db.Model):
    """Track which tests are assigned to each user to ensure no repeats"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_type = db.Column(db.String(20), nullable=False)  # academic or general
    assigned_test_numbers = db.Column(db.Text, nullable=False)  # JSON array of assigned test numbers
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    
    @property
    def test_numbers(self):
        """Get the list of assigned test numbers"""
        return json.loads(self.assigned_test_numbers)
    
    @test_numbers.setter
    def test_numbers(self, value):
        """Set the list of assigned test numbers"""
        self.assigned_test_numbers = json.dumps(value)
        
    def __repr__(self):
        return f'<UserTestAssignment User:{self.user_id} Type:{self.test_type} Tests:{self.assigned_test_numbers}>'

class ConnectionIssueLog(db.Model):
    """Track connection issues for monitoring and support purposes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, nullable=True)  # ID of the test being taken
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
            test_id=kwargs.get('test_id'),
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
    test_id = db.Column(db.Integer, nullable=True)  # ID of the test currently being taken
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
    def create_session(cls, user_id, product_id, test_id=None):
        """Create a new session for a user and product"""
        session = cls(
            user_id=user_id,
            product_id=product_id,
            test_id=test_id
        )
        db.session.add(session)
        db.session.commit()
        return session


class CompleteTestProgress(db.Model):
    """Track user progress through a complete test with multiple sections"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complete_test_id = db.Column(db.Integer, db.ForeignKey('complete_practice_test.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime, nullable=True)
    _section_progress = db.Column(db.Text, default='{}')  # JSON tracking completed sections
    current_section = db.Column(db.String(20), nullable=True)  # Current section (listening, reading, etc.)
    
    @property
    def section_progress(self):
        return json.loads(self._section_progress)
    
    @section_progress.setter
    def section_progress(self, value):
        self._section_progress = json.dumps(value)
        
    def is_section_completed(self, section_type):
        """Check if a specific section has been completed"""
        progress = self.section_progress
        return section_type in progress and progress[section_type].get('completed', False)
        
    def mark_section_completed(self, section_type, score):
        """Mark a section as completed with its score"""
        progress = self.section_progress
        progress[section_type] = {
            'completed': True,
            'score': score,
            'date': datetime.utcnow().isoformat()
        }
        self.section_progress = progress
        
    def is_test_completed(self):
        """Check if all test sections are completed"""
        # Define required sections for different test types
        test = CompletePracticeTest.query.get(self.complete_test_id)
        if not test:
            return False
            
        required_sections = ['listening', 'reading', 'writing', 'speaking']
            
        progress = self.section_progress
        for section in required_sections:
            if section not in progress or not progress[section].get('completed', False):
                return False
                
        # If we got here, all required sections are complete
        if not self.completed_date:
            self.completed_date = datetime.utcnow()
            
        return True
        
    def get_overall_score(self):
        """Calculate overall band score across all completed sections"""
        if not self.section_progress:
            return 0
            
        progress = self.section_progress
        total_score = 0
        count = 0
        
        for section, data in progress.items():
            if data.get('completed', False) and 'score' in data:
                total_score += float(data['score'])
                count += 1
                
        return round(total_score / max(1, count), 1)  # Avoid division by zero
    
    def get_next_section(self):
        """Get the next incomplete section for this test"""
        # Standard section order in IELTS
        section_order = ['listening', 'reading', 'writing', 'speaking']
            
        progress = self.section_progress
        
        for section in section_order:
            if section not in progress or not progress[section].get('completed', False):
                return section
                
        return None  # All sections completed
        
    def __repr__(self):
        return f'<CompleteTestProgress User:{self.user_id} Test:{self.complete_test_id}>'

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

class UserTestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('practice_test.id'), nullable=False)
    complete_test_progress_id = db.Column(db.Integer, db.ForeignKey('complete_test_progress.id'), nullable=True)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    _user_answers = db.Column(db.Text, nullable=False)  # JSON string
    score = db.Column(db.Float, nullable=True)
    assessment = db.Column(db.Text, nullable=True)  # JSON string with full assessment details
    
    # GCP Storage references
    gcp_transcript_path = db.Column(db.String(255), nullable=True)  # Path to transcript in GCP
    gcp_assessment_path = db.Column(db.String(255), nullable=True)  # Path to assessment in GCP
    transcript_expiry_date = db.Column(db.DateTime, nullable=True)  # When transcript expires (6 months)
    
    @property
    def user_answers(self):
        return json.loads(self._user_answers)
    
    @user_answers.setter
    def user_answers(self, value):
        self._user_answers = json.dumps(value)
    
    def is_transcript_expired(self):
        """Check if the transcript has expired (6-month retention policy)"""
        if not self.transcript_expiry_date:
            return False
        return datetime.utcnow() > self.transcript_expiry_date
    
    def __repr__(self):
        return f'<UserTestAttempt User:{self.user_id} Test:{self.test_id}>'

class SpeakingPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part = db.Column(db.Integer, nullable=False)  # IELTS Speaking Part 1, 2, or 3
    prompt_text = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<SpeakingPrompt Part:{self.part}>'

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
