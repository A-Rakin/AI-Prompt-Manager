from flask import Blueprint

# ==============================================================================
# PromptForge - Categories Blueprint Initialization
# ==============================================================================
# Blueprint managing custom user categories and system domain categories.
# ==============================================================================

categories_bp = Blueprint('categories', __name__)

from app.categories import routes
