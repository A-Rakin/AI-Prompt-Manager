from app.models import db, Category

# ==============================================================================
# PromptForge - Initial Database Seeder
# ==============================================================================
# Data seeding is the process of populating a database with initial default data
# required for the application to function out-of-the-box (such as standard categories).
# ==============================================================================

DEFAULT_CATEGORIES = [
    {"name": "Programming", "slug": "programming", "color": "#3B82F6", "icon": "fa-code"},
    {"name": "Writing", "slug": "writing", "color": "#EC4899", "icon": "fa-pen-nib"},
    {"name": "Marketing", "slug": "marketing", "color": "#F59E0B", "icon": "fa-bullhorn"},
    {"name": "Design", "slug": "design", "color": "#8B5CF6", "icon": "fa-palette"},
    {"name": "Education", "slug": "education", "color": "#10B981", "icon": "fa-graduation-cap"},
    {"name": "Research", "slug": "research", "color": "#06B6D4", "icon": "fa-microscope"},
    {"name": "Business", "slug": "business", "color": "#6366F1", "icon": "fa-briefcase"},
    {"name": "Productivity", "slug": "productivity", "color": "#14B8A6", "icon": "fa-check-double"},
]

def seed_default_categories():
    """
    Populates default system categories if they do not exist in the database yet.
    """
    try:
        created_count = 0
        for cat_data in DEFAULT_CATEGORIES:
            existing = Category.query.filter_by(slug=cat_data["slug"], is_system=True).first()
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                    is_system=True
                )
                db.session.add(category)
                created_count += 1
        
        if created_count > 0:
            db.session.commit()
            print(f"Successfully seeded {created_count} default categories.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding default categories: {e}")
