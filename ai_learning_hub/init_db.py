"""
Initialize database with sample content for AI Learning Hub
"""
from datetime import datetime, timedelta
from ai_learning_hub.app import db
from ai_learning_hub.models import (
    AIHubUser, Course, Module, Lesson, UserCourse, LessonCompletion, UserNote
)

def init_db():
    """Create initial data for the AI Learning Hub"""
    # Check if we already have data
    if AIHubUser.query.count() > 0:
        print("Database already contains data. Skipping initialization.")
        return

    print("Initializing AI Learning Hub database with sample data...")

    # Create admin user
    admin = AIHubUser(
        username="admin",
        email="admin@ailearninghub.example.com",
        full_name="Admin User",
        subscription_status="active",
        subscription_expiry=datetime.utcnow() + timedelta(days=365)
    )
    admin.set_password("admin123")
    db.session.add(admin)

    # Create a test user
    test_user = AIHubUser(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        join_date=datetime.utcnow() - timedelta(days=30)
    )
    test_user.set_password("password123")
    db.session.add(test_user)

    # Commit the users so we can reference them
    db.session.commit()

    # Create sample courses
    courses = [
        {
            "title": "Introduction to Artificial Intelligence",
            "slug": "intro-to-ai",
            "description": "Learn the basics of artificial intelligence and machine learning.",
            "author_id": admin.id,
            "is_published": True,
            "difficulty_level": "beginner",
            "duration_minutes": 240,
            "category": "artificial-intelligence",
            "tags": "ai,machine learning,beginners",
            "thumbnail_url": "/static/img/courses/intro-to-ai.jpg"
        },
        {
            "title": "Advanced Deep Learning",
            "slug": "advanced-deep-learning",
            "description": "Master deep learning techniques for solving complex problems.",
            "author_id": admin.id,
            "is_published": True,
            "difficulty_level": "advanced",
            "duration_minutes": 480,
            "category": "deep-learning",
            "tags": "deep learning,neural networks,advanced",
            "thumbnail_url": "/static/img/courses/deep-learning.jpg"
        },
        {
            "title": "AI Ethics and Responsibility",
            "slug": "ai-ethics",
            "description": "Explore the ethical considerations and responsible use of AI technologies.",
            "author_id": admin.id,
            "is_published": True,
            "difficulty_level": "intermediate",
            "duration_minutes": 180,
            "category": "ai-ethics",
            "tags": "ethics,responsible ai,social impact",
            "thumbnail_url": "/static/img/courses/ai-ethics.jpg"
        }
    ]

    # Add courses to the database
    course_objects = []
    for course_data in courses:
        course = Course(**course_data)
        db.session.add(course)
        course_objects.append(course)

    # Commit courses so we can reference them
    db.session.commit()

    # Create modules for the first course
    intro_course = course_objects[0]
    intro_modules = [
        {
            "title": "What is Artificial Intelligence?",
            "description": "An introduction to AI concepts and history.",
            "course_id": intro_course.id,
            "order": 0
        },
        {
            "title": "Machine Learning Fundamentals",
            "description": "Learn the basics of machine learning algorithms.",
            "course_id": intro_course.id,
            "order": 1
        },
        {
            "title": "Neural Networks Basics",
            "description": "Introduction to neural networks and deep learning.",
            "course_id": intro_course.id,
            "order": 2
        }
    ]

    # Add modules to the database
    module_objects = []
    for module_data in intro_modules:
        module = Module(**module_data)
        db.session.add(module)
        module_objects.append(module)

    # Commit modules so we can reference them
    db.session.commit()

    # Create lessons for the first module
    intro_module = module_objects[0]
    intro_lessons = [
        {
            "title": "Definition and History of AI",
            "content": "<p>This lesson covers the definition of artificial intelligence and its historical development.</p>",
            "module_id": intro_module.id,
            "order": 0,
            "duration_minutes": 15
        },
        {
            "title": "Types of AI Systems",
            "content": "<p>Learn about different types of AI systems: narrow AI, general AI, and superintelligence.</p>",
            "module_id": intro_module.id,
            "order": 1,
            "duration_minutes": 20
        },
        {
            "title": "AI Applications in the Real World",
            "content": "<p>Explore real-world applications of AI in various industries and daily life.</p>",
            "module_id": intro_module.id,
            "order": 2,
            "duration_minutes": 25,
            "video_url": "https://example.com/videos/ai-applications.mp4"
        }
    ]

    # Add lessons to the database
    lesson_objects = []
    for lesson_data in intro_lessons:
        lesson = Lesson(**lesson_data)
        db.session.add(lesson)
        lesson_objects.append(lesson)

    # Commit lessons
    db.session.commit()

    # Enroll test user in first course
    enrollment = UserCourse(
        user_id=test_user.id,
        course_id=intro_course.id,
        enrolled_date=datetime.utcnow() - timedelta(days=7),
        last_accessed=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(enrollment)

    # Complete first lesson for test user
    completion = LessonCompletion(
        user_id=test_user.id,
        lesson_id=lesson_objects[0].id,
        completed_date=datetime.utcnow() - timedelta(days=5)
    )
    db.session.add(completion)

    # Add a note for the test user
    note = UserNote(
        user_id=test_user.id,
        lesson_id=lesson_objects[0].id,
        content="AI was first conceptualized in the 1950s. Key names to remember: Turing, McCarthy, Minsky.",
        created_at=datetime.utcnow() - timedelta(days=5)
    )
    db.session.add(note)

    # Commit all the remaining changes
    db.session.commit()

    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()