from flask import Blueprint, request, jsonify
from app.models.post import Post
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('', methods=['GET'])
def get_posts():
    """Get all posts with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    author_id = request.args.get('author_id', type=int)
    post_type = request.args.get('type', type=str)
    search = request.args.get('search', type=str)
    include_comments = request.args.get('include_comments', 'false').lower() == 'true'
    include_media = request.args.get('include_media', 'false').lower() == 'true'
    
    query = Post.query
    
    if user_id:
        query = query.filter(Post.user_id == user_id)
    if author_id:
        query = query.filter(Post.author_id == author_id)
    if post_type:
        from app.models.Enums import PostType
        query = query.filter(Post.type == PostType(post_type))
    if search:
        query = query.filter(
            (Post.content.ilike(f'%{search}%')) |
            (Post.tags.contains([search]))
        )
    
    result = paginate(query.order_by(Post.created_at.desc()), page, per_page)
    
    current_user_id = request.args.get('current_user_id', type=int)
    
    return success_response({
        'posts': [post.to_dict(
            include_comments=include_comments,
            include_media=include_media,
            user_id=current_user_id
        ) for post in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get single post by ID"""
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    include_comments = request.args.get('include_comments', 'false').lower() == 'true'
    include_media = request.args.get('include_media', 'false').lower() == 'true'
    current_user_id = request.args.get('current_user_id', type=int)
    
    return success_response({
        'post': post.to_dict(
            include_comments=include_comments,
            include_media=include_media,
            user_id=current_user_id
        )
    })

@posts_bp.route('', methods=['POST'])
def create_post():
    """Create new post"""
    data = request.get_json()
    
    required_fields = ['user_id', 'author_id', 'author_first_name', 'author_last_name', 'content']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        post = Post(
            user_id=data['user_id'],
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name'],
            content=data['content'],
            type=data.get('type', 'professional'),
            tags=data.get('tags', [])
        )
        
        db.session.add(post)
        db.session.commit()
        
        return success_response({
            'post': post.to_dict()
        }, 'Post created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create post: {str(e)}', 500)

@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update post"""
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    data = request.get_json()
    
    try:
        if 'content' in data:
            post.content = data['content']
        if 'type' in data:
            from app.models.Enums import PostType
            post.type = PostType(data['type'])
        if 'tags' in data:
            post.tags = data['tags']
        
        db.session.commit()
        
        return success_response({
            'post': post.to_dict()
        }, 'Post updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update post: {str(e)}', 500)

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like a post"""
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return error_response('User ID is required', 400)
    
    # Check if user already liked the post
    from models.postLike import PostLike
    existing_like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if existing_like:
        return error_response('Post already liked by user', 409)
    
    try:
        # Create like record
        like = PostLike(post_id=post_id, user_id=user_id)
        db.session.add(like)
        
        # Increment post like count
        post.increment_likes()
        
        db.session.commit()
        
        return success_response({
            'post': post.to_dict(user_id=user_id),
            'like': like.to_dict()
        }, 'Post liked successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to like post: {str(e)}', 500)

@posts_bp.route('/<int:post_id>/unlike', methods=['POST'])
def unlike_post(post_id):
    """Unlike a post"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return error_response('User ID is required', 400)
    
    from models.postLike import PostLike
    like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if not like:
        return error_response('Like not found', 404)
    
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    try:
        db.session.delete(like)
        post.decrement_likes()
        db.session.commit()
        
        return success_response({
            'post': post.to_dict(user_id=user_id)
        }, 'Post unliked successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to unlike post: {str(e)}', 500)

@posts_bp.route('/<int:post_id>/tags', methods=['POST'])
def add_tag_to_post(post_id):
    """Add tag to post"""
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    data = request.get_json()
    tag = data.get('tag')
    
    if not tag:
        return error_response('Tag is required', 400)
    
    try:
        post.add_tag(tag)
        return success_response({
            'post': post.to_dict()
        }, 'Tag added successfully')
    except Exception as e:
        return error_response(f'Failed to add tag: {str(e)}', 500)

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete post"""
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    try:
        db.session.delete(post)
        db.session.commit()
        return success_response(message='Post deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete post: {str(e)}', 500)