from flask import Blueprint, request, jsonify
from app.models.postLike import PostLike
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

post_likes_bp = Blueprint('post_likes', __name__)

@post_likes_bp.route('', methods=['GET'])
def get_post_likes():
    """Get all post likes with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    post_id = request.args.get('post_id', type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = PostLike.query
    
    if post_id:
        query = query.filter(PostLike.post_id == post_id)
    if user_id:
        query = query.filter(PostLike.user_id == user_id)
    
    result = paginate(query.order_by(PostLike.liked_at.desc()), page, per_page)
    
    return success_response({
        'likes': [like.to_dict() for like in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@post_likes_bp.route('/<int:like_id>', methods=['GET'])
def get_post_like(like_id):
    """Get single post like by ID"""
    like = PostLike.query.get(like_id)
    if not like:
        return error_response('Post like not found', 404)
    
    return success_response({'like': like.to_dict()})

@post_likes_bp.route('/post/<int:post_id>/user/<int:user_id>', methods=['GET'])
def check_post_like(post_id, user_id):
    """Check if user liked a post"""
    like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    return success_response({
        'is_liked': like is not None,
        'like': like.to_dict() if like else None
    })

@post_likes_bp.route('/post/<int:post_id>/count', methods=['GET'])
def get_post_likes_count(post_id):
    """Get like count for a post"""
    count = PostLike.query.filter_by(post_id=post_id).count()
    
    return success_response({
        'post_id': post_id,
        'like_count': count
    })

@post_likes_bp.route('/<int:like_id>', methods=['DELETE'])
def delete_post_like(like_id):
    """Delete post like"""
    like = PostLike.query.get(like_id)
    if not like:
        return error_response('Post like not found', 404)
    
    try:
        # Decrement post like count
        from models.post import Post
        post = Post.query.get(like.post_id)
        if post:
            post.decrement_likes()
        
        db.session.delete(like)
        db.session.commit()
        
        return success_response(message='Like removed successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to remove like: {str(e)}', 500)