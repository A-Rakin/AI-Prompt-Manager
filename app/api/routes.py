from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import Prompt, Tag, Category
from app.utils.helpers import record_copy_event

# ==============================================================================
# PromptForge - RESTful API Endpoints (v1)
# ==============================================================================
# Provides programmatic JSON access to Prompts, Tags, and Categories.
# Designed for future browser extension or mobile client integration.
#
# Key Concepts Explained:
# 1. REST (Representational State Transfer): Standard architectural style for APIs
#    using standard HTTP methods (GET, POST, PUT, DELETE).
# 2. JSON Serialization: Converting database models into structured JSON strings
#    understandable by non-Python applications (like JavaScript, Swift, or Kotlin).
# ==============================================================================

@api_bp.route('/prompts', methods=['GET'])
@login_required
def get_prompts():
    """
    Returns paginated JSON list of user active prompts.
    Supports filtering via query parameters: `q`, `platform`, `category_id`, `tag`.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_q = request.args.get('q', '').strip()
    platform = request.args.get('platform', '').strip()

    query = Prompt.query.filter_by(user_id=current_user.id, status='active')

    if search_q:
        filter_str = f"%{search_q}%"
        query = query.filter(
            (Prompt.title.ilike(filter_str)) |
            (Prompt.description.ilike(filter_str)) |
            (Prompt.content.ilike(filter_str))
        )

    if platform:
        query = query.filter_by(platform=platform)

    pagination = query.order_by(Prompt.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'status': 'success',
        'page': page,
        'per_page': per_page,
        'total_items': pagination.total,
        'total_pages': pagination.pages,
        'data': [p.to_dict() for p in pagination.items]
    })


@api_bp.route('/prompts/<int:prompt_id>', methods=['GET'])
@login_required
def get_prompt(prompt_id):
    """
    Returns JSON details of a single prompt by ID.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first()
    if not prompt:
        return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404

    return jsonify({'status': 'success', 'data': prompt.to_dict()})


@api_bp.route('/prompts/<int:prompt_id>/copy', methods=['POST'])
@login_required
def api_copy_prompt(prompt_id):
    """
    API endpoint to increment copy count and update copy velocity history.
    """
    prompt = Prompt.query.filter_by(id=prompt_id, user_id=current_user.id).first()
    if not prompt:
        return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404

    success = record_copy_event(current_user.id, prompt)
    if success:
        return jsonify({
            'status': 'success',
            'copy_count': prompt.copy_count,
            'message': 'Copy count recorded successfully'
        })
    return jsonify({'status': 'error', 'message': 'Failed to record copy event'}), 500


@api_bp.route('/tags', methods=['GET'])
@login_required
def get_tags():
    """
    Returns list of all tag names associated with current user for search autocompletion.
    """
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'status': 'success',
        'tags': [t.name for t in tags]
    })


@api_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """
    Returns high-level user statistics summary.
    """
    total = Prompt.query.filter_by(user_id=current_user.id, status='active').count()
    favorites = Prompt.query.filter_by(user_id=current_user.id, status='active', is_favorite=True).count()
    archived = Prompt.query.filter_by(user_id=current_user.id, status='archived').count()

    return jsonify({
        'status': 'success',
        'stats': {
            'total_active_prompts': total,
            'favorite_prompts': favorites,
            'archived_prompts': archived
        }
    })
