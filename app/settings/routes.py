from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.settings import settings_bp
from app.models import db
from app.utils.helpers import log_activity

# ==============================================================================
# PromptForge - User Settings & UI Preference Routes
# ==============================================================================
# Manages user UI customization settings (Theme mode, Accent color, Font size,
# Compact mode, and Animations).
# ==============================================================================

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Renders UI theme customization form and saves settings to database.
    """
    if request.method == 'POST':
        theme_preference = request.form.get('theme_preference', 'dark')
        accent_color = request.form.get('accent_color', '#6366F1')
        font_size = request.form.get('font_size', 'medium')
        compact_mode = 'compact_mode' in request.form
        animations_enabled = 'animations_enabled' in request.form

        # Save settings to active user record
        current_user.theme_preference = theme_preference
        current_user.accent_color = accent_color
        current_user.font_size = font_size
        current_user.compact_mode = compact_mode
        current_user.animations_enabled = animations_enabled

        db.session.commit()
        log_activity(current_user.id, 'settings_updated', 'Updated UI theme and appearance settings')

        flash("Settings saved successfully!", "success")
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html')
