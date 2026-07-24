from flask import Blueprint

# ==============================================================================
# PromptForge - Prompts Blueprint Initialization
# ==============================================================================
# Prompts blueprint handles core CRUD operations, live search, favorites,
# archiving, duplicating, copying, export, and import.
# ==============================================================================

prompts_bp = Blueprint('prompts', __name__)

from app.prompts import routes
