import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ai_learning_hub_dev_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ai_learning.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# Set configuration for JWT token
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "ai_learning_hub_jwt_dev_key") 

# initialize the extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
with app.app_context():
    # Import the models here or their tables won't be created
    import ai_learning_hub.models  # noqa: F401
    import ai_learning_hub.api.models  # Import API-specific models

    # Register the API blueprint for mobile apps
    from ai_learning_hub.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Register the API web blueprint for documentation and status pages
    from ai_learning_hub.api.views import api_web_bp
    app.register_blueprint(api_web_bp)
    
    # Register the pronunciation coach blueprint
    from ai_learning_hub.pronunciation_routes import pronunciation_bp
    app.register_blueprint(pronunciation_bp)
    
    # Create tables
    db.create_all()