import os
import logging
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.update(
        SECRET_KEY=os.environ.get("SESSION_SECRET", "dev_key"),
        SQLALCHEMY_DATABASE_URI="postgresql://postgres:iUOHaXkJKuymTIvHWaFvxRaTLZgJKwcz@turntable.proxy.rlwy.net:17740/railway",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_pre_ping": True,
            "pool_recycle": 300,
        },
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_PORT=os.environ.get("MAIL_PORT", 587),
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER", "noreply@forjafn.com"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
        UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads"),
    )
    
    # Fix for proper URLs with https
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create database tables
    with app.app_context():
        from models import User, Role, Course, Lesson, Quiz, Question, Answer, Forum, ForumCategory, ForumPost, ForumReply, Payment, UserAchievement, Achievement
        db.create_all()
        
        # Create initial roles and admin if they don't exist
        from utils import create_default_roles, create_admin_user, create_forum_categories
        create_default_roles()
        create_admin_user()
        create_forum_categories()
        
        logger.info("Database tables created and initialized")
    
    # Register blueprints
    from auth import auth_bp, init_auth
    from routes import main_bp
    from forum import forum_bp
    from payment import payment_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(forum_bp, url_prefix='/forum')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    
    # Initialize auth module
    init_auth(app)
    
    # Register error handlers
    from utils import handle_403, handle_404, handle_500
    app.register_error_handler(403, handle_403)
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)
    
    return app
