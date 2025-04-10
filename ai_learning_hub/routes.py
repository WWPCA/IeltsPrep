import os
import json
import logging
from functools import wraps
from datetime import datetime, timedelta

from flask import render_template, url_for, flash, redirect, request, jsonify, session, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from ai_learning_hub.app import app, db
from ai_learning_hub.models import (User, Course, Module, Lesson, Resource, Quiz, 
                                 QuizQuestion, ProjectAssignment, UserCourseProgress, 
                                 UserProjectSubmission, Category, LearningPath,
                                 Subscription, PaymentTransaction)

# Helper functions
def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.subscription_status != "premium":
            flash('This feature requires a premium subscription. Please upgrade to continue.', 'warning')
            return redirect(url_for('subscription_plans'))
        return f(*args, **kwargs)
    return decorated_function

# Home route
@app.route('/')
def index():
    # Get featured courses for the homepage
    featured_courses = Course.query.filter_by(is_featured=True, is_published=True).limit(4).all()
    
    # Get popular learning paths
    learning_paths = LearningPath.query.limit(3).all()
    
    # Get categories for the filter section
    categories = Category.query.all()
    
    return render_template('index.html', 
                           title='AI Learning Hub - Master AI, Machine Learning & Data Science',
                           featured_courses=featured_courses,
                           learning_paths=learning_paths,
                           categories=categories)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html', title='Register')
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return render_template('register.html', title='Register')
        
        new_user = User(
            username=username,
            email=email,
            subscription_status="free"
        )
        new_user.set_password(password)
        
        # Set default learning preferences
        new_user.learning_preferences = {
            "difficulty_level": "beginner",
            "learning_goal": "explore",
            "interests": [],
            "time_commitment": "1-3 hours/week"
        }
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's in-progress courses
    in_progress_courses = UserCourseProgress.query.filter_by(
        user_id=current_user.id, 
        is_completed=False
    ).order_by(UserCourseProgress.last_accessed.desc()).limit(4).all()
    
    # Get recommended courses based on user preferences
    user_preferences = current_user.learning_preferences
    recommended_courses = []
    
    if 'difficulty_level' in user_preferences:
        difficulty = user_preferences['difficulty_level']
        recommended_courses = Course.query.filter_by(
            difficulty_level=difficulty, 
            is_published=True
        ).limit(4).all()
    
    # Get recent project submissions
    recent_submissions = UserProjectSubmission.query.filter_by(
        user_id=current_user.id
    ).order_by(UserProjectSubmission.submission_date.desc()).limit(3).all()
    
    return render_template('dashboard.html', 
                           title='My Dashboard',
                           in_progress_courses=in_progress_courses,
                           recommended_courses=recommended_courses,
                           recent_submissions=recent_submissions)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update user profile
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.root_path, 'static/img/profiles', filename)
                file.save(file_path)
                current_user.profile_image = f'img/profiles/{filename}'
        
        # Update learning preferences
        learning_preferences = current_user.learning_preferences
        learning_preferences.update({
            "difficulty_level": request.form.get('difficulty_level', 'beginner'),
            "learning_goal": request.form.get('learning_goal', 'explore'),
            "time_commitment": request.form.get('time_commitment', '1-3 hours/week')
        })
        
        # Handle interests as a multi-select
        interests = request.form.getlist('interests')
        learning_preferences['interests'] = interests
        
        current_user.learning_preferences = learning_preferences
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Get all categories for interests selection
    categories = Category.query.all()
    
    return render_template('profile.html', 
                           title='My Profile',
                           categories=categories)

# Course routes
@app.route('/courses')
def courses():
    # Get query parameters for filtering
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    search = request.args.get('search')
    
    # Start with the base query
    query = Course.query.filter_by(is_published=True)
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    if search:
        query = query.filter(Course.title.ilike(f'%{search}%') | 
                            Course.description.ilike(f'%{search}%'))
    
    # Get results
    courses = query.order_by(Course.title).all()
    
    # Get all categories for filter options
    categories = Category.query.all()
    
    return render_template('courses.html', 
                           title='AI & ML Courses',
                           courses=courses,
                           categories=categories,
                           selected_category=category,
                           selected_difficulty=difficulty,
                           search_query=search)

@app.route('/course/<slug>')
def course_detail(slug):
    # Get the course by slug
    course = Course.query.filter_by(slug=slug).first_or_404()
    
    # Get course modules ordered by their sequence
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
    
    # Check if user is enrolled
    is_enrolled = False
    user_progress = None
    
    if current_user.is_authenticated:
        user_progress = UserCourseProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        
        is_enrolled = user_progress is not None
    
    # Get related courses in the same category
    related_courses = Course.query.filter_by(
        category=course.category, 
        is_published=True
    ).filter(Course.id != course.id).limit(3).all()
    
    return render_template('course_detail.html', 
                           title=course.title,
                           course=course,
                           modules=modules,
                           is_enrolled=is_enrolled,
                           user_progress=user_progress,
                           related_courses=related_courses)

@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if course is premium and user has required subscription
    if course.is_premium and current_user.subscription_status != "premium":
        flash('This is a premium course. Please upgrade your subscription to enroll.', 'warning')
        return redirect(url_for('subscription_plans'))
    
    # Check if already enrolled
    existing_enrollment = UserCourseProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('course_detail', slug=course.slug))
    
    # Create new enrollment
    enrollment = UserCourseProgress(
        user_id=current_user.id,
        course_id=course_id,
        completion_percentage=0.0,
        is_completed=False,
        completed_lessons=[],
        quiz_scores={}
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    flash('Successfully enrolled in the course!', 'success')
    return redirect(url_for('learn', course_slug=course.slug))

@app.route('/learn/<course_slug>')
@login_required
def learn(course_slug):
    # Get the course
    course = Course.query.filter_by(slug=course_slug).first_or_404()
    
    # Check if user is enrolled
    user_progress = UserCourseProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first_or_404()
    
    # Update last_accessed time
    user_progress.last_accessed = datetime.utcnow()
    db.session.commit()
    
    # Get modules and their lessons
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
    
    # Determine which lesson to show
    current_lesson = None
    
    if request.args.get('lesson_id'):
        # If a specific lesson is requested
        lesson_id = int(request.args.get('lesson_id'))
        current_lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if this lesson belongs to the course
        lesson_module = Module.query.get(current_lesson.module_id)
        if lesson_module.course_id != course.id:
            abort(404)
    else:
        # Find the first uncompleted lesson
        completed_lessons = user_progress.completed_lessons
        
        for module in modules:
            lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
            for lesson in lessons:
                if str(lesson.id) not in completed_lessons:
                    current_lesson = lesson
                    break
            if current_lesson:
                break
        
        # If all lessons are completed or no lessons found, show the first lesson
        if not current_lesson and modules and modules[0].lessons:
            current_lesson = modules[0].lessons[0]
    
    # Get resources for the current lesson
    resources = []
    quiz = None
    
    if current_lesson:
        resources = Resource.query.filter_by(lesson_id=current_lesson.id).all()
        quiz = Quiz.query.filter_by(lesson_id=current_lesson.id).first()
    
    return render_template('learn.html', 
                           title=f'Learning: {course.title}',
                           course=course,
                           modules=modules,
                           current_lesson=current_lesson,
                           resources=resources,
                           quiz=quiz,
                           user_progress=user_progress)

@app.route('/api/complete-lesson', methods=['POST'])
@login_required
def complete_lesson():
    data = request.json
    lesson_id = data.get('lesson_id')
    course_id = data.get('course_id')
    
    if not lesson_id or not course_id:
        return jsonify({'error': 'Missing required data'}), 400
    
    # Get user progress
    user_progress = UserCourseProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first_or_404()
    
    # Update completed lessons
    completed_lessons = user_progress.completed_lessons
    if str(lesson_id) not in completed_lessons:
        completed_lessons.append(str(lesson_id))
        user_progress.completed_lessons = completed_lessons
    
    # Calculate completion percentage
    total_lessons = db.session.query(Lesson).join(Module).filter(Module.course_id == course_id).count()
    completion_percentage = (len(completed_lessons) / total_lessons) * 100 if total_lessons > 0 else 0
    user_progress.completion_percentage = completion_percentage
    
    # Check if course is completed
    if completion_percentage >= 100:
        user_progress.is_completed = True
        user_progress.completion_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'completion_percentage': completion_percentage,
        'is_completed': user_progress.is_completed
    })

@app.route('/api/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    data = request.json
    quiz_id = data.get('quiz_id')
    course_id = data.get('course_id')
    lesson_id = data.get('lesson_id')
    answers = data.get('answers', {})
    
    if not quiz_id or not course_id or not lesson_id:
        return jsonify({'error': 'Missing required data'}), 400
    
    # Get quiz questions and correct answers
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    
    # Calculate score
    score = 0
    total_points = sum(question.points for question in questions)
    
    for question in questions:
        if str(question.id) in answers and answers[str(question.id)] == question.correct_answer:
            score += question.points
    
    score_percentage = (score / total_points) * 100 if total_points > 0 else 0
    
    # Update user progress
    user_progress = UserCourseProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first_or_404()
    
    # Update quiz scores
    quiz_scores = user_progress.quiz_scores
    quiz_scores[str(quiz_id)] = {
        'score': score,
        'total': total_points,
        'percentage': score_percentage,
        'date': datetime.utcnow().isoformat()
    }
    user_progress.quiz_scores = quiz_scores
    
    # Auto-complete the lesson if score is passing (>= 70%)
    if score_percentage >= 70:
        completed_lessons = user_progress.completed_lessons
        if str(lesson_id) not in completed_lessons:
            completed_lessons.append(str(lesson_id))
            user_progress.completed_lessons = completed_lessons
        
        # Recalculate completion percentage
        total_lessons = db.session.query(Lesson).join(Module).filter(Module.course_id == course_id).count()
        completion_percentage = (len(completed_lessons) / total_lessons) * 100 if total_lessons > 0 else 0
        user_progress.completion_percentage = completion_percentage
        
        # Check if course is completed
        if completion_percentage >= 100:
            user_progress.is_completed = True
            user_progress.completion_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': score,
        'total': total_points,
        'percentage': score_percentage,
        'passed': score_percentage >= 70
    })

# Learning Paths
@app.route('/learning-paths')
def learning_paths():
    # Get all learning paths
    paths = LearningPath.query.all()
    
    # Get all categories for filter options
    categories = Category.query.all()
    
    return render_template('learning_paths.html', 
                           title='AI Learning Paths',
                           learning_paths=paths,
                           categories=categories)

@app.route('/learning-path/<slug>')
def learning_path_detail(slug):
    # Get the learning path
    path = LearningPath.query.filter_by(slug=slug).first_or_404()
    
    # Get the courses in this path
    course_ids = path.course_sequence
    courses = []
    
    for course_id in course_ids:
        course = Course.query.get(course_id)
        if course and course.is_published:
            courses.append(course)
    
    # Get user progress if authenticated
    user_progress = {}
    if current_user.is_authenticated:
        for course in courses:
            progress = UserCourseProgress.query.filter_by(
                user_id=current_user.id,
                course_id=course.id
            ).first()
            
            if progress:
                user_progress[course.id] = progress
    
    return render_template('learning_path_detail.html', 
                           title=path.title,
                           path=path,
                           courses=courses,
                           user_progress=user_progress)

# Projects
@app.route('/projects')
def projects():
    # Get all projects
    projects = ProjectAssignment.query.all()
    
    # Get all categories for filter options
    categories = Category.query.all()
    
    return render_template('projects.html', 
                           title='AI Projects',
                           projects=projects,
                           categories=categories)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    # Get the project
    project = ProjectAssignment.query.get_or_404(project_id)
    
    # Check if premium project and user is not premium
    if project.is_premium and (not current_user.is_authenticated or current_user.subscription_status != "premium"):
        flash('This is a premium project. Please upgrade your subscription to access.', 'warning')
        return redirect(url_for('subscription_plans'))
    
    # Get user submission if exists
    submission = None
    if current_user.is_authenticated:
        submission = UserProjectSubmission.query.filter_by(
            user_id=current_user.id,
            project_id=project_id
        ).first()
    
    return render_template('project_detail.html', 
                           title=project.title,
                           project=project,
                           submission=submission)

@app.route('/submit-project/<int:project_id>', methods=['POST'])
@login_required
def submit_project(project_id):
    project = ProjectAssignment.query.get_or_404(project_id)
    
    # Check if premium project and user is not premium
    if project.is_premium and current_user.subscription_status != "premium":
        flash('This is a premium project. Please upgrade your subscription to access.', 'warning')
        return redirect(url_for('subscription_plans'))
    
    # Get form data
    submission_code = request.form.get('submission_code')
    submission_notes = request.form.get('submission_notes')
    
    if not submission_code:
        flash('Please provide your code submission.', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    # Check if user already has a submission
    existing_submission = UserProjectSubmission.query.filter_by(
        user_id=current_user.id,
        project_id=project_id
    ).first()
    
    if existing_submission:
        # Update existing submission
        existing_submission.submission_code = submission_code
        existing_submission.submission_notes = submission_notes
        existing_submission.submission_date = datetime.utcnow()
        existing_submission.feedback = None
        existing_submission.score = None
    else:
        # Create new submission
        submission = UserProjectSubmission(
            user_id=current_user.id,
            project_id=project_id,
            submission_code=submission_code,
            submission_notes=submission_notes
        )
        db.session.add(submission)
    
    db.session.commit()
    flash('Project submitted successfully! You will receive feedback shortly.', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

# Subscription
@app.route('/subscription-plans')
def subscription_plans():
    # Get all subscription plans
    plans = Subscription.query.all()
    
    return render_template('subscription_plans.html', 
                           title='Subscription Plans',
                           plans=plans)

@app.route('/upgrade/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def upgrade_subscription(plan_id):
    plan = Subscription.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Handle payment (simplified for now)
        period = request.form.get('period', 'monthly')
        
        # Create a "successful" payment transaction
        amount = plan.price_monthly if period == 'monthly' else plan.price_yearly
        
        transaction = PaymentTransaction(
            user_id=current_user.id,
            subscription_id=plan.id,
            amount=amount,
            currency="USD",
            payment_provider="stripe",
            payment_status="success",
            subscription_period=period
        )
        
        # Update user subscription
        days = 30 if period == 'monthly' else 365
        current_user.subscription_status = "premium"
        current_user.subscription_expiry = datetime.utcnow() + timedelta(days=days)
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Thank you for upgrading to {plan.name}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upgrade.html', 
                           title='Upgrade Subscription',
                           plan=plan)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='Page Not Found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', title='Server Error'), 500