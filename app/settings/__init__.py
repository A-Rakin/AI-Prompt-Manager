from flask import Blueprint

# ==============================================================================
# PromptForge - Settings Blueprint Initialization
# ==============================================================================
# Blueprint managing user UI customizations (Dark/Light mode, Accent color, Font size, Animations).
# ==============================================================================

settings_bp = Blueprint('settings', __name__)

from app.settings import routes
