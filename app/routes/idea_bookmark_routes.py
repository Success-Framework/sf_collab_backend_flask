from flask import Blueprint, request, jsonify
from app.models.ideaBookmark import IdeaBookmark
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from datetime import datetime, timedelta

idea_bookmarks_bp = Blueprint('idea_bookmarks', __name__, url_prefix='/api/idea-bookmarks')

@idea_bookmarks_bp.route('', methods=['GET'])
def get_idea_bookmarks():
    """Get all idea bookmarks with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    idea_id = request.args.get('idea_id', type=int)
    recent_only = request.args.get('recent_only', 'false').lower() == 'true'
    
    query = IdeaBookmark.query
    
    if user_id:
        query = query.filter(IdeaBookmark.user_id == user_id)
    if idea_id:
        query = query.filter(IdeaBookmark.idea_id == idea_id)
    if recent_only:
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(IdeaBookmark.created_at >= week_ago)
    
    result = paginate(query.order_by(IdeaBookmark.created_at.desc()), page, per_page)
    
    return success_response({
        'bookmarks': [bookmark.to_dict() for bookmark in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@idea_bookmarks_bp.route('/<int:bookmark_id>', methods=['GET'])
def get_idea_bookmark(bookmark_id):
    """Get single idea bookmark by ID"""
    bookmark = IdeaBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Idea bookmark not found', 404)
    
    return success_response({'bookmark': bookmark.to_dict()})

@idea_bookmarks_bp.route('', methods=['POST'])
def create_idea_bookmark():
    """Create new idea bookmark"""
    data = request.get_json()
    
    required_fields = ['user_id', 'idea_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, idea_id')
    
    # Check if bookmark already exists
    existing = IdeaBookmark.query.filter_by(
        user_id=data['user_id'],
        idea_id=data['idea_id']
    ).first()
    
    if existing:
        return error_response('Bookmark already exists', 409)
    
    try:
        # Get idea details
        from models.idea import Idea
        idea = Idea.query.get(data['idea_id'])
        if not idea:
            return error_response('Idea not found', 404)
        
        bookmark = IdeaBookmark(
            user_id=data['user_id'],
            idea_id=data['idea_id'],
            title=data.get('title', idea.title),
            content_preview=data.get('content_preview', idea.description[:200] if idea.description else ''),
            url=data.get('url')
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        return success_response({
            'bookmark': bookmark.to_dict()
        }, 'Idea bookmark created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create idea bookmark: {str(e)}', 500)

@idea_bookmarks_bp.route('/<int:bookmark_id>', methods=['PUT'])
def update_idea_bookmark(bookmark_id):
    """Update idea bookmark"""
    bookmark = IdeaBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Idea bookmark not found', 404)
    
    data = request.get_json()
    
    try:
        bookmark.update_content(
            title=data.get('title'),
            content_preview=data.get('content_preview'),
            url=data.get('url')
        )
        return success_response({
            'bookmark': bookmark.to_dict()
        }, 'Idea bookmark updated successfully')
    except Exception as e:
        return error_response(f'Failed to update idea bookmark: {str(e)}', 500)

@idea_bookmarks_bp.route('/user/<int:user_id>/idea/<int:idea_id>', methods=['GET'])
def check_idea_bookmark(user_id, idea_id):
    """Check if user has bookmarked an idea"""
    bookmark = IdeaBookmark.query.filter_by(
        user_id=user_id,
        idea_id=idea_id
    ).first()
    
    return success_response({
        'is_bookmarked': bookmark is not None,
        'bookmark': bookmark.to_dict() if bookmark else None
    })

@idea_bookmarks_bp.route('/user/<int:user_id>/idea/<int:idea_id>', methods=['DELETE'])
def remove_idea_bookmark(user_id, idea_id):
    """Remove idea bookmark by user and idea"""
    bookmark = IdeaBookmark.query.filter_by(
        user_id=user_id,
        idea_id=idea_id
    ).first()
    
    if not bookmark:
        return error_response('Idea bookmark not found', 404)
    
    try:
        db.session.delete(bookmark)
        db.session.commit()
        return success_response(message='Idea bookmark removed successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to remove idea bookmark: {str(e)}', 500)

@idea_bookmarks_bp.route('/<int:bookmark_id>', methods=['DELETE'])
def delete_idea_bookmark(bookmark_id):
    """Delete idea bookmark"""
    bookmark = IdeaBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Idea bookmark not found', 404)
    
    try:
        db.session.delete(bookmark)
        db.session.commit()
        return success_response(message='Idea bookmark deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete idea bookmark: {str(e)}', 500)