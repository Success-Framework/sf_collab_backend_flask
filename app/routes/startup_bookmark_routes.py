from flask import Blueprint, request, jsonify
from app.models.startupBookmark import StartupBookmark
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

bookmarks_bp = Blueprint('startup_bookmarks', __name__, url_prefix='/api/startup-bookmarks')

@bookmarks_bp.route('', methods=['GET'])
def get_bookmarks():
    """Get all bookmarks with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = StartupBookmark.query
    
    if user_id:
        query = query.filter(StartupBookmark.user_id == user_id)
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'bookmarks': [bookmark.to_dict() for bookmark in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@bookmarks_bp.route('/<int:bookmark_id>', methods=['GET'])
def get_bookmark(bookmark_id):
    """Get single bookmark by ID"""
    bookmark = StartupBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Bookmark not found', 404)
    
    return success_response({'bookmark': bookmark.to_dict()})

@bookmarks_bp.route('', methods=['POST'])
def create_bookmark():
    """Create new bookmark"""
    data = request.get_json()
    
    required_fields = ['user_id', 'startup_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, startup_id')
    
    # Check if bookmark already exists
    existing = StartupBookmark.query.filter_by(
        user_id=data['user_id'], 
        startup_id=data['startup_id']
    ).first()
    
    if existing:
        return error_response('Bookmark already exists', 409)
    
    try:
        bookmark = StartupBookmark(
            user_id=data['user_id'],
            startup_id=data['startup_id'],
            title=data.get('title'),
            content_preview=data.get('content_preview'),
            url=data.get('url')
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        return success_response({'bookmark': bookmark.to_dict()}, 'Bookmark created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create bookmark: {str(e)}', 500)

@bookmarks_bp.route('/<int:bookmark_id>', methods=['PUT'])
def update_bookmark(bookmark_id):
    """Update bookmark"""
    bookmark = StartupBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Bookmark not found', 404)
    
    data = request.get_json()
    
    try:
        bookmark.update_content(
            title=data.get('title'),
            content_preview=data.get('content_preview'),
            url=data.get('url')
        )
        return success_response({'bookmark': bookmark.to_dict()}, 'Bookmark updated successfully')
    except Exception as e:
        return error_response(f'Failed to update bookmark: {str(e)}', 500)

@bookmarks_bp.route('/<int:bookmark_id>', methods=['DELETE'])
def delete_bookmark(bookmark_id):
    """Delete bookmark"""
    bookmark = StartupBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Bookmark not found', 404)
    
    try:
        db.session.delete(bookmark)
        db.session.commit()
        return success_response(message='Bookmark deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete bookmark: {str(e)}', 500)