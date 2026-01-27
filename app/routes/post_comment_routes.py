"""
Post Comment Routes with Notification Triggers
SF Collab Notification System - Section 4.2 Social & Engagement
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.postComment import PostComment
from app.models.post import Post
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

# Import notification helpers
from app.notifications.helpers import (
    notify_new_comment,
    notify_comment_reply,
    notify_user_mentioned
)

post_comments_bp = Blueprint('post_comments', __name__)


def get_user_full_name(user_id):
    """Helper to get user's full name"""
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name or ''} {user.last_name or ''}".strip() or "Someone"
    return "Someone"


def extract_mentions(content):
    """Extract @mentions from comment content"""
    import re
    # Match @username patterns
    mentions = re.findall(r'@(\w+)', content)
    return mentions


def get_user_by_username(username):
    """Get user by username for mentions"""
    return User.query.filter_by(username=username).first()


@post_comments_bp.route('', methods=['GET'])
def get_post_comments():
    """Get all post comments with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    post_id = request.args.get('post_id', type=int)
    author_id = request.args.get('author_id', type=int)
    
    query = PostComment.query
    
    if post_id:
        query = query.filter(PostComment.post_id == post_id)
    if author_id:
        query = query.filter(PostComment.author_id == author_id)
    
    result = paginate(query.order_by(PostComment.created_at.desc()), page, per_page)
    
    return success_response({
        'comments': [comment.to_dict() for comment in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


@post_comments_bp.route('/<int:comment_id>', methods=['GET'])
def get_post_comment(comment_id):
    """Get single post comment by ID"""
    comment = PostComment.query.get(comment_id)
    if not comment:
        return error_response('Post comment not found', 404)
    
    return success_response({'comment': comment.to_dict()})


@post_comments_bp.route('', methods=['POST'])
@jwt_required()
def create_post_comment():
    """Create new post comment"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['post_id', 'content', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    # Get the post to notify the author
    post = Post.query.get(data['post_id'])
    if not post:
        return error_response('Post not found', 404)
    
    try:
        comment = PostComment(
            post_id=data['post_id'],
            content=data['content'],
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name']
        )
        
        db.session.add(comment)
        
        # Increment post comment count
        post.increment_comments()
        
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: New Comment on Post (4.2)
        # ════════════════════════════════════════════════════════════
        commenter_name = f"{data['author_first_name']} {data['author_last_name']}".strip()
        
        # Notify post author if not commenting on own post
        if post.author_id != data['author_id']:
            try:
                notify_new_comment(
                    user_id=post.author_id,
                    commenter_id=data['author_id'],
                    commenter_name=commenter_name,
                    entity_type='post',
                    entity_id=post.id
                )
            except Exception as e:
                print(f"⚠️ Post comment notification failed: {e}")
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: User Mentioned in Comment (4.2)
        # ════════════════════════════════════════════════════════════
        try:
            mentions = extract_mentions(data['content'])
            for username in mentions:
                mentioned_user = get_user_by_username(username)
                if mentioned_user and mentioned_user.id != data['author_id']:
                    notify_user_mentioned(
                        user_id=mentioned_user.id,
                        actor_id=data['author_id'],
                        actor_name=commenter_name,
                        entity_type='comment',
                        entity_id=comment.id
                    )
        except Exception as e:
            print(f"⚠️ Mention notification failed: {e}")
        
        return success_response({
            'comment': comment.to_dict()
        }, 'Comment created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create comment: {str(e)}', 500)


@post_comments_bp.route('/<int:comment_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_post_comment(comment_id):
    """Reply to an existing post comment"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get the parent comment
    parent_comment = PostComment.query.get(comment_id)
    if not parent_comment:
        return error_response('Comment not found', 404)
    
    required_fields = ['content', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        reply = PostComment(
            post_id=parent_comment.post_id,
            content=data['content'],
            author_id=current_user_id,
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name'],
            parent_id=comment_id  # If you have parent_id field for threading
        )
        
        db.session.add(reply)
        
        # Increment post comment count
        post = Post.query.get(parent_comment.post_id)
        if post:
            post.increment_comments()
        
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
        
        return success_response({
            'comment': reply.to_dict()
        }, 'Reply created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create reply: {str(e)}', 500)


@post_comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_post_comment(comment_id):
    """Update post comment"""
    current_user_id = get_jwt_identity()
    
    comment = PostComment.query.get(comment_id)
    if not comment:
        return error_response('Post comment not found', 404)
    
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


@post_comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_post_comment(comment_id):
    """Delete post comment"""
    current_user_id = get_jwt_identity()
    
    comment = PostComment.query.get(comment_id)
    if not comment:
        return error_response('Post comment not found', 404)
    
    # Check ownership
    if comment.author_id != current_user_id:
        return error_response('Unauthorized to delete this comment', 403)
    
    try:
        # Decrement post comment count
        post = Post.query.get(comment.post_id)
        if post:
            post.decrement_comments()
        
        db.session.delete(comment)
        db.session.commit()
        
        return success_response(message='Comment deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete comment: {str(e)}', 500)