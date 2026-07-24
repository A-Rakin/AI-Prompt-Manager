from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.collections import collections_bp
from app.models import db, Collection, Prompt
from app.forms.prompt_forms import CollectionForm
from app.utils.helpers import log_activity

# ==============================================================================
# PromptForge - Collections (Folders) Routes
# ==============================================================================
# Enables users to group prompts into custom folders (e.g. Work, University, Research).
# Supports drag-and-drop prompt assignment.
# ==============================================================================

@collections_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Lists user's collection folders and provides form to create new collection folders.
    """
    form = CollectionForm()

    if form.validate_on_submit():
        collection = Collection(
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
            color=form.color.data,
            icon=form.icon.data.strip() if form.icon.data else "fa-folder-open",
            user_id=current_user.id
        )
        db.session.add(collection)
        db.session.commit()

        log_activity(current_user.id, 'collection_created', f"Created collection folder '{collection.name}'")
        flash(f"Collection '{collection.name}' created successfully!", "success")
        return redirect(url_for('collections.index'))

    collections = Collection.query.filter_by(user_id=current_user.id).order_by(Collection.created_at.desc()).all()
    user_prompts = Prompt.query.filter_by(user_id=current_user.id, status='active').all()

    return render_template('collections/list.html', form=form, collections=collections, user_prompts=user_prompts)


@collections_bp.route('/<int:collection_id>', methods=['GET'])
@login_required
def detail(collection_id):
    """
    Renders prompts contained within a specific collection folder.
    """
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    prompts = [p for p in collection.prompts if p.status == 'active']

    # All user active prompts for "Add Prompt to Collection" dropdown
    all_user_prompts = Prompt.query.filter_by(user_id=current_user.id, status='active').all()

    return render_template('collections/detail.html', collection=collection, prompts=prompts, all_user_prompts=all_user_prompts)


@collections_bp.route('/<int:collection_id>/add-prompt', methods=['POST'])
@login_required
def add_prompt(collection_id):
    """
    Adds a prompt into a collection folder (via form POST or Drag-and-Drop AJAX).
    """
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()

    prompt_id = request.form.get('prompt_id') or (request.json.get('prompt_id') if request.is_json else None)
    if not prompt_id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Missing prompt_id'}), 400
        flash("Please select a valid prompt.", "warning")
        return redirect(url_for('collections.detail', collection_id=collection.id))

    prompt = Prompt.query.filter_by(id=int(prompt_id), user_id=current_user.id).first_or_404()

    if prompt not in collection.prompts:
        collection.prompts.append(prompt)
        db.session.commit()
        log_activity(current_user.id, 'collection_add', f"Added prompt '{prompt.title}' to collection '{collection.name}'")

    if request.is_json:
        return jsonify({'success': True, 'message': f"Added '{prompt.title}' to '{collection.name}'"})

    flash(f"Added '{prompt.title}' to '{collection.name}'!", "success")
    return redirect(url_for('collections.detail', collection_id=collection.id))


@collections_bp.route('/<int:collection_id>/remove-prompt', methods=['POST'])
@login_required
def remove_prompt(collection_id):
    """
    Removes a prompt from a collection folder.
    """
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    prompt_id = request.form.get('prompt_id', type=int)
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first_or_404()

    if prompt in collection.prompts:
        collection.prompts.remove(prompt)
        db.session.commit()
        log_activity(current_user.id, 'collection_remove', f"Removed prompt '{prompt.title}' from collection '{collection.name}'")
        flash(f"Removed '{prompt.title}' from collection.", "info")

    return redirect(url_for('collections.detail', collection_id=collection.id))


@collections_bp.route('/<int:collection_id>/delete', methods=['POST'])
@login_required
def delete(collection_id):
    """
    Deletes a collection folder. Prompts inside the folder are preserved.
    """
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    name = collection.name
    db.session.delete(collection)
    db.session.commit()

    log_activity(current_user.id, 'collection_deleted', f"Deleted collection folder '{name}'")
    flash(f"Collection folder '{name}' deleted.", "warning")
    return redirect(url_for('collections.index'))
