import re
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.categories import categories_bp
from app.models import db, Category, Prompt
from app.forms.prompt_forms import CategoryForm
from app.utils.helpers import log_activity

# ==============================================================================
# PromptForge - Categories Routes
# ==============================================================================
# Manages system default categories and user-created custom categories.
# ==============================================================================

def slugify(text):
    """Utility helper converting strings into URL-safe slugs (e.g. 'Data Science' -> 'data-science')."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)

@categories_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Lists system and custom categories with prompt statistics per category.
    Allows users to create new custom categories.
    """
    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        slug = slugify(name)

        # Check if category with same slug already exists for user
        existing = Category.query.filter_by(slug=slug, user_id=current_user.id).first()
        if existing:
            flash(f"A category named '{name}' already exists.", "warning")
        else:
            category = Category(
                name=name,
                slug=slug,
                color=form.color.data,
                icon=form.icon.data.strip() if form.icon.data else "fa-folder",
                is_system=False,
                user_id=current_user.id
            )
            db.session.add(category)
            db.session.commit()

            log_activity(current_user.id, 'category_created', f"Created custom category '{name}'")
            flash(f"Category '{name}' created successfully!", "success")
            return redirect(url_for('categories.index'))

    # Fetch all categories available to user (System categories + user custom categories)
    categories = Category.query.filter(
        (Category.is_system == True) | (Category.user_id == current_user.id)
    ).order_by(Category.name.asc()).all()

    # Calculate prompt counts per category for active prompts owned by current user
    category_stats = []
    for cat in categories:
        count = Prompt.query.filter_by(
            user_id=current_user.id,
            category_id=cat.id,
            status='active'
        ).count()
        category_stats.append({
            'category': cat,
            'prompt_count': count
        })

    return render_template('categories/list.html', form=form, category_stats=category_stats)


@categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete(category_id):
    """
    Deletes a custom user category. System categories cannot be deleted.
    """
    category = Category.query.get_or_404(category_id)

    if category.is_system or category.user_id != current_user.id:
        flash("You cannot delete default system categories.", "danger")
        return redirect(url_for('categories.index'))

    name = category.name
    db.session.delete(category)
    db.session.commit()

    log_activity(current_user.id, 'category_deleted', f"Deleted custom category '{name}'")
    flash(f"Category '{name}' removed successfully.", "warning")
    return redirect(url_for('categories.index'))
