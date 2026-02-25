from flask import Blueprint, request, jsonify
from app.models.knowledge import Knowledge
from app.models.user import User
from app.utils.plans_utils import can_upload_file, can_update_file
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

knowledge_bp = Blueprint('knowledge', __name__)
# For now it is a good idea to mix content from SForger and external sources.
# In the future, we might want to separate them.
@knowledge_bp.route('', methods=['GET'])
def get_knowledge_posts():
    """Get all knowledge posts with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', type=str)
    author_id = request.args.get('author_id', type=int)
    search = request.args.get('search', type=str)
    include_comments = request.args.get('include_comments', 'false').lower() == 'true'
    include_external = request.args.get('include_external', 'true').lower() == 'true'
    query = Knowledge.query
    
    if category:
        query = query.filter(Knowledge.category.ilike(f'%{category}%'))
    if author_id:
        query = query.filter(Knowledge.author_id == author_id)
    if search:
        query = query.filter(
            (Knowledge.title.ilike(f'%{search}%')) |
            (Knowledge.title_description.ilike(f'%{search}%')) |
            (Knowledge.content_preview.ilike(f'%{search}%'))
        )
    # if include_external: 
        
    result = paginate(query.order_by(Knowledge.created_at.desc()), page, per_page)
    
    return success_response({
        'knowledge_posts': [post.to_dict(include_comments=include_comments) for post in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@knowledge_bp.route('/<int:knowledge_id>', methods=['GET'])
def get_knowledge_post(knowledge_id):
    """Get single knowledge post by ID"""
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return error_response('Knowledge post not found', 404)
    
    # Increment views
    knowledge.increment_views()
    
    include_comments = request.args.get('include_comments', 'false').lower() == 'true'
    
    return success_response({
        'knowledge_post': knowledge.to_dict(include_comments=include_comments)
    })

@knowledge_bp.route('', methods=['POST'])
def create_knowledge_post():
    """Create new knowledge post"""
    data = request.get_json()
    
    required_fields = ['title', 'title_description', 'content_preview', 'category', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        file_size_mb = data.get('file_size_mb', 0)
        can_upload, error_message = can_upload_file(data['author_id'], file_size_mb)
        if not can_upload:
            return error_response(error_message, 500)

        knowledge = Knowledge(
            title=data['title'],
            title_description=data['title_description'],
            content_preview=data['content_preview'],
            category=data['category'],
            file_url=data.get('file_url'),
            file_size_mb=file_size_mb,
            tags=data.get('tags', []),
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name']
        )
        
        db.session.add(knowledge)

        user = User.query.get(data['author_id'])
        if user:
            user.increase_storage_used(file_size_mb)
        
        db.session.commit()
        
        return success_response({
            'knowledge_post': knowledge.to_dict()
        }, 'Knowledge post created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create knowledge post: {str(e)}', 500)

@knowledge_bp.route('/<int:knowledge_id>', methods=['PUT'])
def update_knowledge_post(knowledge_id):
    """Update knowledge post"""
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return error_response('Knowledge post not found', 404)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            knowledge.title = data['title']
        if 'title_description' in data:
            knowledge.title_description = data['title_description']
        if 'content_preview' in data:
            knowledge.content_preview = data['content_preview']
        if 'category' in data:
            knowledge.category = data['category']
        if 'tags' in data:
            knowledge.tags = data['tags']
        if 'status' in data:
            knowledge.update_status(data['status'])
        if 'file_url' in data and 'file_size_mb' in data:
            new_file_size_mb = data['file_size_mb']
            old_file_size_mb = knowledge.file_size_mb or 0
            can_update, error_message = can_update_file(knowledge.author_id, new_file_size_mb - old_file_size_mb)
            if not can_update:
                return error_response(error_message, 500)
            
            # Update storage usage
            user = User.query.get(knowledge.author_id)
            if user:
                user.update_storage_used(old_file_size_mb or 0, new_file_size_mb)

            knowledge.file_size_mb = new_file_size_mb
            knowledge.file_url = data['file_url']s
        
        db.session.commit()
        
        return success_response({
            'knowledge_post': knowledge.to_dict()
        }, 'Knowledge post updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update knowledge post: {str(e)}', 500)

@knowledge_bp.route('/<int:knowledge_id>/like', methods=['POST'])
def like_knowledge_post(knowledge_id):
    """Like a knowledge post"""
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return error_response('Knowledge post not found', 404)
    
    try:
        knowledge.increment_likes()
        return success_response({
            'knowledge_post': knowledge.to_dict()
        }, 'Knowledge post liked successfully')
    except Exception as e:
        return error_response(f'Failed to like knowledge post: {str(e)}', 500)

@knowledge_bp.route('/<int:knowledge_id>/download', methods=['POST'])
def download_knowledge_post(knowledge_id):
    """Increment download count for knowledge post"""
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return error_response('Knowledge post not found', 404)
    
    try:
        knowledge.increment_downloads()
        return success_response({
            'knowledge_post': knowledge.to_dict()
        }, 'Download recorded successfully')
    except Exception as e:
        return error_response(f'Failed to record download: {str(e)}', 500)

@knowledge_bp.route('/<int:knowledge_id>/tags', methods=['POST'])
def add_tag_to_knowledge(knowledge_id):
    """Add tag to knowledge post"""
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return error_response('Knowledge post not found', 404)
    
    data = request.get_json()
    tag = data.get('tag')
    
    if not tag:
        return error_response('Tag is required', 400)
    
    try:
        knowledge.add_tag(tag)
        return success_response({
            'knowledge_post': knowledge.to_dict()
        }, 'Tag added successfully')
    except Exception as e:
        return error_response(f'Failed to add tag: {str(e)}', 500)

@knowledge_bp.route('/<int:knowledge_id>', methods=['DELETE'])
def delete_knowledge_post(knowledge_id):
    """Delete knowledge post"""
    knowledge = Knowledge.query.get(knowledge_id)
    if not knowledge:
        return error_response('Knowledge post not found', 404)
    
    try:
        user = User.query.get(knowledge.author_id)
        if user:
            user.decrease_storage_used(knowledge.file_size_mb or 0)
        
        db.session.delete(knowledge)
        db.session.commit()
        return success_response(message='Knowledge post deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete knowledge post: {str(e)}', 500)