from flask import Blueprint

# ==============================================================================
# PromptForge - Authentication Blueprint Initialization
# ==============================================================================
# Blueprints isolate application features into self-contained modules.
# ==============================================================================

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
