import datetime
from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.dashboard import dashboard_bp
from app.models import db, Prompt, Category, ActivityLog, CopyHistory

# ==============================================================================
# PromptForge - Dashboard Routes
# ==============================================================================
# Aggregates system metrics, recent activity feeds, copy histories, and top categories
# to construct a Notion/Linear-inspired productivity dashboard.
# ==============================================================================

@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Renders main dashboard overview with metric cards, recent prompts, copy history,
    and user activity timeline.
    """
    user_id = current_user.id

    # Metric 1: Total Prompts owned by user
    total_prompts = Prompt.query.filter_by(user_id=user_id, status='active').count()

    # Metric 2: Favorite Prompts count
    favorite_count = Prompt.query.filter_by(user_id=user_id, status='active', is_favorite=True).count()

    # Metric 3: Total Custom & System Categories available
    categories_count = Category.query.filter(
        (Category.is_system == True) | (Category.user_id == user_id)
    ).count()

    # Metric 4: Most Used Category (category with highest number of prompts created by user)
    most_used_category_query = db.session.query(
        Category.name, Category.color, func.count(Prompt.id).label('prompt_count')
    ).join(Prompt, Prompt.category_id == Category.id)\
     .filter(Prompt.user_id == user_id, Prompt.status == 'active')\
     .group_by(Category.id)\
     .order_by(func.count(Prompt.id).desc()).first()

    most_used_category = {
        'name': most_used_category_query[0] if most_used_category_query else 'None Yet',
        'color': most_used_category_query[1] if most_used_category_query else '#64748B',
        'count': most_used_category_query[2] if most_used_category_query else 0
    }

    # Widget 1: Recent Prompts (5 most recently created active prompts)
    recent_prompts = Prompt.query.filter_by(user_id=user_id, status='active')\
        .order_by(Prompt.created_at.desc()).limit(5).all()

    # Widget 2: Recently Copied Prompts (5 most recently copied prompts)
    recently_copied = Prompt.query.filter(
        Prompt.user_id == user_id,
        Prompt.status == 'active',
        Prompt.last_copied_at.isnot(None)
    ).order_by(Prompt.last_copied_at.desc()).limit(5).all()

    # Widget 3: Activity Timeline (10 most recent user actions)
    activity_timeline = ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.created_at.desc()).limit(10).all()

    # Metric 5: Weekly Copy Statistics (Copies performed in the last 7 days)
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    weekly_copies = CopyHistory.query.filter(
        CopyHistory.user_id == user_id,
        CopyHistory.copied_at >= seven_days_ago
    ).count()

    return render_template(
        'dashboard/index.html',
        total_prompts=total_prompts,
        favorite_count=favorite_count,
        categories_count=categories_count,
        most_used_category=most_used_category,
        recent_prompts=recent_prompts,
        recently_copied=recently_copied,
        activity_timeline=activity_timeline,
        weekly_copies=weekly_copies
    )
