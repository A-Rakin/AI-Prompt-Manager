import os
from flask import Flask, render_template
from flask_login import LoginManager, AnonymousUserMixin
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config
from app.models import db, User
from app.utils.helpers import format_relative_time
from app.utils.seed import seed_default_categories

# ==============================================================================
# PromptForge - Application Factory Module
# ==============================================================================
# The Application Factory pattern (`create_app`) allows us to instantiate Flask
# applications dynamically with different configurations (e.g., Development, Testing, Production).
# This prevents global state pollution and makes automated testing seamless.
#
# Key Concepts Explained:
# 1. Application Factory: A function that creates and returns a configured Flask app instance.
# 2. Flask Blueprints: Modular components that group routes, templates, and static assets logically
#    (e.g., Auth Blueprint, Prompts Blueprint, API Blueprint).
# 3. Flask-Login: Manages user sessions. `login_manager.user_loader` fetches the current user from database by ID.
# 4. CSRFProtect: Protects HTML forms and AJAX endpoints against Cross-Site Request Forgery attacks.
# ==============================================================================

class AnonymousUser(AnonymousUserMixin):
    """Custom Anonymous User providing default theme preferences for unauthenticated visitors."""
    theme_preference = 'dark'
    accent_color = '#6366F1'

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please sign in to access PromptForge."
login_manager.login_message_category = "info"
login_manager.anonymous_user = AnonymousUser

migrate = Migrate()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback function that reloads the user object from the database
    using the user ID stored in the session cookie.
    """
    return db.session.get(User, int(user_id))


def create_app(config_name=None):
    """
    Constructs and configures the Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with the application instance
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register custom Jinja2 template filters
    @app.template_filter('relative_time')
    def relative_time_filter(dt):
        return format_relative_time(dt)

    @app.template_filter('escapejs')
    def escapejs_filter(val):
        if not val:
            return ""
        import json
        return json.dumps(str(val))[1:-1]

    # Context processor to inject global variables into all Jinja templates
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': app.config['APP_NAME'],
            'app_tagline': app.config['APP_TAGLINE']
        }

    # Register Modular Flask Blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.prompts import prompts_bp
    from app.categories import categories_bp
    from app.collections import collections_bp
    from app.settings import settings_bp
    from app.analytics import analytics_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prompts_bp, url_prefix='/prompts')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(collections_bp, url_prefix='/collections')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Register Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Auto-seed database tables and initial categories on start up
    with app.app_context():
        db.create_all()
        seed_default_categories()

    return app
