import json
from datetime import datetime
from ai_learning_hub.app import db, login_manager
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
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.String(256), nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_status = db.Column(db.String(20), default="free")
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Store learning preferences as JSON string
    _learning_preferences = db.Column(db.Text, default='{}')
    # Store progress data as JSON string
    _learning_progress = db.Column(db.Text, default='{}')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def learning_preferences(self):
        return json.loads(self._learning_preferences)
    
    @learning_preferences.setter
    def learning_preferences(self, value):
        self._learning_preferences = json.dumps(value)
    
    @property
    def learning_progress(self):
        return json.loads(self._learning_progress)
    
    @learning_progress.setter
    def learning_progress(self, value):
        self._learning_progress = json.dumps(value)
    
    def is_subscribed(self):
        # Free tier is always considered subscribed to basic content
        if self.subscription_status == "free":
            return True
            
        # Check if user has a premium subscription
        if self.subscription_status == "premium" and self.subscription_expiry:
            # Check if subscription has expired
            if self.subscription_expiry < datetime.utcnow():
                self.subscription_status = "expired"
                db.session.commit()
                return False
            return True
        
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    category = db.Column(db.String(50), nullable=False)  # ai, ml, data_science, etc.
    image_url = db.Column(db.String(256), nullable=True)
    prerequisites = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    estimated_time = db.Column(db.Integer, nullable=True)  # in minutes
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Module {self.title}>'

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    estimated_time = db.Column(db.Integer, nullable=True)  # in minutes
    is_premium = db.Column(db.Boolean, default=False)
    
    # Relationships
    resources = db.relationship('Resource', backref='lesson', lazy=True, cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', backref='lesson', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # video, pdf, code, link
    url = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    
    def __repr__(self):
        return f'<Resource {self.title}>'

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    
    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Quiz {self.title}>'

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, true_false, code_completion
    _options = db.Column(db.Text, nullable=True)  # JSON string for multiple choice options
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=1)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    
    @property
    def options(self):
        return json.loads(self._options) if self._options else None
    
    @options.setter
    def options(self, value):
        self._options = json.dumps(value) if value else None
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>'

class ProjectAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    category = db.Column(db.String(50), nullable=False)  # ai, ml, data_science, etc.
    instructions = db.Column(db.Text, nullable=False)
    starter_code = db.Column(db.Text, nullable=True)
    solution_code = db.Column(db.Text, nullable=True)
    is_premium = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ProjectAssignment {self.title}>'

class UserCourseProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    started_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completion_percentage = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    
    # Store completed lessons as JSON string
    _completed_lessons = db.Column(db.Text, default='[]')
    # Store quiz scores as JSON string
    _quiz_scores = db.Column(db.Text, default='{}')
    
    @property
    def completed_lessons(self):
        return json.loads(self._completed_lessons)
    
    @completed_lessons.setter
    def completed_lessons(self, value):
        self._completed_lessons = json.dumps(value)
    
    @property
    def quiz_scores(self):
        return json.loads(self._quiz_scores)
    
    @quiz_scores.setter
    def quiz_scores(self, value):
        self._quiz_scores = json.dumps(value)
    
    def __repr__(self):
        return f'<UserCourseProgress User:{self.user_id} Course:{self.course_id}>'

class UserProjectSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project_assignment.id'), nullable=False)
    submission_code = db.Column(db.Text, nullable=False)
    submission_notes = db.Column(db.Text, nullable=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<UserProjectSubmission User:{self.user_id} Project:{self.project_id}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon_class = db.Column(db.String(50), nullable=True)  # For Font Awesome icons
    
    def __repr__(self):
        return f'<Category {self.name}>'

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_url = db.Column(db.String(256), nullable=True)
    _course_sequence = db.Column(db.Text, nullable=False)  # JSON array of course IDs in sequence
    estimated_completion_time = db.Column(db.Integer, nullable=True)  # in hours
    
    @property
    def course_sequence(self):
        return json.loads(self._course_sequence)
    
    @course_sequence.setter
    def course_sequence(self, value):
        self._course_sequence = json.dumps(value)
    
    def __repr__(self):
        return f'<LearningPath {self.title}>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price_monthly = db.Column(db.Float, nullable=False)
    price_yearly = db.Column(db.Float, nullable=False)
    features = db.Column(db.Text, nullable=False)  # JSON string of features
    
    def __repr__(self):
        return f'<Subscription {self.name}>'

class PaymentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default="USD")
    payment_provider = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)  # success, pending, failed
    subscription_period = db.Column(db.String(10), nullable=False)  # monthly, yearly
    transaction_id = db.Column(db.String(100), nullable=True)  # External transaction ID
    
    def __repr__(self):
        return f'<PaymentTransaction User:{self.user_id} Amount:{self.currency}{self.amount}>'