from flask import Blueprint

# ==============================================================================
# PromptForge - Collections Blueprint Initialization
# ==============================================================================
# Blueprint managing custom folder collections for drag-and-drop prompt organization.
# ==============================================================================

collections_bp = Blueprint('collections', __name__)

from app.collections import routes
