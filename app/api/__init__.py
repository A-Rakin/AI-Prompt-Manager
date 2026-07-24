from flask import Blueprint

# ==============================================================================
# PromptForge - REST API Blueprint Initialization
# ==============================================================================
# REST API endpoints for external tools, mobile apps, or browser extension integrations.
# ==============================================================================

api_bp = Blueprint('api', __name__)

from app.api import routes
