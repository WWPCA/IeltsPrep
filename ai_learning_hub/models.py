import json
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ai_learning_hub.app import db

# We'll use the existing User model from the main application
# and create our AI Learning Hub specific models with different names

class AIHubUser(db.Model):
    """AI Learning Hub user profile model that extends the main User model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Reference to main User model
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Preferences
    skill_level = db.Column(db.String(20), default="beginner")  # beginner, intermediate, advanced
    interests = db.Column(db.String(200), nullable=True)  # comma-separated list of interests
    learning_goal = db.Column(db.String(100), nullable=True)
    
    # Subscription info
    subscription_type = db.Column(db.String(20), default="free")  # free, basic, premium
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='aihub_user', lazy=True, 
                                 foreign_keys='Enrollment.aihub_user_id')
    progress_records = db.relationship('ProgressRecord', backref='aihub_user', lazy=True,
                                      foreign_keys='ProgressRecord.aihub_user_id')
    completed_lessons = db.relationship('CompletedLesson', backref='aihub_user', lazy=True,
                                       foreign_keys='CompletedLesson.aihub_user_id')
    
    def is_subscribed(self):
        if self.subscription_type == "free":
            return False
        if not self.subscription_expiry:
            return False
        return self.subscription_expiry > datetime.utcnow()
    
    def __repr__(self):
        return f'<AIHubUser {self.id}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200), nullable=True)
    cover_image = db.Column(db.String(200), nullable=True)
    level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    price = db.Column(db.Float, default=0.0)
    is_premium = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(200), nullable=True)  # comma-separated tags
    prerequisites = db.Column(db.Text, nullable=True)
    learning_outcomes = db.Column(db.Text, nullable=True)  # JSON string list
    instructor_id = db.Column(db.Integer, db.ForeignKey('ai_hub_user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Rating and stats
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    enrollment_count = db.Column(db.Integer, default=0)
    
    # SEO fields
    meta_title = db.Column(db.String(150), nullable=True)
    meta_description = db.Column(db.String(300), nullable=True)
    seo_keywords = db.Column(db.String(200), nullable=True)
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    
    def instructor(self):
        return AIHubUser.query.get(self.instructor_id)
    
    @property
    def outcomes_list(self):
        if self.learning_outcomes:
            return json.loads(self.learning_outcomes)
        return []
    
    @outcomes_list.setter
    def outcomes_list(self, value):
        self.learning_outcomes = json.dumps(value)
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy=True)
    
    def __repr__(self):
        return f'<Module {self.title}>'


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    lesson_type = db.Column(db.String(20), default="text")  # text, video, quiz, project
    video_url = db.Column(db.String(200), nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)
    is_free = db.Column(db.Boolean, default=False)
    
    # Relationships
    quiz_questions = db.relationship('QuizQuestion', backref='lesson', lazy=True)
    completed_by = db.relationship('CompletedLesson', backref='lesson', lazy=True)
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default="multiple_choice")  # multiple_choice, true_false, code_completion
    options = db.Column(db.Text, nullable=True)  # JSON string for options
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    
    @property
    def options_list(self):
        if self.options:
            return json.loads(self.options)
        return []
    
    @options_list.setter
    def options_list(self, value):
        self.options = json.dumps(value)
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>'


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aihub_user_id = db.Column(db.Integer, db.ForeignKey('ai_hub_user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Enrollment {self.id}>'


class ProgressRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aihub_user_id = db.Column(db.Integer, db.ForeignKey('ai_hub_user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    last_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProgressRecord {self.id}>'


class CompletedLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aihub_user_id = db.Column(db.Integer, db.ForeignKey('ai_hub_user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_score = db.Column(db.Float, nullable=True)  # If lesson has a quiz
    
    def __repr__(self):
        return f'<CompletedLesson {self.id}>'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aihub_user_id = db.Column(db.Integer, db.ForeignKey('ai_hub_user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aihub_user_id = db.Column(db.Integer, db.ForeignKey('ai_hub_user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Certificate {self.certificate_id}>'