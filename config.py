import os
from datetime import timedelta

# ==============================================================================
# PromptForge - Application Configuration Module
# ==============================================================================
# This module defines configuration classes for different execution environments
# (Development, Testing, and Production).
#
# Key Concepts Explained:
# 1. Environment Variables: Values stored outside the application code (e.g. in OS or .env file).
#    This keeps secret credentials (like database passwords or API keys) safe and configurable.
# 2. Secret Key: A cryptographic key used by Flask to encrypt session cookies and sign CSRF tokens.
# 3. Database URI (Uniform Resource Identifier): The connection string specifying the database type,
#    username, password, host, port, and database name.
#    - SQLite: File-based database ideal for local development (no server setup needed).
#    - PostgreSQL: Enterprise-grade relational database ideal for production deployments.
# 4. CSRF (Cross-Site Request Forgery): An attack where unauthorized commands are submitted from a user
#    that the web application trusts. CSRF protection prevents this by validating anti-forgery tokens.
# ==============================================================================

# Determine base directory of the project for database file storage
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class with default settings shared across all environments.
    """
    # Secret key used for signing cookies and protecting against CSRF attacks.
    # In production, this MUST be set via the SECRET_KEY environment variable.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'promptforge-super-secret-dev-key-change-in-production')

    # Turn off SQLAlchemy event system modification tracking to save system memory.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session lifetime settings: keeps users logged in for 7 days if "Remember Me" is checked
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Enable Flask-WTF CSRF Protection globally across forms and AJAX requests
    WTF_CSRF_ENABLED = True

    # Application details used across header footers and templates
    APP_NAME = "PromptForge"
    APP_TAGLINE = "Elevate Your AI Workflow with Precision Prompts"

class DevelopmentConfig(Config):
    """
    Development configuration enabling debugging and SQLite database file storage.
    """
    DEBUG = True
    # Default to SQLite local database file located in the root project folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'promptforge_dev.db')

class ProductionConfig(Config):
    """
    Production configuration ensuring high security and PostgreSQL database connectivity.
    """
    DEBUG = False

    # PostgreSQL database string (e.g. postgresql://user:password@localhost:5432/promptforge_db)
    # Render/Heroku sometimes pass 'postgres://', which SQLAlchemy 2.0 requires to be 'postgresql://'
    raw_db_url = os.environ.get('DATABASE_URL', '')
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = raw_db_url or 'sqlite:///' + os.path.join(BASE_DIR, 'promptforge_prod.db')

class TestingConfig(Config):
    """
    Testing configuration utilizing an in-memory SQLite database for lightning-fast test execution.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Mapping environment names to their respective configuration classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
