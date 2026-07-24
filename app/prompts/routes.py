import json
import csv
import io
from flask import render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import login_required, current_user
from app.prompts import prompts_bp
from app.models import db, Prompt, Category, Tag, Collection, prompt_tags
from app.forms.prompt_forms import PromptForm
from app.utils.helpers import log_activity, record_copy_event

# ==============================================================================
# PromptForge - Prompts Management Routes
# ==============================================================================
# Core engine managing Prompt creation, editing, soft deletion (archiving),
# live multi-filter searching, copy tracking, tag associations, and import/export.
# ==============================================================================

@prompts_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Lists active prompts with support for live search, pagination, category filtering,
    platform filtering, tag filtering, and custom sorting.
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    platform = request.args.get('platform', '').strip()
    tag_name = request.args.get('tag', '').strip()
    sort_by = request.args.get('sort', 'created_desc')

    # Base query restricted to active prompts owned by current logged-in user
    query = Prompt.query.filter_by(user_id=current_user.id, status='active')

    # Apply live text search across Title, Description, and Prompt Content
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            (Prompt.title.ilike(search_filter)) |
            (Prompt.description.ilike(search_filter)) |
            (Prompt.content.ilike(search_filter))
        )

    # Filter by Category
    if category_id:
        query = query.filter_by(category_id=category_id)

    # Filter by AI Platform (ChatGPT, Claude, Gemini, etc.)
    if platform:
        query = query.filter_by(platform=platform)

    # Filter by Tag name via junction table join
    if tag_name:
        query = query.join(Prompt.tags).filter(Tag.name == tag_name)

    # Sorting logic (Pinned prompts always appear first)
    if sort_by == 'title_asc':
        query = query.order_by(Prompt.is_pinned.desc(), Prompt.title.asc())
    elif sort_by == 'copies_desc':
        query = query.order_by(Prompt.is_pinned.desc(), Prompt.copy_count.desc())
    elif sort_by == 'created_asc':
        query = query.order_by(Prompt.is_pinned.desc(), Prompt.created_at.asc())
    else:  # 'created_desc' (Default)
        query = query.order_by(Prompt.is_pinned.desc(), Prompt.created_at.desc())

    # Paginate results (12 prompts per page)
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    prompts = pagination.items

    # Fetch user categories and popular tags for sidebar filters
    categories = Category.query.filter(
        (Category.is_system == True) | (Category.user_id == current_user.id)
    ).all()

    tags = Tag.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'prompts/list.html',
        prompts=prompts,
        pagination=pagination,
        categories=categories,
        tags=tags,
        selected_category=category_id,
        selected_platform=platform,
        selected_tag=tag_name,
        search_query=search_query,
        sort_by=sort_by
    )


@prompts_bp.route('/favorites', methods=['GET'])
@login_required
def favorites():
    """
    Dedicated view displaying favorited prompts for quick access.
    """
    prompts = Prompt.query.filter_by(
        user_id=current_user.id,
        status='active',
        is_favorite=True
    ).order_by(Prompt.is_pinned.desc(), Prompt.updated_at.desc()).all()

    return render_template('prompts/favorites.html', prompts=prompts)


@prompts_bp.route('/archived', methods=['GET'])
@login_required
def archived():
    """
    Displays soft-deleted (archived) prompts with options to restore or permanently delete.
    """
    prompts = Prompt.query.filter_by(
        user_id=current_user.id,
        status='archived'
    ).order_by(Prompt.updated_at.desc()).all()

    return render_template('prompts/archived.html', prompts=prompts)


@prompts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """
    Renders prompt creation form and handles database insertion.
    """
    form = PromptForm()

    # Populate category choices dynamically (system categories + user categories)
    user_categories = Category.query.filter(
        (Category.is_system == True) | (Category.user_id == current_user.id)
    ).order_by(Category.name.asc()).all()

    form.category_id.choices = [(0, 'Select Category (Optional)')] + [
        (cat.id, cat.name) for cat in user_categories
    ]

    if form.validate_on_submit():
        category_id = form.category_id.data if form.category_id.data != 0 else None

        prompt = Prompt(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
            content=form.content.data.strip(),
            platform=form.platform.data,
            category_id=category_id,
            language=form.language.data,
            difficulty=form.difficulty.data,
            is_pinned=form.is_pinned.data,
            is_favorite=form.is_favorite.data,
            user_id=current_user.id
        )

        db.session.add(prompt)

        # Process comma-separated tags input
        tags_str = form.tags_input.data
        if tags_str:
            raw_tags = [t.strip().lower() for t in tags_str.split(',') if t.strip()]
            for tag_name in raw_tags:
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                prompt.tags.append(tag)

        db.session.commit()

        log_activity(current_user.id, 'created', f"Created prompt '{prompt.title}'", prompt.id)
        flash(f"Prompt '{prompt.title}' created successfully!", "success")
        return redirect(url_for('prompts.detail', prompt_id=prompt.id))

    return render_template('prompts/form.html', form=form, title="Create New Prompt")


@prompts_bp.route('/<int:prompt_id>', methods=['GET'])
@login_required
def detail(prompt_id):
    """
    Renders detailed view of a single prompt.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    return render_template('prompts/detail.html', prompt=prompt)


@prompts_bp.route('/<int:prompt_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(prompt_id):
    """
    Renders prompt editing form pre-filled with existing data and updates records.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    form = PromptForm(obj=prompt)

    user_categories = Category.query.filter(
        (Category.is_system == True) | (Category.user_id == current_user.id)
    ).order_by(Category.name.asc()).all()

    form.category_id.choices = [(0, 'Select Category (Optional)')] + [
        (cat.id, cat.name) for cat in user_categories
    ]

    if request.method == 'GET':
        form.category_id.data = prompt.category_id if prompt.category_id else 0
        form.tags_input.data = ", ".join([t.name for t in prompt.tags])

    if form.validate_on_submit():
        prompt.title = form.title.data.strip()
        prompt.description = form.description.data.strip() if form.description.data else ""
        prompt.content = form.content.data.strip()
        prompt.platform = form.platform.data
        prompt.category_id = form.category_id.data if form.category_id.data != 0 else None
        prompt.language = form.language.data
        prompt.difficulty = form.difficulty.data
        prompt.is_pinned = form.is_pinned.data
        prompt.is_favorite = form.is_favorite.data

        # Re-associate tags
        prompt.tags.clear()
        tags_str = form.tags_input.data
        if tags_str:
            raw_tags = [t.strip().lower() for t in tags_str.split(',') if t.strip()]
            for tag_name in raw_tags:
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                prompt.tags.append(tag)

        db.session.commit()
        log_activity(current_user.id, 'edited', f"Updated prompt '{prompt.title}'", prompt.id)
        flash(f"Prompt '{prompt.title}' updated successfully!", "success")
        return redirect(url_for('prompts.detail', prompt_id=prompt.id))

    return render_template('prompts/form.html', form=form, title="Edit Prompt", prompt=prompt)


@prompts_bp.route('/<int:prompt_id>/copy', methods=['POST'])
@login_required
def copy_prompt(prompt_id):
    """
    AJAX endpoint called when user clicks 'Copy Prompt'.
    Increments copy count, updates last_copied_at, and records copy history.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first()
    if not prompt:
        return jsonify({'success': False, 'message': 'Prompt not found'}), 404

    success = record_copy_event(current_user.id, prompt)
    if success:
        return jsonify({
            'success': True,
            'copy_count': prompt.copy_count,
            'message': 'Prompt content copied to clipboard!'
        })
    return jsonify({'success': False, 'message': 'Failed to record copy action'}), 500


@prompts_bp.route('/<int:prompt_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(prompt_id):
    """
    AJAX endpoint to toggle favorite status on/off.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    prompt.is_favorite = not prompt.is_favorite
    db.session.commit()

    action_text = "favorited" if prompt.is_favorite else "unfavorited"
    log_activity(current_user.id, action_text, f"{action_text.capitalize()} prompt '{prompt.title}'", prompt.id)

    return jsonify({
        'success': True,
        'is_favorite': prompt.is_favorite,
        'message': f"Prompt {'added to' if prompt.is_favorite else 'removed from'} favorites."
    })


@prompts_bp.route('/<int:prompt_id>/pin', methods=['POST'])
@login_required
def toggle_pin(prompt_id):
    """
    AJAX endpoint to toggle pinned status on/off.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    prompt.is_pinned = not prompt.is_pinned
    db.session.commit()

    action_text = "pinned" if prompt.is_pinned else "unpinned"
    log_activity(current_user.id, action_text, f"{action_text.capitalize()} prompt '{prompt.title}'", prompt.id)

    return jsonify({
        'success': True,
        'is_pinned': prompt.is_pinned,
        'message': f"Prompt {'pinned to top' if prompt.is_pinned else 'unpinned'}."
    })


@prompts_bp.route('/<int:prompt_id>/archive', methods=['POST'])
@login_required
def archive_prompt(prompt_id):
    """
    Toggles soft delete status ('active' <-> 'archived').
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    if prompt.status == 'active':
        prompt.status = 'archived'
        msg = f"Prompt '{prompt.title}' moved to archive."
        act = 'archived'
    else:
        prompt.status = 'active'
        msg = f"Prompt '{prompt.title}' restored from archive."
        act = 'restored'

    db.session.commit()
    log_activity(current_user.id, act, msg, prompt.id)
    flash(msg, "info")
    return redirect(url_for('prompts.index'))


@prompts_bp.route('/<int:prompt_id>/duplicate', methods=['POST'])
@login_required
def duplicate(prompt_id):
    """
    Duplicates an existing prompt, creating a copy with title prefix 'Copy of...'.
    """
    source_prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    
    new_prompt = Prompt(
        title=f"Copy of {source_prompt.title}",
        description=source_prompt.description,
        content=source_prompt.content,
        platform=source_prompt.platform,
        category_id=source_prompt.category_id,
        language=source_prompt.language,
        difficulty=source_prompt.difficulty,
        user_id=current_user.id,
        status='active'
    )

    # Copy tags
    for tag in source_prompt.tags:
        new_prompt.tags.append(tag)

    db.session.add(new_prompt)
    db.session.commit()

    log_activity(current_user.id, 'duplicated', f"Duplicated prompt '{source_prompt.title}'", new_prompt.id)
    flash(f"Duplicated '{source_prompt.title}' as '{new_prompt.title}'!", "success")
    return redirect(url_for('prompts.detail', prompt_id=new_prompt.id))


@prompts_bp.route('/<int:prompt_id>/delete', methods=['POST'])
@login_required
def hard_delete(prompt_id):
    """
    Permanently deletes a prompt from the database.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()
    title = prompt.title
    db.session.delete(prompt)
    db.session.commit()

    log_activity(current_user.id, 'deleted', f"Permanently deleted prompt '{title}'")
    flash(f"Prompt '{title}' permanently deleted.", "warning")
    return redirect(url_for('prompts.index'))


@prompts_bp.route('/export', methods=['GET'])
@login_required
def export_prompts():
    """
    Exports all active user prompts into downloadable JSON or CSV files.
    """
    fmt = request.args.get('format', 'json').lower()
    prompts = Prompt.query.filter_by(user_id=current_user.id, status='active').all()

    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Title', 'Description', 'Content', 'Platform', 'Category', 'Tags', 'Language', 'Difficulty', 'Copy Count'])
        
        for p in prompts:
            tags_str = ", ".join([t.name for t in p.tags])
            cat_name = p.category.name if p.category else ''
            writer.writerow([p.title, p.description, p.content, p.platform, cat_name, tags_str, p.language, p.difficulty, p.copy_count])
        
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers["Content-Disposition"] = "attachment; filename=promptforge_export.csv"
        return response

    else:  # JSON format (Default)
        export_data = [p.to_dict() for p in prompts]
        response = Response(json.dumps(export_data, indent=2), mimetype='application/json')
        response.headers["Content-Disposition"] = "attachment; filename=promptforge_export.json"
        return response


@prompts_bp.route('/import', methods=['POST'])
@login_required
def import_prompts():
    """
    Imports prompts from an uploaded JSON file.
    """
    if 'file' not in request.files:
        flash("No file selected for import.", "danger")
        return redirect(url_for('prompts.index'))

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.json'):
        flash("Invalid file format. Please upload a valid JSON file.", "danger")
        return redirect(url_for('prompts.index'))

    try:
        data = json.load(file)
        imported_count = 0

        for item in data:
            if 'title' in item and 'content' in item:
                prompt = Prompt(
                    title=item.get('title', 'Imported Prompt').strip(),
                    description=item.get('description', ''),
                    content=item.get('content', ''),
                    platform=item.get('platform', 'ChatGPT'),
                    language=item.get('language', 'English'),
                    difficulty=item.get('difficulty', 'Intermediate'),
                    user_id=current_user.id
                )
                db.session.add(prompt)
                imported_count += 1

        db.session.commit()
        log_activity(current_user.id, 'imported', f"Imported {imported_count} prompts from JSON file")
        flash(f"Successfully imported {imported_count} prompts!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error parsing import JSON file: {str(e)}", "danger")

    return redirect(url_for('prompts.index'))
