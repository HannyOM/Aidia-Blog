import os
from dotenv import load_dotenv 
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore


load_dotenv()

# Instantiate extensions (without app object).
db = SQLAlchemy()                   
migrate = Migrate()


class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SECURITY_TOKEN_JSON_KEY = "fs_token"
    REMEMBER_COOKIE_SAMESITE = "lax"
    SESSION_COOKIE_SAMESITE = "lax"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SECURITY_REGISTERABLE = True
    SECURITY_EMAIL_SUBJECT_REGISTER = os.environ.get("SECURITY_EMAIL_SUBJECT_REGISTER")
    SECURITY_POST_REGISTER_VIEW = "blog.check_email"
    SECURITY_MSG_CONFIRM_REGISTRATION = (
        "We've emailed a verification link to %(email)s. Please check your inbox"
        " - and your spam folder just in case - then click the link to confirm your account.",
        "success",
    )
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_CONFIRMABLE = True
    SECURITY_SEND_REGISTER = True
    SECURITY_EMAIL_SENDER = os.environ.get("RESEND_FROM_EMAIL")
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
    RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL")
    MAILBOXLAYER_ACCESS_KEY = os.environ.get("MAILBOXLAYER_ACCESS_KEY")
    MAILBOXLAYER_API_URL = os.environ.get("MAILBOXLAYER_API_URL")


class DevelopmentConfig(ProductionConfig):
    DEBUG = True
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


# Application factory
def create_app(config_class=None, test_config=None):
    app = Flask(__name__)
    
    # Handle backward compatibility: if config_class is a dict, treat it as test_config
    if isinstance(config_class, dict):
        test_config = config_class
        config_class = None
    
    if config_class:
        app.config.from_object(config_class)
    else:
        is_prod = os.environ.get("FLASK_ENV") == "production"
        app.config.from_object(ProductionConfig if is_prod else DevelopmentConfig)
    
    # Override with test_config if it exists.
    if test_config is not None:
        app.config.update(test_config)

    # Initialize extensions (with app object).
    db.init_app(app)
    migrate.init_app(app, db)

    from .email_service import email_service
    email_service.init_app(app)

    # Import models to create tables in database.
    from .models import User, Role, Post, Suggestion, SuggestionVote

    # Setup Flask-Security
    from .email_service import ResendMailUtil
    from .forms import VerifiedRegisterForm
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(
        app,
        user_datastore,
        mail_util_cls=ResendMailUtil,
        register_form=VerifiedRegisterForm,
    )

    # Fix for Flask-Security 5.x: @auth_required() doesn't recognize password
    # authentication as session auth. This sets fs_authn_via in each request
    # if the user is authenticated via session.
    from flask import request, session
    from flask_login import current_user
    from flask_security.utils import get_request_attr, set_request_attr

    @app.before_request
    def set_fs_authn_via():
        if current_user.is_authenticated:
            existing = get_request_attr("fs_authn_via")
            if not existing:
                set_request_attr("fs_authn_via", "session")

    @app.context_processor
    def inject_user():
        return {"user": current_user}

    # Automatically assign registered user with "editor" role.
    from .roles import setup_roles_signals
    setup_roles_signals(app)

    # Import blueprints
    from . import blog
    
    # Register blueprints
    app.register_blueprint(blog.bp)
    app.add_url_rule("/",
                     endpoint="index")

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 503

    @app.errorhandler(500)
    def handle_500(error):
        from flask import flash
        flash("An error occurred. Please try again later.", "error")
        return render_template("blog/index.html"), 500

    return app