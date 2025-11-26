from flask import Blueprint, request, jsonify
from app.models.knowledgeComment import KnowledgeComment
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

knowledge_comments_bp = Blueprint('knowledge_comments', __name__, url_prefix='/api/knowledge-comments')

@knowledge_comments_bp.route('', methods=['GET'])
def get_knowledge_comments():
    """Get all knowledge comments with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    resource_id = request.args.get('resource_id', type=int)
    author_id = request.args.get('author_id', type=int)
    
    query = KnowledgeComment.query
    
    if resource_id:
        query = query.filter(KnowledgeComment.resource_id == resource_id)
    if author_id:
        query = query.filter(KnowledgeComment.author_id == author_id)
    
    result = paginate(query.order_by(KnowledgeComment.created_at.desc()), page, per_page)
    
    return success_response({
        'comments': [comment.to_dict() for comment in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@knowledge_comments_bp.route('/<int:comment_id>', methods=['GET'])
def get_knowledge_comment(comment_id):
    """Get single knowledge comment by ID"""
    comment = KnowledgeComment.query.get(comment_id)
    if not comment:
        return error_response('Knowledge comment not found', 404)
    
    return success_response({'comment': comment.to_dict()})

@knowledge_comments_bp.route('', methods=['POST'])
def create_knowledge_comment():
    """Create new knowledge comment"""
    data = request.get_json()
    
    required_fields = ['resource_id', 'content', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        comment = KnowledgeComment(
            resource_id=data['resource_id'],
            content=data['content'],
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name']
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return success_response({
            'comment': comment.to_dict()
        }, 'Knowledge comment created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create knowledge comment: {str(e)}', 500)

@knowledge_comments_bp.route('/<int:comment_id>', methods=['PUT'])
def update_knowledge_comment(comment_id):
    """Update knowledge comment"""
    comment = KnowledgeComment.query.get(comment_id)
    if not comment:
        return error_response('Knowledge comment not found', 404)
    
    data = request.get_json()
    new_content = data.get('content')
    
    if not new_content:
        return error_response('Content is required', 400)
    
    try:
        comment.update_content(new_content)
        return success_response({
            'comment': comment.to_dict()
        }, 'Knowledge comment updated successfully')
    except Exception as e:
        return error_response(f'Failed to update knowledge comment: {str(e)}', 500)

@knowledge_comments_bp.route('/<int:comment_id>', methods=['DELETE'])
def delete_knowledge_comment(comment_id):
    """Delete knowledge comment"""
    comment = KnowledgeComment.query.get(comment_id)
    if not comment:
        return error_response('Knowledge comment not found', 404)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return success_response(message='Knowledge comment deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete knowledge comment: {str(e)}', 500)