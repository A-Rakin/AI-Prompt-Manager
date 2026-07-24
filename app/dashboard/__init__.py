from flask import Blueprint

# ==============================================================================
# PromptForge - Dashboard Blueprint Initialization
# ==============================================================================
# Dashboard blueprint renders summary analytics, recent prompts, activity timeline,
# and key productivity statistics.
# ==============================================================================

dashboard_bp = Blueprint('dashboard', __name__)

from app.dashboard import routes
