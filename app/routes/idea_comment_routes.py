from flask import Blueprint, request, jsonify
from app.models.ideaComment import IdeaComment
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

idea_comments_bp = Blueprint('idea_comments', __name__)

@idea_comments_bp.route('', methods=['GET'])
def get_idea_comments():
    """Get all comments with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    idea_id = request.args.get('idea_id', type=int)
    author_id = request.args.get('author_id', type=int)
    
    query = IdeaComment.query
    
    if idea_id:
        query = query.filter(IdeaComment.idea_id == idea_id)
    if author_id:
        query = query.filter(IdeaComment.author_id == author_id)
    
    result = paginate(query.order_by(IdeaComment.created_at.desc()), page, per_page)
    
    return success_response({
        'comments': [comment.to_dict() for comment in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@idea_comments_bp.route('', methods=['POST'])
def create_comment():
    """Create new comment"""
    data = request.get_json()
    
    required_fields = ['idea_id', 'content', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        comment = IdeaComment(
            idea_id=data['idea_id'],
            content=data['content'],
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name']
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Check achievements for comment creation
        AchievementService.check_achievements(data['author_id'], 'comments_made')
        
        return success_response({
            'comment': comment.to_dict()
        }, 'Comment created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create comment: {str(e)}', 500)

@idea_comments_bp.route('/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """Update comment"""
    comment = IdeaComment.query.get(comment_id)
    if not comment:
        return error_response('Comment not found', 404)
    
    data = request.get_json()
    new_content = data.get('content')
    
    if not new_content:
        return error_response('Content is required', 400)
    
    try:
        comment.update_content(new_content)
        return success_response({
            'comment': comment.to_dict()
        }, 'Comment updated successfully')
    except Exception as e:
        return error_response(f'Failed to update comment: {str(e)}', 500)

@idea_comments_bp.route('/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete comment"""
    comment = IdeaComment.query.get(comment_id)
    if not comment:
        return error_response('Comment not found', 404)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return success_response(message='Comment deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete comment: {str(e)}', 500)