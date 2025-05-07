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
    phone = db.Column(db.String(30), nullable=True)  # Optional phone number
    region = db.Column(db.String(50), nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_status = db.Column(db.String(20), default="none")
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    # App only available in English - preferred_language column retained for database compatibility
    # but not used in UI
    preferred_language = db.Column(db.String(10), default="en")
    test_preference = db.Column(db.String(20), default="academic")  # Options: academic, general
    target_score = db.Column(db.String(10), default="7.0")  # Target IELTS band score
    
    # Study streak tracking
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    # Store study activity history as JSON string
    _activity_history = db.Column(db.Text, default='[]')
    
    # Store test history as JSON string
    _test_history = db.Column(db.Text, default='[]')
    # Store speaking scores as JSON string
    _speaking_scores = db.Column(db.Text, default='[]')
    # Store completed tests as JSON string
    _completed_tests = db.Column(db.Text, default='[]')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def test_history(self):
        return json.loads(self._test_history)
    
    @test_history.setter
    def test_history(self, value):
        self._test_history = json.dumps(value)
    
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
                    # Check if taken during current subscription period
                    if self.subscription_expiry:
                        test_date = datetime.fromisoformat(test['date'])
                        # Get subscription duration from test_history
                        subscription_days = 30  # Default to 30 days
                        
                        for history_item in self.test_history:
                            if "test_purchase" in history_item:
                                purchase_data = history_item["test_purchase"]
                                if "expiry_date" in purchase_data:
                                    # Calculate days between purchase and expiry
                                    purchase_date = datetime.fromisoformat(purchase_data["purchase_date"])
                                    expiry_date = datetime.fromisoformat(purchase_data["expiry_date"])
                                    subscription_days = (expiry_date - purchase_date).days
                                    break
                            elif "subscription_data" in history_item:
                                sub_data = history_item["subscription_data"]
                                if "plan" in sub_data:
                                    # Value pack (4 tests) = 30 days, others = 15 days
                                    subscription_days = 30 if "pro" in sub_data["plan"] else 15
                                    break
                        
                        # If test was taken before current subscription started, allow retaking
                        subscription_start = self.subscription_expiry - timedelta(days=subscription_days)
                        if test_date < subscription_start:
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
    
    def is_subscribed(self):
        """Check if user has an active subscription"""
        # Check if subscription has expired first
        if self.subscription_expiry and self.subscription_expiry <= datetime.utcnow():
            # Subscription has expired - update status
            self.subscription_status = "expired"
            db.session.commit()
            return False
            
        # Check for test purchases in test_history
        for history_item in self.test_history:
            if "test_purchase" in history_item:
                purchase_data = history_item["test_purchase"]
                if "expiry_date" in purchase_data:
                    # Check if purchase is still valid
                    expiry_date = datetime.fromisoformat(purchase_data["expiry_date"])
                    if expiry_date > datetime.utcnow():
                        return True
            
        # Check for the new subscription status values
        valid_subscriptions = [
            "Value Pack", "Single Test", "Double Package",  # New naming convention
            "Speaking Only Basic", "Speaking Only Pro",     # Speaking-only packages
            "premium", "base", "intermediate", "pro"        # Legacy naming convention
        ]
            
        # Verify that subscription status is not "none" or "expired" and hasn't expired
        if (self.subscription_status in valid_subscriptions and 
                self.subscription_status != "none" and
                self.subscription_status != "expired" and
                (not self.subscription_expiry or self.subscription_expiry > datetime.utcnow())):
            return True
                
        return False
        
    def is_speaking_only_user(self):
        """Check if user has speaking-only access"""
        # Speaking-only users have permanent account access (no expiry)
        # Check for speaking-only subscription status
        speaking_only_subscriptions = ["Speaking Only Basic", "Speaking Only Pro"]
        
        # Check if current subscription is a speaking-only type
        if self.subscription_status in speaking_only_subscriptions:
            return True
                
        # Check for speaking-only test purchases in test_history
        for history_item in self.test_history:
            if "speaking_purchase" in history_item:
                # If there's a speaking purchase in history, user has speaking-only access
                # (speaking packages have permanent access)
                return True
                        
        return False
        
    def get_remaining_speaking_assessments(self):
        """Get the number of speaking assessments remaining for speaking-only users"""
        # Default to 0 if not a speaking-only user
        if not self.is_speaking_only_user():
            return 0
            
        # Check for speaking assessments count in test_history
        for history_item in reversed(self.test_history):  # Check most recent first
            if "speaking_purchase" in history_item:
                purchase_data = history_item["speaking_purchase"]
                if "total_assessments" in purchase_data and "used_assessments" in purchase_data:
                    remaining = purchase_data["total_assessments"] - purchase_data["used_assessments"]
                    return max(0, remaining)  # Ensure never negative
        
        # If subscription is Speaking Only but no purchase data found
        if self.subscription_status == "Speaking Only Basic":
            return 4  # Default for basic speaking package
        elif self.subscription_status == "Speaking Only Pro":
            return 10  # Default for pro speaking package
            
        return 0
    
    def use_speaking_assessment(self):
        """Mark that a speaking assessment has been used"""
        if not self.is_speaking_only_user():
            return False
            
        # Find the most recent speaking purchase and increment used count
        history = self.test_history
        for i in range(len(history) - 1, -1, -1):  # Reverse traversal
            if "speaking_purchase" in history[i]:
                purchase_data = history[i]["speaking_purchase"]
                if "total_assessments" in purchase_data and "used_assessments" in purchase_data:
                    # Only increment if assessments remain
                    if purchase_data["used_assessments"] < purchase_data["total_assessments"]:
                        purchase_data["used_assessments"] += 1
                        history[i]["speaking_purchase"] = purchase_data
                        self.test_history = history
                        return True
                    return False
                    
        # If no existing purchase data found, create a new entry based on subscription type
        if self.subscription_status == "Speaking Only Basic":
            # Create new purchase data for basic (4 assessments)
            new_purchase = {
                "speaking_purchase": {
                    "purchase_date": datetime.utcnow().isoformat(),
                    "expiry_date": None,  # No expiry
                    "total_assessments": 4,
                    "used_assessments": 1,
                    "amount": 15.0,
                    "package": "Speaking Only Basic"
                }
            }
            history.append(new_purchase)
            self.test_history = history
            return True
        elif self.subscription_status == "Speaking Only Pro":
            # Create new purchase data for pro (10 assessments)
            new_purchase = {
                "speaking_purchase": {
                    "purchase_date": datetime.utcnow().isoformat(),
                    "expiry_date": None,  # No expiry
                    "total_assessments": 10,
                    "used_assessments": 1,
                    "amount": 20.0,
                    "package": "Speaking Only Pro"
                }
            }
            history.append(new_purchase)
            self.test_history = history
            return True
            
        return False
    
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
    subscription_level = db.Column(db.String(20), nullable=False, default="basic")  # basic, intermediate, premium
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

class UserTestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('practice_test.id'), nullable=False)
    complete_test_progress_id = db.Column(db.Integer, db.ForeignKey('complete_test_progress.id'), nullable=True)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    _user_answers = db.Column(db.Text, nullable=False)  # JSON string
    score = db.Column(db.Float, nullable=True)
    assessment = db.Column(db.Text, nullable=True)  # JSON string with full assessment details
    
    @property
    def user_answers(self):
        return json.loads(self._user_answers)
    
    @user_answers.setter
    def user_answers(self, value):
        self._user_answers = json.dumps(value)
    
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


class CountryPricing(db.Model):
    """Table for storing country-specific pricing information."""
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False, unique=True)
    country_name = db.Column(db.String(100), nullable=False)
    
    # Pricing for different subscription levels (in USD)
    monthly_price = db.Column(db.Float, nullable=False)
    quarterly_price = db.Column(db.Float, nullable=False)
    yearly_price = db.Column(db.Float, nullable=False)
    
    # Default country flag (for showing as default option)
    is_default = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<CountryPricing {self.country_name} - ${self.monthly_price}/month>"
