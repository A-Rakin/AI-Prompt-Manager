import datetime
from flask import render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.analytics import analytics_bp
from app.models import db, Prompt, Category, CopyHistory

# ==============================================================================
# PromptForge - Analytics & Reporting Routes
# ==============================================================================
# Computes productivity analytics, platform breakdown statistics, favorite ratios,
# and copy velocity history for Chart.js rendering.
# ==============================================================================

@analytics_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Renders analytics page containing Chart.js visual graphs.
    """
    return render_template('analytics/index.html')


@analytics_bp.route('/data', methods=['GET'])
@login_required
def get_chart_data():
    """
    JSON API endpoint returning data objects for Chart.js canvas renderings.

    Charts Provided:
    1. Prompts Created Per Month (Line Chart)
    2. Most Used Categories Breakdown (Bar Chart)
    3. Favorite Percentage (Pie Chart)
    4. Platform Usage Distribution (Doughnut Chart)
    5. Copy Statistics (Line Chart)
    """
    user_id = current_user.id

    # --------------------------------------------------------------------------
    # Chart 1: Platform Usage Distribution
    # --------------------------------------------------------------------------
    platform_counts = db.session.query(
        Prompt.platform, func.count(Prompt.id)
    ).filter(Prompt.user_id == user_id, Prompt.status == 'active')\
     .group_by(Prompt.platform).all()

    platform_labels = [p[0] for p in platform_counts] or ['No Prompts Yet']
    platform_data = [p[1] for p in platform_counts] or [0]

    # --------------------------------------------------------------------------
    # Chart 2: Category Distribution
    # --------------------------------------------------------------------------
    category_counts = db.session.query(
        Category.name, func.count(Prompt.id)
    ).join(Prompt, Prompt.category_id == Category.id)\
     .filter(Prompt.user_id == user_id, Prompt.status == 'active')\
     .group_by(Category.id).all()

    cat_labels = [c[0] for c in category_counts] or ['Uncategorized']
    cat_data = [c[1] for c in category_counts] or [0]

    # --------------------------------------------------------------------------
    # Chart 3: Favorite Percentage
    # --------------------------------------------------------------------------
    fav_count = Prompt.query.filter_by(user_id=user_id, status='active', is_favorite=True).count()
    non_fav_count = Prompt.query.filter_by(user_id=user_id, status='active', is_favorite=False).count()

    # --------------------------------------------------------------------------
    # Chart 4: Prompts Created Per Month (Last 6 Months)
    # --------------------------------------------------------------------------
    monthly_labels = []
    monthly_data = []

    today = datetime.date.today()
    for i in range(5, -1, -1):
        # Calculate start and end of month for last 6 months
        first_day_of_month = (today.replace(day=1) - datetime.timedelta(days=i*28)).replace(day=1)
        if first_day_of_month.month == 12:
            last_day_of_month = first_day_of_month.replace(year=first_day_of_month.year + 1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            last_day_of_month = first_day_of_month.replace(month=first_day_of_month.month + 1, day=1) - datetime.timedelta(days=1)

        month_name = first_day_of_month.strftime("%b %Y")
        count = Prompt.query.filter(
            Prompt.user_id == user_id,
            Prompt.created_at >= first_day_of_month,
            Prompt.created_at <= datetime.datetime.combine(last_day_of_month, datetime.time.max)
        ).count()

        monthly_labels.append(month_name)
        monthly_data.append(count)

    # --------------------------------------------------------------------------
    # Chart 5: Copy Velocity (Last 7 Days)
    # --------------------------------------------------------------------------
    copy_labels = []
    copy_data = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)

        count = CopyHistory.query.filter(
            CopyHistory.user_id == user_id,
            CopyHistory.copied_at >= day_start,
            CopyHistory.copied_at <= day_end
        ).count()

        copy_labels.append(day.strftime("%a"))
        copy_data.append(count)

    return jsonify({
        'platforms': {
            'labels': platform_labels,
            'data': platform_data
        },
        'categories': {
            'labels': cat_labels,
            'data': cat_data
        },
        'favorites': {
            'labels': ['Favorited', 'Standard'],
            'data': [fav_count, non_fav_count]
        },
        'monthly': {
            'labels': monthly_labels,
            'data': monthly_data
        },
        'copies': {
            'labels': copy_labels,
            'data': copy_data
        }
    })
