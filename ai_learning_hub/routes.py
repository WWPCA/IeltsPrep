import json
from functools import wraps
from datetime import datetime, timedelta

from flask import (
    flash, jsonify, redirect, render_template, request, session, url_for
)
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user
)
from werkzeug.security import check_password_hash, generate_password_hash

from ai_learning_hub.app import app, db
from ai_learning_hub.models import (
    AIHubUser, Certificate, CompletedLesson, Course, Enrollment, Lesson, Module,
    ProgressRecord, QuizQuestion, Review
)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return AIHubUser.query.get(int(user_id))


# Custom decorators
def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_subscribed():
            flash('This content requires a premium subscription.', 'warning')
            return redirect(url_for('pricing'))
        return f(*args, **kwargs)
    return decorated_function


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Main routes
@app.route('/')
def index():
    featured_courses = Course.query.filter_by(is_premium=False).order_by(Course.rating.desc()).limit(6).all()
    categories = db.session.query(Course.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template(
        'index.html',
        featured_courses=featured_courses,
        categories=categories
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = AIHubUser.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            error = 'Invalid email or password'
    
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Form validation
        if not username or not email or not password:
            error = 'All fields are required'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long'
        elif AIHubUser.query.filter_by(username=username).first():
            error = 'Username already taken'
        elif AIHubUser.query.filter_by(email=email).first():
            error = 'Email already registered'
        else:
            # Create new user
            new_user = AIHubUser(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            login_user(new_user)
            flash('Registration successful! Welcome to AI Learning Hub.', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('register.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's enrolled courses
    enrollments = Enrollment.query.filter_by(aihub_user_id=current_user.id).all()
    enrolled_courses = []
    
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        progress = ProgressRecord.query.filter_by(
            aihub_user_id=current_user.id,
            course_id=course.id
        ).first()
        
        progress_percentage = progress.progress_percentage if progress else 0
        
        enrolled_courses.append({
            'course': course,
            'enrollment': enrollment,
            'progress': progress_percentage
        })
    
    # Get recommended courses based on user's interests and skill level
    if current_user.interests:
        interests = [i.strip() for i in current_user.interests.split(',')]
        recommended_courses = Course.query.filter(
            Course.level == current_user.skill_level,
            Course.id.notin_([e.course_id for e in enrollments])
        ).limit(4).all()
    else:
        recommended_courses = Course.query.filter(
            Course.id.notin_([e.course_id for e in enrollments])
        ).order_by(Course.rating.desc()).limit(4).all()
    
    # Get user's completed certificates
    certificates = Certificate.query.filter_by(aihub_user_id=current_user.id).all()
    
    return render_template(
        'dashboard.html',
        enrolled_courses=enrolled_courses,
        recommended_courses=recommended_courses,
        certificates=certificates
    )


@app.route('/courses')
def courses():
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    search = request.args.get('search', '')
    
    query = Course.query
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if search:
        query = query.filter(Course.title.ilike(f'%{search}%'))
    
    courses = query.order_by(Course.title).all()
    categories = db.session.query(Course.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template(
        'courses.html',
        courses=courses,
        categories=categories,
        current_category=category,
        current_level=level,
        search_term=search
    )


@app.route('/course/<slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
    
    # Check if user is enrolled
    is_enrolled = False
    user_progress = 0
    
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            aihub_user_id=current_user.id,
            course_id=course.id
        ).first()
        
        is_enrolled = enrollment is not None
        
        if is_enrolled:
            progress = ProgressRecord.query.filter_by(
                aihub_user_id=current_user.id,
                course_id=course.id
            ).first()
            
            if progress:
                user_progress = progress.progress_percentage
    
    # Get reviews
    reviews = Review.query.filter_by(course_id=course.id).order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template(
        'course_detail.html',
        course=course,
        modules=modules,
        is_enrolled=is_enrolled,
        user_progress=user_progress,
        reviews=reviews
    )


@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course.id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('course_detail', slug=course.slug))
    
    # Check if course is premium and user has subscription
    if course.is_premium and not current_user.is_subscribed():
        flash('This is a premium course. Please upgrade your subscription.', 'warning')
        return redirect(url_for('pricing'))
    
    # Create enrollment
    enrollment = Enrollment(aihub_user_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    
    # Create progress record
    progress = ProgressRecord(
        aihub_user_id=current_user.id,
        course_id=course.id,
        progress_percentage=0
    )
    db.session.add(progress)
    
    # Update course enrollment count
    course.enrollment_count += 1
    
    db.session.commit()
    
    flash('You have successfully enrolled in this course!', 'success')
    return redirect(url_for('learn', course_slug=course.slug))


@app.route('/learn/<course_slug>')
@login_required
def learn(course_slug):
    course = Course.query.filter_by(slug=course_slug).first_or_404()
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course.id
    ).first_or_404()
    
    # Get course modules and lessons
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
    
    # Get user progress
    progress = ProgressRecord.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course.id
    ).first()
    
    # Get completed lessons
    completed_lessons = CompletedLesson.query.filter_by(
        aihub_user_id=current_user.id
    ).all()
    completed_lesson_ids = [cl.lesson_id for cl in completed_lessons]
    
    # If there's a last lesson, get it; otherwise get the first lesson
    if progress and progress.last_lesson_id:
        current_lesson = Lesson.query.get(progress.last_lesson_id)
    else:
        first_module = modules[0] if modules else None
        if first_module:
            current_lesson = Lesson.query.filter_by(module_id=first_module.id).order_by(Lesson.order).first()
        else:
            current_lesson = None
    
    return render_template(
        'learn.html',
        course=course,
        modules=modules,
        current_lesson=current_lesson,
        progress=progress,
        completed_lesson_ids=completed_lesson_ids
    )


@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    module = Module.query.get_or_404(lesson.module_id)
    course = Course.query.get_or_404(module.course_id)
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course.id
    ).first_or_404()
    
    # Check if lesson is premium and user has subscription
    if not lesson.is_free and course.is_premium and not current_user.is_subscribed():
        flash('This lesson requires a premium subscription.', 'warning')
        return redirect(url_for('pricing'))
    
    # Update user's last accessed lesson
    progress = ProgressRecord.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course.id
    ).first()
    
    if progress:
        progress.last_lesson_id = lesson.id
        progress.updated_at = datetime.utcnow()
        db.session.commit()
    
    # Get next and previous lessons
    next_lesson = Lesson.query.filter(
        Lesson.module_id == module.id,
        Lesson.order > lesson.order
    ).order_by(Lesson.order).first()
    
    if not next_lesson:
        # Check if there's a next module
        next_module = Module.query.filter(
            Module.course_id == course.id,
            Module.order > module.order
        ).order_by(Module.order).first()
        
        if next_module:
            next_lesson = Lesson.query.filter_by(
                module_id=next_module.id
            ).order_by(Lesson.order).first()
    
    prev_lesson = Lesson.query.filter(
        Lesson.module_id == module.id,
        Lesson.order < lesson.order
    ).order_by(Lesson.order.desc()).first()
    
    if not prev_lesson:
        # Check if there's a previous module
        prev_module = Module.query.filter(
            Module.course_id == course.id,
            Module.order < module.order
        ).order_by(Module.order.desc()).first()
        
        if prev_module:
            prev_lesson = Lesson.query.filter_by(
                module_id=prev_module.id
            ).order_by(Lesson.order.desc()).first()
    
    # Check if lesson is completed
    is_completed = CompletedLesson.query.filter_by(
        aihub_user_id=current_user.id,
        lesson_id=lesson.id
    ).first() is not None
    
    # If this is a quiz lesson, get the questions
    quiz_questions = []
    if lesson.lesson_type == 'quiz':
        quiz_questions = QuizQuestion.query.filter_by(
            lesson_id=lesson.id
        ).order_by(QuizQuestion.order).all()
    
    return render_template(
        'lesson.html',
        course=course,
        module=module,
        lesson=lesson,
        next_lesson=next_lesson,
        prev_lesson=prev_lesson,
        is_completed=is_completed,
        quiz_questions=quiz_questions
    )


@app.route('/api/complete-lesson', methods=['POST'])
@login_required
def complete_lesson():
    data = request.json
    lesson_id = data.get('lesson_id')
    course_id = data.get('course_id')
    
    if not lesson_id or not course_id:
        return jsonify({'success': False, 'error': 'Missing required parameters'})
    
    # Check if already completed
    existing = CompletedLesson.query.filter_by(
        aihub_user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not existing:
        # Mark lesson as completed
        completed = CompletedLesson(
            aihub_user_id=current_user.id,
            lesson_id=lesson_id
        )
        db.session.add(completed)
        
        # Update progress
        course = Course.query.get_or_404(course_id)
        total_lessons = 0
        
        # Count total lessons in course
        for module in Module.query.filter_by(course_id=course_id).all():
            total_lessons += Lesson.query.filter_by(module_id=module.id).count()
        
        # Count completed lessons
        completed_count = CompletedLesson.query.filter(
            CompletedLesson.aihub_user_id == current_user.id,
            CompletedLesson.lesson_id.in_([
                l.id for m in Module.query.filter_by(course_id=course_id).all()
                for l in Lesson.query.filter_by(module_id=m.id).all()
            ])
        ).count() + 1  # +1 for the current lesson
        
        # Calculate percentage
        completion_percentage = (completed_count / total_lessons) * 100 if total_lessons > 0 else 0
        
        # Update progress record
        progress = ProgressRecord.query.filter_by(
            aihub_user_id=current_user.id,
            course_id=course_id
        ).first()
        
        if progress:
            progress.progress_percentage = completion_percentage
            progress.updated_at = datetime.utcnow()
        else:
            progress = ProgressRecord(
                aihub_user_id=current_user.id,
                course_id=course_id,
                progress_percentage=completion_percentage
            )
            db.session.add(progress)
        
        # Check if course is completed
        is_completed = completion_percentage >= 100
        if is_completed:
            enrollment = Enrollment.query.filter_by(
                aihub_user_id=current_user.id,
                course_id=course_id
            ).first()
            
            if enrollment:
                enrollment.completed = True
                enrollment.completion_date = datetime.utcnow()
                
                # Generate certificate
                certificate = Certificate.query.filter_by(
                    aihub_user_id=current_user.id,
                    course_id=course_id
                ).first()
                
                if not certificate:
                    import uuid
                    certificate_id = f"{course.slug[:8]}-{uuid.uuid4().hex[:8]}"
                    certificate = Certificate(
                        aihub_user_id=current_user.id,
                        course_id=course_id,
                        certificate_id=certificate_id
                    )
                    db.session.add(certificate)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'completion_percentage': completion_percentage,
            'is_completed': is_completed
        })
    
    # Already completed, just return current progress
    progress = ProgressRecord.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course_id
    ).first()
    
    return jsonify({
        'success': True,
        'completion_percentage': progress.progress_percentage if progress else 0,
        'is_completed': progress.progress_percentage >= 100 if progress else False
    })


@app.route('/api/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    data = request.json
    quiz_id = data.get('quiz_id')
    lesson_id = data.get('lesson_id')
    course_id = data.get('course_id')
    answers = data.get('answers', {})
    
    if not lesson_id or not course_id:
        return jsonify({'success': False, 'error': 'Missing required parameters'})
    
    # Get all questions for this quiz
    questions = QuizQuestion.query.filter_by(lesson_id=lesson_id).all()
    
    total_score = 0
    total_questions = len(questions)
    
    for question in questions:
        question_id = str(question.id)
        if question_id in answers:
            user_answer = answers[question_id]
            if user_answer == question.correct_answer:
                total_score += 1
    
    # Calculate percentage
    percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0
    passed = percentage >= 70  # Pass threshold
    
    # If passed, mark lesson as completed
    if passed:
        # Check if already completed
        existing = CompletedLesson.query.filter_by(
            aihub_user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not existing:
            completed = CompletedLesson(
                aihub_user_id=current_user.id,
                lesson_id=lesson_id,
                quiz_score=percentage
            )
            db.session.add(completed)
            db.session.commit()
    
    return jsonify({
        'success': True,
        'score': total_score,
        'total': total_questions,
        'percentage': percentage,
        'passed': passed
    })


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = current_user
    
    # Update user fields
    user.full_name = request.form.get('full_name', user.full_name)
    user.bio = request.form.get('bio', user.bio)
    user.skill_level = request.form.get('skill_level', user.skill_level)
    user.interests = request.form.get('interests', user.interests)
    user.learning_goal = request.form.get('learning_goal', user.learning_goal)
    
    # Handle profile image upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename:
            # TODO: Add proper file upload handling
            # For now, we'll set a placeholder
            user.profile_image = '/static/img/profiles/default.jpg'
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/submit-review', methods=['POST'])
@login_required
def submit_review():
    course_id = request.form.get('course_id')
    rating = request.form.get('rating')
    review_text = request.form.get('review_text')
    
    if not course_id or not rating:
        flash('Missing required fields', 'error')
        return redirect(request.referrer)
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in the course to review it', 'error')
        return redirect(request.referrer)
    
    # Check if user already reviewed
    existing_review = Review.query.filter_by(
        aihub_user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.review_text = review_text
        existing_review.updated_at = datetime.utcnow()
    else:
        # Create new review
        review = Review(
            aihub_user_id=current_user.id,
            course_id=course_id,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)
    
    # Update course rating
    course = Course.query.get(course_id)
    if course:
        all_reviews = Review.query.filter_by(course_id=course_id).all()
        total_rating = sum(r.rating for r in all_reviews)
        count = len(all_reviews) if existing_review else len(all_reviews) + 1
        
        course.rating = total_rating / count if count > 0 else 0
        course.rating_count = count
    
    db.session.commit()
    flash('Thank you for your review!', 'success')
    return redirect(request.referrer)


@app.route('/certificate/<certificate_id>')
def view_certificate(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    course = Course.query.get_or_404(certificate.course_id)
    user = AIHubUser.query.get_or_404(certificate.aihub_user_id)
    
    return render_template(
        'certificate.html',
        certificate=certificate,
        course=course,
        user=user
    )


# Database initialization command
@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    print('Initialized the database.')