"""
Initialize database with sample content for AI Learning Hub
"""
import json
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_learning_hub.app import app, db
from ai_learning_hub.models import (
    AIHubUser, Certificate, CompletedLesson, Course, Enrollment, Lesson, Module,
    ProgressRecord, QuizQuestion, Review
)

def init_db():
    """Create initial data for the AI Learning Hub"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        if User.query.count() > 0:
            print("Database already initialized, skipping...")
            return
        
        print("Creating admin user...")
        admin = User(
            username="admin",
            email="admin@ailearninghub.com",
            full_name="Admin User",
            skill_level="advanced",
            interests="machine learning, deep learning, ai ethics",
            join_date=datetime.utcnow() - timedelta(days=100)
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        print("Creating regular users...")
        # Create sample users
        john = User(
            username="john_doe",
            email="john@example.com",
            full_name="John Doe",
            bio="AI enthusiast and software engineer",
            skill_level="intermediate",
            interests="machine learning, deep learning, nlp",
            join_date=datetime.utcnow() - timedelta(days=45)
        )
        john.set_password("password123")
        db.session.add(john)
        
        jane = User(
            username="jane_smith",
            email="jane@example.com",
            full_name="Jane Smith",
            bio="Data scientist with 5 years of experience",
            skill_level="advanced",
            interests="data science, computer vision, reinforcement learning",
            join_date=datetime.utcnow() - timedelta(days=30)
        )
        jane.set_password("password123")
        db.session.add(jane)
        
        # Create sample courses
        print("Creating courses...")
        
        ml_intro = Course(
            title="Introduction to Machine Learning",
            slug="intro-to-machine-learning",
            description="""
            This comprehensive introduction to Machine Learning covers all the fundamental concepts 
            needed to understand how ML systems work. Through practical exercises and real-world examples, 
            you'll build a strong foundation in machine learning theory and practice.
            
            By the end of this course, you'll understand:
            - The difference between supervised and unsupervised learning
            - How to prepare data for machine learning algorithms
            - When to use classification vs regression models
            - How to evaluate model performance
            - Basic machine learning algorithms and their applications
            """,
            short_description="A beginner-friendly introduction to machine learning concepts and techniques.",
            cover_image="/static/img/course-placeholder.jpg",
            level="beginner",
            price=0.0,
            is_premium=False,
            category="machine-learning",
            tags="ml, beginners, python, algorithms",
            prerequisites="Basic Python programming knowledge",
            learning_outcomes=json.dumps([
                "Understand fundamental ML concepts",
                "Apply common ML algorithms to real problems",
                "Prepare datasets for machine learning",
                "Evaluate and improve model performance"
            ]),
            instructor_id=1,
            rating=4.8,
            rating_count=245,
            enrollment_count=1250,
            meta_title="Introduction to Machine Learning | AI Learning Hub",
            meta_description="Learn the foundations of machine learning with hands-on projects and intuitive explanations. Perfect for beginners.",
            seo_keywords="machine learning, ML basics, learn ML, beginner AI course"
        )
        db.session.add(ml_intro)
        
        deep_learning = Course(
            title="Deep Learning Fundamentals",
            slug="deep-learning-fundamentals",
            description="""
            Dive into the world of neural networks and deep learning with this comprehensive course.
            From basic perceptrons to complex architectures like CNNs and RNNs, you'll learn the theory
            and practice of building deep learning models for various applications.
            
            This course covers:
            - Neural network fundamentals
            - Training and optimization techniques
            - Convolutional Neural Networks (CNNs)
            - Recurrent Neural Networks (RNNs)
            - Transfer learning
            - Model deployment strategies
            
            You'll complete hands-on projects using popular frameworks like TensorFlow and PyTorch.
            """,
            short_description="Master neural networks and deep learning architectures with hands-on projects.",
            cover_image="/static/img/course-placeholder.jpg",
            level="intermediate",
            price=49.99,
            is_premium=True,
            category="deep-learning",
            tags="deep learning, neural networks, CNN, RNN, tensorflow, pytorch",
            prerequisites="Basic machine learning knowledge, Python programming",
            learning_outcomes=json.dumps([
                "Build and train neural networks from scratch",
                "Implement CNNs for image recognition tasks",
                "Develop RNNs for sequence modeling",
                "Apply transfer learning techniques",
                "Deploy models to production environments"
            ]),
            instructor_id=2,
            rating=4.9,
            rating_count=186,
            enrollment_count=825,
            meta_title="Deep Learning Fundamentals | AI Learning Hub",
            meta_description="Learn to build and train neural networks for various applications with hands-on projects using TensorFlow and PyTorch.",
            seo_keywords="deep learning, neural networks, CNN, RNN, tensorflow, pytorch"
        )
        db.session.add(deep_learning)
        
        nlp_course = Course(
            title="Natural Language Processing",
            slug="natural-language-processing",
            description="""
            Explore the fascinating field of Natural Language Processing (NLP) and learn how to build
            systems that can understand, analyze, and generate human language. This course combines
            theoretical foundations with practical applications.
            
            Topics covered include:
            - Text preprocessing techniques
            - Language modeling and word embeddings
            - Sentiment analysis and text classification
            - Named entity recognition
            - Machine translation
            - Question answering systems
            - Transformer architectures and BERT
            
            Through hands-on projects, you'll build real NLP applications using modern libraries and frameworks.
            """,
            short_description="Learn to build systems that understand and generate human language.",
            cover_image="/static/img/course-placeholder.jpg",
            level="intermediate",
            price=59.99,
            is_premium=True,
            category="nlp",
            tags="nlp, text processing, BERT, transformers, language models",
            prerequisites="Python programming, basic machine learning knowledge",
            learning_outcomes=json.dumps([
                "Process and prepare text data for NLP tasks",
                "Build word embedding models",
                "Develop sentiment analysis applications",
                "Implement named entity recognition systems",
                "Apply transformer models to NLP tasks"
            ]),
            instructor_id=2,
            rating=4.7,
            rating_count=134,
            enrollment_count=612,
            meta_title="Natural Language Processing | AI Learning Hub",
            meta_description="Master NLP techniques and build systems that understand and generate human language with modern frameworks.",
            seo_keywords="NLP, natural language processing, text analysis, BERT, transformers"
        )
        db.session.add(nlp_course)
        
        db.session.commit()
        
        # Create sample modules for Intro to ML course
        print("Creating modules and lessons...")
        
        module1 = Module(
            title="Introduction to ML Concepts",
            description="Understand the foundational concepts of machine learning and its applications.",
            course_id=1,
            order=1
        )
        db.session.add(module1)
        
        module2 = Module(
            title="Data Preparation",
            description="Learn how to prepare and preprocess data for machine learning algorithms.",
            course_id=1,
            order=2
        )
        db.session.add(module2)
        
        module3 = Module(
            title="Supervised Learning",
            description="Explore supervised learning algorithms for classification and regression tasks.",
            course_id=1,
            order=3
        )
        db.session.add(module3)
        
        # Create sample lessons for module 1
        lesson1 = Lesson(
            title="What is Machine Learning?",
            slug="what-is-machine-learning",
            content="""
            # What is Machine Learning?
            
            Machine Learning (ML) is a subset of artificial intelligence that focuses on developing systems that learn from data without being explicitly programmed. Instead of writing code with specific instructions to accomplish a task, we provide a model with examples, and it learns to perform the task from these examples.
            
            ## Key Concepts
            
            ### Learning from Data
            
            Machine learning algorithms build a model based on sample data, known as "training data," to make predictions or decisions without being explicitly programmed to do so. The quality and quantity of the training data significantly impact the model's performance.
            
            ### Types of Machine Learning
            
            1. **Supervised Learning**: The algorithm learns from labeled training data, and makes predictions based on that data.
            2. **Unsupervised Learning**: The algorithm learns from unlabeled data, finding hidden patterns or intrinsic structures.
            3. **Reinforcement Learning**: The algorithm learns by interacting with an environment, receiving feedback in the form of rewards or penalties.
            
            ### Applications of Machine Learning
            
            Machine learning is used in various applications:
            
            - Image and speech recognition
            - Email filtering
            - Recommendation systems
            - Fraud detection
            - Medical diagnosis
            - Self-driving cars
            - Natural language processing
            
            ## Machine Learning vs. Traditional Programming
            
            In traditional programming, we provide the computer with an algorithm (a set of instructions) to solve a problem. In machine learning, we provide the computer with data and let it find the algorithm itself.
            
            | Traditional Programming | Machine Learning |
            |-------------------------|------------------|
            | Human creates rules (algorithms) | Machine creates rules from data |
            | Input: Data + Algorithm | Input: Data + Desired Output |
            | Output: Answer | Output: Algorithm |
            
            ## The Machine Learning Workflow
            
            1. **Data Collection**: Gather relevant data for your problem.
            2. **Data Preparation**: Clean and preprocess the data.
            3. **Feature Engineering**: Select and transform the most important features.
            4. **Model Selection**: Choose the appropriate algorithm.
            5. **Training**: Feed the training data to the algorithm.
            6. **Evaluation**: Assess the model's performance.
            7. **Hyperparameter Tuning**: Optimize the model's parameters.
            8. **Deployment**: Implement the model in a real-world environment.
            
            ## Conclusion
            
            Machine learning is a powerful tool that can help solve complex problems by learning from data. As you progress through this course, you'll learn how to implement various machine learning algorithms and apply them to real-world problems.
            """,
            module_id=1,
            order=1,
            lesson_type="text",
            is_free=True
        )
        db.session.add(lesson1)
        
        lesson2 = Lesson(
            title="AI, ML, and Deep Learning: Understanding the Differences",
            slug="ai-ml-deep-learning-differences",
            content="""
            # AI, ML, and Deep Learning: Understanding the Differences
            
            Artificial Intelligence (AI), Machine Learning (ML), and Deep Learning are related but distinct concepts in the field of computer science. Understanding the differences and relationships between these terms is crucial for anyone entering the field.
            
            ## Artificial Intelligence
            
            Artificial Intelligence is the broadest term, referring to machines or systems that can perform tasks that typically require human intelligence. These tasks include:
            
            - Reasoning
            - Problem-solving
            - Understanding natural language
            - Perception
            - Learning
            
            AI can be categorized into:
            
            - **Narrow/Weak AI**: Systems designed for a specific task (like virtual assistants or image recognition)
            - **General/Strong AI**: Systems with generalized human cognitive abilities
            
            ## Machine Learning
            
            Machine Learning is a subset of AI that focuses on the development of algorithms that allow computers to learn from and make predictions or decisions based on data. Instead of explicitly programming rules, ML systems learn patterns from examples.
            
            Key approaches in Machine Learning include:
            
            - **Supervised Learning**: Learning from labeled training data
            - **Unsupervised Learning**: Finding patterns in unlabeled data
            - **Reinforcement Learning**: Learning through interaction with an environment
            
            Common ML algorithms include linear regression, decision trees, random forests, support vector machines, and k-means clustering.
            
            ## Deep Learning
            
            Deep Learning is a specialized subset of Machine Learning that uses neural networks with multiple layers (hence "deep") to analyze various factors of data. Deep Learning has been revolutionary in solving complex problems like:
            
            - Image and speech recognition
            - Natural language processing
            - Game playing
            - Drug discovery
            
            Deep Learning architectures include:
            
            - Convolutional Neural Networks (CNNs)
            - Recurrent Neural Networks (RNNs)
            - Transformers
            - Generative Adversarial Networks (GANs)
            
            ## The Relationship: AI ⊃ ML ⊃ Deep Learning
            
            Think of these concepts as nested subsets:
            
            - **AI** is the largest field, encompassing any technique that enables computers to mimic human intelligence
            - **Machine Learning** is a subset of AI that focuses on systems that can learn from data
            - **Deep Learning** is a subset of ML that uses multi-layered neural networks to learn from data
            
            ## When to Use Which Approach
            
            - **AI** approaches like expert systems might be suitable when you have clear rules and logic
            - **ML** algorithms like decision trees or random forests work well for structured data with clear features
            - **Deep Learning** excels with large amounts of unstructured data (images, text, audio) and complex patterns
            
            ## Conclusion
            
            While these terms are often used interchangeably in popular media, understanding their distinctions is important for anyone working in the field. As we progress through this course, we'll focus primarily on Machine Learning techniques, with some introduction to Deep Learning concepts.
            """,
            module_id=1,
            order=2,
            lesson_type="text",
            is_free=True
        )
        db.session.add(lesson2)
        
        lesson3 = Lesson(
            title="Machine Learning Applications",
            slug="machine-learning-applications",
            content="""
            # Machine Learning Applications
            
            Machine learning has transformed numerous industries by enabling new capabilities and improving existing processes. In this lesson, we'll explore some of the most impactful applications of machine learning across different domains.
            
            ## Healthcare
            
            - **Disease Diagnosis**: ML models can analyze medical images to detect diseases like cancer, often with accuracy comparable to human experts.
            - **Predictive Analytics**: Algorithms can predict patient readmission risks or potential disease outbreaks.
            - **Drug Discovery**: ML accelerates the identification of potential drug candidates by analyzing molecular structures.
            - **Personalized Medicine**: ML helps tailor treatments based on individual patient characteristics and genetic profiles.
            
            ## Finance
            
            - **Fraud Detection**: ML systems identify unusual patterns that may indicate fraudulent transactions.
            - **Algorithmic Trading**: ML models analyze market data to make trading decisions.
            - **Credit Scoring**: Advanced algorithms assess creditworthiness beyond traditional methods.
            - **Risk Management**: ML helps financial institutions evaluate and manage various forms of risk.
            
            ## Retail and E-commerce
            
            - **Recommendation Systems**: ML powers product recommendations based on user behavior and preferences.
            - **Inventory Management**: Predictive models optimize inventory levels based on forecasted demand.
            - **Price Optimization**: ML determines optimal pricing strategies based on multiple factors.
            - **Customer Segmentation**: Algorithms group customers based on behavior for targeted marketing.
            
            ## Transportation
            
            - **Autonomous Vehicles**: ML enables self-driving cars to perceive their environment and make driving decisions.
            - **Traffic Prediction**: ML models forecast traffic conditions to optimize routes.
            - **Ride-sharing Optimization**: Algorithms match drivers with riders efficiently.
            - **Predictive Maintenance**: ML detects potential equipment failures before they occur.
            
            ## Entertainment and Media
            
            - **Content Recommendations**: Streaming services use ML to suggest movies, shows, or music.
            - **Content Creation**: ML assists in creating music, art, and even writing scripts.
            - **User Experience Personalization**: Websites and apps adapt to individual user preferences.
            - **Sentiment Analysis**: ML gauges audience reactions to content across social media.
            
            ## Manufacturing
            
            - **Quality Control**: ML-powered visual inspection systems detect defects more efficiently than manual methods.
            - **Supply Chain Optimization**: Algorithms predict supply chain disruptions and optimize logistics.
            - **Predictive Maintenance**: ML models detect machinery problems before they cause failures.
            - **Process Optimization**: ML improves manufacturing processes by identifying inefficiencies.
            
            ## Agriculture
            
            - **Crop Monitoring**: ML analyzes satellite and drone imagery to monitor crop health.
            - **Yield Prediction**: Algorithms forecast crop yields based on various factors.
            - **Precision Farming**: ML enables precise application of water, fertilizers, and pesticides.
            - **Livestock Management**: ML monitors animal health and optimizes feeding strategies.
            
            ## Energy
            
            - **Energy Consumption Prediction**: ML forecasts energy demand to balance grid loads.
            - **Renewable Energy Optimization**: Algorithms maximize energy harvesting from renewable sources.
            - **Fault Detection**: ML identifies potential failures in energy infrastructure.
            - **Energy Efficiency**: ML optimizes energy usage in buildings and industrial processes.
            
            ## Ethical Considerations
            
            As ML applications continue to grow, it's crucial to consider:
            
            - **Bias and Fairness**: Ensuring ML systems don't perpetuate or amplify existing biases
            - **Privacy**: Protecting sensitive data used to train and operate ML systems
            - **Transparency**: Making ML decisions interpretable and explainable
            - **Accountability**: Establishing responsibility for ML system outcomes
            
            ## Conclusion
            
            Machine learning applications continue to expand as the technology matures and datasets grow. The examples discussed here represent just a fraction of how ML is transforming our world. As you progress through this course, you'll develop the skills to contribute to these exciting applications and perhaps create entirely new ones.
            """,
            module_id=1,
            order=3,
            lesson_type="text",
            is_free=False
        )
        db.session.add(lesson3)
        
        lesson4 = Lesson(
            title="Understanding the ML Ecosystem",
            slug="understanding-ml-ecosystem",
            content="""
            # Understanding the ML Ecosystem
            
            The machine learning ecosystem consists of various tools, frameworks, libraries, and platforms that enable data scientists and machine learning engineers to develop, train, deploy, and maintain machine learning models efficiently. In this lesson, we'll explore this ecosystem and understand how different components work together.
            
            ## Programming Languages
            
            Several programming languages are commonly used in machine learning:
            
            - **Python**: The most popular language for ML due to its simplicity and extensive libraries
            - **R**: Widely used for statistical computing and data analysis
            - **Julia**: Gaining popularity for its high performance in numerical computing
            - **Java/Scala**: Often used in production systems and big data environments
            
            ## Data Processing Libraries
            
            Before applying ML algorithms, data typically needs preprocessing:
            
            - **NumPy**: Fundamental package for scientific computing in Python
            - **Pandas**: Data manipulation and analysis library
            - **Dask**: Parallel computing library for scaling to larger datasets
            - **Apache Spark**: Big data processing framework
            
            ## Machine Learning Libraries
            
            These libraries implement various ML algorithms and utilities:
            
            - **Scikit-learn**: Comprehensive library for classical ML algorithms
            - **XGBoost/LightGBM**: Gradient boosting frameworks
            - **TensorFlow**: End-to-end open source platform for ML
            - **PyTorch**: Deep learning framework with dynamic computation graphs
            - **Keras**: High-level neural networks API
            - **JAX**: High-performance numerical computing with automatic differentiation
            
            ## Visualization Tools
            
            Visualizing data and model results is crucial for understanding and communicating findings:
            
            - **Matplotlib**: Basic plotting library
            - **Seaborn**: Statistical data visualization
            - **Plotly**: Interactive visualizations
            - **Tableau**: Business intelligence and analytics platform
            - **PowerBI**: Business analytics service
            
            ## Experiment Tracking and Model Management
            
            Tools for tracking experiments and managing models:
            
            - **MLflow**: Platform for managing the ML lifecycle
            - **Weights & Biases**: Tool for tracking experiments
            - **TensorBoard**: Visualization toolkit for TensorFlow
            - **Neptune.ai**: Metadata store for MLOps
            
            ## Model Deployment
            
            Frameworks and services for deploying models to production:
            
            - **Flask/FastAPI**: Web frameworks for creating APIs
            - **TensorFlow Serving**: System for serving TensorFlow models
            - **ONNX**: Open format for representing machine learning models
            - **Docker**: Containerization platform
            - **Kubernetes**: Container orchestration system
            
            ## Cloud Platforms
            
            Major cloud providers offer ML services:
            
            - **AWS SageMaker**: End-to-end ML platform
            - **Google Cloud AI Platform**: Suite of ML services
            - **Azure Machine Learning**: Comprehensive ML service
            - **IBM Watson**: AI platform for business
            
            ## AutoML Tools
            
            Automated machine learning tools that simplify the ML process:
            
            - **Google AutoML**: Suite of ML products
            - **H2O AutoML**: Automated machine learning
            - **AutoKeras**: AutoML system based on Keras
            - **TPOT**: Automated ML tool that optimizes machine learning pipelines
            
            ## Development Environments
            
            Tools for writing and executing ML code:
            
            - **Jupyter Notebooks**: Interactive computing environment
            - **Google Colab**: Free cloud-based Jupyter notebook environment
            - **VS Code**: Code editor with ML extensions
            - **PyCharm**: Python IDE with data science features
            
            ## ML Workflow Components
            
            The typical machine learning workflow includes:
            
            1. **Data Collection**: Gathering relevant data from various sources
            2. **Data Preparation**: Cleaning, transforming, and preparing the data
            3. **Feature Engineering**: Creating new features or selecting important ones
            4. **Model Training**: Training algorithms on the prepared data
            5. **Model Evaluation**: Assessing model performance
            6. **Model Deployment**: Making the model available for predictions
            7. **Monitoring**: Tracking model performance in production
            
            ## MLOps
            
            Machine Learning Operations (MLOps) is a set of practices that aims to deploy and maintain ML models in production reliably and efficiently:
            
            - **Continuous Integration/Continuous Deployment (CI/CD)**: Automating testing and deployment
            - **Model Versioning**: Tracking different versions of models
            - **Monitoring**: Observing model performance and data drift
            - **Governance**: Ensuring compliance with regulations and standards
            
            ## Conclusion
            
            The machine learning ecosystem is rich and diverse, with tools and frameworks for every step of the ML lifecycle. As you progress in your ML journey, you'll become familiar with many of these components and learn to choose the right tools for specific tasks. In this course, we'll focus primarily on Python-based libraries like scikit-learn, pandas, and NumPy, which form the foundation of most ML workflows.
            """,
            module_id=1,
            order=4,
            lesson_type="text",
            is_free=False
        )
        db.session.add(lesson4)
        
        # Quiz for module 1
        lesson5 = Lesson(
            title="Module 1 Quiz",
            slug="module-1-quiz",
            content="Test your understanding of machine learning concepts covered in this module.",
            module_id=1,
            order=5,
            lesson_type="quiz",
            is_free=False
        )
        db.session.add(lesson5)
        db.session.commit()
        
        # Add quiz questions
        quiz1 = QuizQuestion(
            lesson_id=5,
            question_text="Which of the following is NOT a type of machine learning?",
            question_type="multiple_choice",
            options=json.dumps([
                "Supervised Learning",
                "Unsupervised Learning",
                "Reinforcement Learning",
                "Determinate Learning"
            ]),
            correct_answer="Determinate Learning",
            explanation="The three main types of machine learning are Supervised Learning, Unsupervised Learning, and Reinforcement Learning. 'Determinate Learning' is not a recognized type of machine learning.",
            order=1
        )
        db.session.add(quiz1)
        
        quiz2 = QuizQuestion(
            lesson_id=5,
            question_text="In machine learning, what is the data used to train a model called?",
            question_type="multiple_choice",
            options=json.dumps([
                "Testing data",
                "Training data",
                "Validation data",
                "Production data"
            ]),
            correct_answer="Training data",
            explanation="Training data is the dataset used to train a machine learning model. The model learns patterns from this data to make predictions.",
            order=2
        )
        
        db.session.add(quiz2)
        
        quiz3 = QuizQuestion(
            lesson_id=5,
            question_text="Deep Learning is a subset of Machine Learning.",
            question_type="true_false",
            options=json.dumps([
                "True",
                "False"
            ]),
            correct_answer="True",
            explanation="Deep Learning is indeed a specialized subset of Machine Learning that uses neural networks with multiple layers to analyze various factors of data.",
            order=3
        )
        
        db.session.add(quiz3)
        
        quiz4 = QuizQuestion(
            lesson_id=5,
            question_text="Which of the following is NOT a common application of machine learning?",
            question_type="multiple_choice",
            options=json.dumps([
                "Image recognition",
                "Fraud detection",
                "Mechanical engineering calculations",
                "Recommendation systems"
            ]),
            correct_answer="Mechanical engineering calculations",
            explanation="While machine learning can be applied to some aspects of mechanical engineering, traditional mechanical engineering calculations typically rely on established physical equations and principles rather than learning from data.",
            order=4
        )
        
        db.session.add(quiz4)
        
        quiz5 = QuizQuestion(
            lesson_id=5,
            question_text="In traditional programming, humans provide the algorithm and data to get answers. In machine learning, what do humans provide?",
            question_type="multiple_choice",
            options=json.dumps([
                "Only algorithms",
                "Only data",
                "Data and desired outputs",
                "Nothing; the machine learns everything on its own"
            ]),
            correct_answer="Data and desired outputs",
            explanation="In machine learning, humans typically provide data and the desired outputs (for supervised learning), and the machine creates the algorithm (model) that maps inputs to outputs.",
            order=5
        )
        
        db.session.add(quiz5)
        
        print("Creating sample lessons for modules 2 and 3...")
        # Create sample lessons for module 2 (Data Preparation)
        lesson6 = Lesson(
            title="Understanding Data Types",
            slug="understanding-data-types",
            content="Content about different data types in machine learning...",
            module_id=2,
            order=1,
            lesson_type="text",
            is_free=True
        )
        db.session.add(lesson6)
        
        lesson7 = Lesson(
            title="Data Cleaning Techniques",
            slug="data-cleaning-techniques",
            content="Content about data cleaning, handling missing values...",
            module_id=2,
            order=2,
            lesson_type="text",
            is_free=False
        )
        db.session.add(lesson7)
        
        # Create sample lessons for module 3 (Supervised Learning)
        lesson8 = Lesson(
            title="Introduction to Supervised Learning",
            slug="intro-supervised-learning",
            content="Content about supervised learning concepts...",
            module_id=3,
            order=1,
            lesson_type="text",
            is_free=True
        )
        db.session.add(lesson8)
        
        lesson9 = Lesson(
            title="Linear Regression",
            slug="linear-regression",
            content="Content about linear regression algorithm...",
            module_id=3,
            order=2,
            lesson_type="text",
            is_free=False,
            video_url="https://www.youtube.com/embed/zPG4NjIkCjc"
        )
        db.session.add(lesson9)
        
        # Create modules for Deep Learning course
        dl_module1 = Module(
            title="Neural Network Fundamentals",
            description="Learn the basic concepts and components of neural networks.",
            course_id=2,
            order=1
        )
        db.session.add(dl_module1)
        
        dl_module2 = Module(
            title="Convolutional Neural Networks",
            description="Understand the architecture and applications of CNNs.",
            course_id=2,
            order=2
        )
        db.session.add(dl_module2)
        
        # Create modules for NLP course
        nlp_module1 = Module(
            title="Text Preprocessing",
            description="Learn how to clean and prepare text data for NLP tasks.",
            course_id=3,
            order=1
        )
        db.session.add(nlp_module1)
        
        nlp_module2 = Module(
            title="Word Embeddings",
            description="Understand how to represent words as vectors for NLP tasks.",
            course_id=3,
            order=2
        )
        db.session.add(nlp_module2)
        
        # Create some user enrollments
        print("Creating enrollments and progress records...")
        enrollment1 = Enrollment(
            user_id=2,  # John Doe
            course_id=1,  # Intro to ML
            enrolled_at=datetime.utcnow() - timedelta(days=20)
        )
        db.session.add(enrollment1)
        
        progress1 = ProgressRecord(
            user_id=2,
            course_id=1,
            progress_percentage=35.0,
            last_lesson_id=3
        )
        db.session.add(progress1)
        
        completed1 = CompletedLesson(
            user_id=2,
            lesson_id=1,
            completed_at=datetime.utcnow() - timedelta(days=18)
        )
        db.session.add(completed1)
        
        completed2 = CompletedLesson(
            user_id=2,
            lesson_id=2,
            completed_at=datetime.utcnow() - timedelta(days=15)
        )
        db.session.add(completed2)
        
        # Add some reviews
        print("Adding reviews...")
        review1 = Review(
            user_id=2,
            course_id=1,
            rating=5,
            review_text="Excellent introduction to machine learning concepts! The explanations are clear and the examples are very helpful.",
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(review1)
        
        review2 = Review(
            user_id=3,
            course_id=1,
            rating=4,
            review_text="Very good content. I would have liked more practical exercises, but the theoretical explanations are excellent.",
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(review2)
        
        db.session.commit()
        print("Database initialization complete!")

if __name__ == "__main__":
    init_db()