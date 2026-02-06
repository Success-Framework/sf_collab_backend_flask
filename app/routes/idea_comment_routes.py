from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.ideaComment import IdeaComment
from app.models.idea import Idea
from app.models.user import User
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

# Import notification helpers
from app.notifications.helpers import (
    notify_comment_reply,
    notify_idea_feedback,
    notify_info
)

idea_comments_bp = Blueprint('idea_comments', __name__)


def get_user_full_name(user_id):
    """Helper to get user's full name"""
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name or ''} {user.last_name or ''}".strip() or "Someone"
    return "Someone"


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
@jwt_required()
def create_comment():
    """Create new comment on an idea"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['idea_id', 'content', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    # Get the idea to notify the creator
    idea = Idea.query.get(data['idea_id'])
    if not idea:
        return error_response('Idea not found', 404)
    
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
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: New Comment on Idea (4.2 & 4.3)
        # ════════════════════════════════════════════════════════════
        # Notify idea creator if not commenting on own idea
        if idea.creator_id != data['author_id']:
            try:
                commenter_name = f"{data['author_first_name']} {data['author_last_name']}".strip()
                
                # Notify about new comment
                notify_info(
                    user_id=idea.creator.id,
                    message=f"{commenter_name} commented on your idea '{idea.title}'.",
                    entity_type='idea',
                    link_url=f"/ideation-details?id={idea.id}"
                )
                
                # Also notify as feedback on the idea
                notify_idea_feedback(
                    user_id=idea.creator_id,
                    feedback_giver_id=data['author_id'],
                    feedback_giver_name=commenter_name,
                    idea_title=idea.title,
                    idea_id=idea.id
                )
            except Exception as e:
                print(f"⚠️ Idea comment notification failed: {e}")
        
        # Check achievements for comment creation
        AchievementService.check_achievements(data['author_id'], 'comments_made')
        
        return success_response({
            'comment': comment.to_dict()
        }, 'Comment created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create comment: {str(e)}', 500)


@idea_comments_bp.route('/<int:comment_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_comment(comment_id):
    """Reply to an existing comment"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get the parent comment
    parent_comment = IdeaComment.query.get(comment_id)
    if not parent_comment:
        return error_response('Comment not found', 404)
    
    required_fields = ['content', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        reply = IdeaComment(
            idea_id=parent_comment.idea_id,
            content=data['content'],
            author_id=current_user_id,
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name'],
            parent_id=comment_id  # If you have parent_id field for threading
        )
        
        db.session.add(reply)
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Comment Reply (4.2)
        # ════════════════════════════════════════════════════════════
        # Notify original commenter if not replying to own comment
        if parent_comment.author_id != current_user_id:
            try:
                replier_name = f"{data['author_first_name']} {data['author_last_name']}".strip()
                notify_comment_reply(
                    user_id=parent_comment.author_id,
                    replier_id=current_user_id,
                    replier_name=replier_name,
                    comment_id=comment_id
                )
            except Exception as e:
                print(f"⚠️ Comment reply notification failed: {e}")
        
        # Check achievements
        AchievementService.check_achievements(current_user_id, 'comments_made')
        
        return success_response({
            'comment': reply.to_dict()
        }, 'Reply created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create reply: {str(e)}', 500)


@idea_comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update comment"""
    current_user_id = get_jwt_identity()
    
    comment = IdeaComment.query.get(comment_id)
    if not comment:
        return error_response('Comment not found', 404)
    
    # Check ownership
    if comment.author_id != current_user_id:
        return error_response('Unauthorized to update this comment', 403)
    
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
@jwt_required()
def delete_comment(comment_id):
    """Delete comment"""
    current_user_id = get_jwt_identity()
    
    comment = IdeaComment.query.get(comment_id)
    if not comment:
        return error_response('Comment not found', 404)
    
    # Check ownership
    if comment.author_id != current_user_id:
        return error_response('Unauthorized to delete this comment', 403)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return success_response(message='Comment deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete comment: {str(e)}', 500)