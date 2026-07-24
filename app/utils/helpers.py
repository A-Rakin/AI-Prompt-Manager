import datetime
from app.models import db, ActivityLog, CopyHistory

# ==============================================================================
# PromptForge - Utility Helpers Module
# ==============================================================================
# This module provides reusable helper functions for logging user activities,
# recording prompt copying events, and formatting human-friendly relative time strings.
#
# Key Concepts Explained:
# 1. Audit Logging: Recording user actions (create, edit, delete, copy) creates an audit trail
#    that powers activity timelines and analytics.
# 2. Relative Time Formatter: Converting raw UTC ISO timestamps (like 2026-07-24T17:34:00Z)
#    into natural human phrases (like "5 minutes ago" or "Yesterday").
# ==============================================================================

def log_activity(user_id, action, details, prompt_id=None):
    """
    Creates an ActivityLog entry to track user interactions within PromptForge.

    Parameters:
    - user_id (int): ID of the active user performing the action.
    - action (str): Short descriptor of the action ('created', 'copied', 'favorited', etc.).
    - details (str): Descriptive message for timeline display.
    - prompt_id (int, optional): ID of the affected prompt, if applicable.
    """
    try:
        log_entry = ActivityLog(
            user_id=user_id,
            prompt_id=prompt_id,
            action=action,
            details=details,
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")


def record_copy_event(user_id, prompt):
    """
    Executes all database operations needed when a user copies a prompt:
    1. Increments prompt's copy_count.
    2. Updates last_copied_at timestamp.
    3. Adds an entry to CopyHistory table.
    4. Creates an ActivityLog entry.

    Parameters:
    - user_id (int): Active user ID copying the prompt.
    - prompt (Prompt): SQLAlchemy Prompt model instance.
    """
    try:
        # Increment total copy count for productivity analytics
        prompt.copy_count = (prompt.copy_count or 0) + 1
        prompt.last_copied_at = datetime.datetime.utcnow()

        # Add record to copy history table
        history_entry = CopyHistory(
            user_id=user_id,
            prompt_id=prompt.id,
            copied_at=datetime.datetime.utcnow()
        )
        db.session.add(history_entry)

        # Commit changes to update copy stats
        db.session.commit()

        # Create activity log entry for the user's activity timeline
        log_activity(
            user_id=user_id,
            action='copied',
            details=f"Copied prompt '{prompt.title}'",
            prompt_id=prompt.id
        )
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error recording copy event: {e}")
        return False


def format_relative_time(dt):
    """
    Converts a Python datetime object into a clean, human-readable relative time string.

    Example Outputs:
    - "Just now"
    - "5 mins ago"
    - "3 hours ago"
    - "Yesterday"
    - "Jul 24, 2026"
    """
    if not dt:
        return "Never"

    now = datetime.datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = int(seconds // 60)
        return f"{mins} min{'s' if mins > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 172800:
        return "Yesterday"
    else:
        days = int(seconds // 86400)
        if days < 30:
            return f"{days} days ago"
        return dt.strftime("%b %d, %Y")
