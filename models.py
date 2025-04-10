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
    region = db.Column(db.String(50), nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_status = db.Column(db.String(20), default="none")
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    preferred_language = db.Column(db.String(10), default="en")
    
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
        # Check if user has an active subscription
        if self.subscription_status == "active" and self.subscription_expiry:
            # Check if subscription has expired
            if self.subscription_expiry < datetime.utcnow():
                self.subscription_status = "expired"
                db.session.commit()
                return False
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

class PracticeTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(20), nullable=False)  # listening, reading, writing
    section = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    _questions = db.Column(db.Text, nullable=False)  # JSON string
    _answers = db.Column(db.Text, nullable=False)  # JSON string
    audio_url = db.Column(db.String(256), nullable=True)  # For listening tests
    
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
        
    def __repr__(self):
        return f'<PracticeTest {self.test_type} {self.section}: {self.title}>'

class UserTestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('practice_test.id'), nullable=False)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    _user_answers = db.Column(db.Text, nullable=False)  # JSON string
    score = db.Column(db.Float, nullable=True)
    
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
