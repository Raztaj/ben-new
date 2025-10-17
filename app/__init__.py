# --- START OF FILE app/__init__.py ---

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize extensions without an app context
db = SQLAlchemy()
login_manager = LoginManager()

# This is the crucial callback required by Flask-Login.
# It tells the extension how to find a specific user from the ID stored
# in their session cookie.
@login_manager.user_loader
def load_user(user_id):
    # We must import the model here to avoid circular dependencies
    from .models import User
    return User.query.get(int(user_id))


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # --- Configuration ---
    # Use environment variables with sensible defaults for development
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'postgresql://beneficiary_user:password@localhost/beneficiary_db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
    )

    # If behind a proxy like Nginx, this helps get the correct protocol (http/https)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # --- Initialize Extensions with the App Instance ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- Configure Flask-Login ---
    # Redirect users to this route if they try to access a protected page
    login_manager.login_view = 'routes.login' # Note the 'routes.' blueprint prefix
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # The app_context is essential for database operations and imports
    with app.app_context():
        # --- Import parts of our application ---
        from . import routes  # Import routes
        from . import models  # Import models

        # --- Register Blueprints ---
        app.register_blueprint(routes.bp)

        # --- Create Database Tables ---
        # This will create tables for any models that don't exist yet
        db.create_all()

        # --- Seed Database with Default Users (only if they don't exist) ---
        # Security Note: Default credentials should only be used for development/demo
        # In production, use environment variables or create admin via CLI
        if not models.User.query.filter_by(username='admin').first():
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin = models.User(username='admin', full_name='System Administrator', role='admin')
            admin.set_password(admin_password)
            db.session.add(admin)

        if not models.User.query.filter_by(username='user').first():
            user_password = os.environ.get('USER_PASSWORD', 'user123')
            user = models.User(username='user', full_name='Regular User', role='user')
            user.set_password(user_password)
            db.session.add(user)

        db.session.commit()

    return app
