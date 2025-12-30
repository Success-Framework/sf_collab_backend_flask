from flask import Blueprint, request, jsonify
from app.models.knowledgeBookmark import KnowledgeBookmark
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

knowledge_bookmarks_bp = Blueprint('knowledge_bookmarks', __name__)

@knowledge_bookmarks_bp.route('', methods=['GET'])
def get_knowledge_bookmarks():
    """Get all knowledge bookmarks with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    knowledge_id = request.args.get('knowledge_id', type=int)
    
    query = KnowledgeBookmark.query
    
    if user_id:
        query = query.filter(KnowledgeBookmark.user_id == user_id)
    if knowledge_id:
        query = query.filter(KnowledgeBookmark.knowledge_id == knowledge_id)
    
    result = paginate(query.order_by(KnowledgeBookmark.created_at.desc()), page, per_page)
    
    return success_response({
        'bookmarks': [bookmark.to_dict() for bookmark in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@knowledge_bookmarks_bp.route('/<int:bookmark_id>', methods=['GET'])
def get_knowledge_bookmark(bookmark_id):
    """Get single knowledge bookmark by ID"""
    bookmark = KnowledgeBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Knowledge bookmark not found', 404)
    
    return success_response({'bookmark': bookmark.to_dict()})

@knowledge_bookmarks_bp.route('', methods=['POST'])
def create_knowledge_bookmark():
    """Create new knowledge bookmark"""
    data = request.get_json()
    
    required_fields = ['user_id', 'knowledge_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, knowledge_id')
    
    # Check if bookmark already exists
    existing = KnowledgeBookmark.query.filter_by(
        user_id=data['user_id'],
        knowledge_id=data['knowledge_id']
    ).first()
    
    if existing:
        return error_response('Bookmark already exists', 409)
    
    try:
        # Get knowledge post details
        from models.knowledge import Knowledge
        knowledge = Knowledge.query.get(data['knowledge_id'])
        if not knowledge:
            return error_response('Knowledge post not found', 404)
        
        bookmark = KnowledgeBookmark(
            user_id=data['user_id'],
            knowledge_id=data['knowledge_id'],
            title=data.get('title', knowledge.title),
            content_preview=data.get('content_preview', knowledge.content_preview),
            url=data.get('url')
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        return success_response({
            'bookmark': bookmark.to_dict()
        }, 'Knowledge bookmark created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create knowledge bookmark: {str(e)}', 500)

@knowledge_bookmarks_bp.route('/<int:bookmark_id>', methods=['PUT'])
def update_knowledge_bookmark(bookmark_id):
    """Update knowledge bookmark"""
    bookmark = KnowledgeBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Knowledge bookmark not found', 404)
    
    data = request.get_json()
    
    try:
        bookmark.update_content(
            title=data.get('title'),
            content_preview=data.get('content_preview'),
            url=data.get('url')
        )
        return success_response({
            'bookmark': bookmark.to_dict()
        }, 'Knowledge bookmark updated successfully')
    except Exception as e:
        return error_response(f'Failed to update knowledge bookmark: {str(e)}', 500)

@knowledge_bookmarks_bp.route('/<int:bookmark_id>', methods=['DELETE'])
def delete_knowledge_bookmark(bookmark_id):
    """Delete knowledge bookmark"""
    bookmark = KnowledgeBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Knowledge bookmark not found', 404)
    
    try:
        db.session.delete(bookmark)
        db.session.commit()
        return success_response(message='Knowledge bookmark deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete knowledge bookmark: {str(e)}', 500)