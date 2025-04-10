"""
Database models for the AI Learning Hub application
"""
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ai_learning_hub.app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database"""
    return AIHubUser.query.get(int(user_id))

class AIHubUser(UserMixin, db.Model):
    """User model for AI Learning Hub"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    subscription_status = db.Column(db.String(20), default="none")
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    preferred_language = db.Column(db.String(10), default="en")
    _preferences = db.Column(db.Text, default='{}')  # JSON string of user preferences
    
    # Relationships
    courses = db.relationship('UserCourse', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the password is correct"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def preferences(self):
        """Get user preferences"""
        return json.loads(self._preferences)
    
    @preferences.setter
    def preferences(self, value):
        """Set user preferences"""
        self._preferences = json.dumps(value)
    
    def is_subscribed(self):
        """Check if the user has an active subscription"""
        if not self.subscription_expiry:
            return False
        return self.subscription_status == "active" and self.subscription_expiry > datetime.utcnow()
    
    def __repr__(self):
        return f'<AIHubUser {self.username}>'

class Course(db.Model):
    """Course model for AI Learning Hub"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('aihub_user.id'))
    is_published = db.Column(db.Boolean, default=False)
    difficulty_level = db.Column(db.String(20), default="beginner")
    duration_minutes = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.String(256), nullable=True)  # Comma-separated tags
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy='dynamic')
    enrollments = db.relationship('UserCourse', backref='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Module(db.Model):
    """Module model for courses"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    order = db.Column(db.Integer, default=0)  # Order in the course
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy='dynamic')
    
    def __repr__(self):
        return f'<Module {self.title}>'

class Lesson(db.Model):
    """Lesson model for modules"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    order = db.Column(db.Integer, default=0)  # Order in the module
    video_url = db.Column(db.String(256), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    
    # Relationships
    completions = db.relationship('LessonCompletion', backref='lesson', lazy='dynamic')
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class UserCourse(db.Model):
    """Model for user course enrollments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('aihub_user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<UserCourse user_id={self.user_id} course_id={self.course_id}>'

class LessonCompletion(db.Model):
    """Model for tracking completed lessons"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('aihub_user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LessonCompletion user_id={self.user_id} lesson_id={self.lesson_id}>'

class UserNote(db.Model):
    """Model for user notes on lessons"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('aihub_user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserNote user_id={self.user_id} lesson_id={self.lesson_id}>'