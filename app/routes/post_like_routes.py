"""
SF Collab Post Like Routes
Updated with notification triggers for social interactions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.postLike import PostLike
from app.models.post import Post
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from datetime import datetime

# ===== NOTIFICATION IMPORTS =====
from app.notifications.helpers import notify_post_liked

post_likes_bp = Blueprint('post_likes', __name__)


def get_user_full_name(user_id):
    """Get user's full name"""
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name} {user.last_name}"
    return "Unknown User"


@post_likes_bp.route('', methods=['GET'])
@jwt_required()
def get_post_likes():
    """Get likes for a post"""
    post_id = request.args.get('post_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not post_id:
        return error_response('post_id is required', 400)
    
    query = PostLike.query.filter_by(post_id=post_id)
    result = paginate(query.order_by(PostLike.created_at.desc()), page, per_page)
    
    return success_response({
        'likes': [like.to_dict() for like in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


@post_likes_bp.route('', methods=['POST'])
@jwt_required()
def like_post():
    """Like a post"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    post_id = data.get('post_id')
    if not post_id:
        return error_response('post_id is required', 400)
    
    # Check if post exists
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    # Check if already liked
    existing_like = PostLike.query.filter_by(
        post_id=post_id,
        user_id=current_user_id
    ).first()
    
    if existing_like:
        return error_response('Already liked this post', 400)
    
    try:
        like = PostLike(
            post_id=post_id,
            user_id=current_user_id
        )
        
        db.session.add(like)
        
        # Update post like count
        post.likes_count = (post.likes_count or 0) + 1
        
        db.session.commit()
        
        # ===== SEND NOTIFICATION TO POST OWNER =====
        if post.user_id != current_user_id:
            try:
                liker_name = get_user_full_name(current_user_id)
                notify_post_liked(
                    user_id=post.user_id,
                    liker_id=current_user_id,
                    liker_name=liker_name,
                    post_id=post_id
                )
            except Exception as e:
                print(f"Error sending post liked notification: {e}")
        
        return success_response({
            'like': like.to_dict(),
            'likes_count': post.likes_count
        }, 'Post liked successfully', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to like post: {str(e)}', 500)


@post_likes_bp.route('/<int:like_id>', methods=['DELETE'])
@jwt_required()
def unlike_post(like_id):
    """Unlike a post"""
    current_user_id = int(get_jwt_identity())
    
    like = PostLike.query.get(like_id)
    if not like:
        return error_response('Like not found', 404)
    
    if like.user_id != current_user_id:
        return error_response('Unauthorized to unlike this post', 403)
    
    try:
        post = Post.query.get(like.post_id)
        if post and post.likes_count:
            post.likes_count = max(0, post.likes_count - 1)
        
        db.session.delete(like)
        db.session.commit()
        
        return success_response({
            'likes_count': post.likes_count if post else 0
        }, 'Post unliked successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to unlike post: {str(e)}', 500)


@post_likes_bp.route('/toggle', methods=['POST'])
@jwt_required()
def toggle_like():
    """Toggle like on a post"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    post_id = data.get('post_id')
    if not post_id:
        return error_response('post_id is required', 400)
    
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    existing_like = PostLike.query.filter_by(
        post_id=post_id,
        user_id=current_user_id
    ).first()
    
    try:
        if existing_like:
            # Unlike
            if post.likes_count:
                post.likes_count = max(0, post.likes_count - 1)
            db.session.delete(existing_like)
            db.session.commit()
            
            return success_response({
                'liked': False,
                'likes_count': post.likes_count or 0
            }, 'Post unliked')
        else:
            # Like
            like = PostLike(
                post_id=post_id,
                user_id=current_user_id
            )
            db.session.add(like)
            post.likes_count = (post.likes_count or 0) + 1
            db.session.commit()
            
            # ===== SEND NOTIFICATION TO POST OWNER =====
            if post.user_id != current_user_id:
                try:
                    liker_name = get_user_full_name(current_user_id)
                    notify_post_liked(
                        user_id=post.user_id,
                        liker_id=current_user_id,
                        liker_name=liker_name,
                        post_id=post_id
                    )
                except Exception as e:
                    print(f"Error sending post liked notification: {e}")
            
            return success_response({
                'liked': True,
                'likes_count': post.likes_count
            }, 'Post liked')
            
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to toggle like: {str(e)}', 500)


@post_likes_bp.route('/check', methods=['GET'])
@jwt_required()
def check_like():
    """Check if current user liked a post"""
    current_user_id = int(get_jwt_identity())
    post_id = request.args.get('post_id', type=int)
    
    if not post_id:
        return error_response('post_id is required', 400)
    
    like = PostLike.query.filter_by(
        post_id=post_id,
        user_id=current_user_id
    ).first()
    
    post = Post.query.get(post_id)
    
    return success_response({
        'liked': like is not None,
        'like_id': like.id if like else None,
        'likes_count': post.likes_count if post else 0
    })