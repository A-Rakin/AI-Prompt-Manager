from flask import Blueprint

# ==============================================================================
# PromptForge - Analytics Blueprint Initialization
# ==============================================================================
# Blueprint serving productivity charts and JSON datasets for Chart.js.
# ==============================================================================

analytics_bp = Blueprint('analytics', __name__)

from app.analytics import routes
