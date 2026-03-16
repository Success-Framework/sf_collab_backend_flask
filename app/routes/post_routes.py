from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.post import Post
from app.models.postMedia import PostMedia
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from app.utils.upload_to_s3 import upload_file_to_s3

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('', methods=['GET'])
@jwt_required
def get_posts():
    """Get all posts with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    author_id = request.args.get('author_id', type=int)
    post_type = request.args.get('type', type=str)
    search = request.args.get('search', type=str)
    
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
            include_comments=True,
            include_media=True,
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
@jwt_required()
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
@jwt_required()
def create_post():
    """Create new post"""
    media_files = request.files.getlist('media')
    
    required_fields = ['user_id', 'author_id', 'content']
    if not all(field in request.form for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        user = User.query.get(request.form['user_id'])
        if not user:
            return error_response('User not found', 404)
        
        post = Post(
            user_id=request.form.get('user_id', user.id),
            author_id=request.form.get('author_id', user.id),
            author_first_name=request.form.get('author_first_name', user.first_name),
            author_last_name=request.form.get('author_last_name', user.last_name),
            content=request.form.get('content'),
            type=request.form.get('type', 'professional'),
            tags=request.form.get('tags', [])
        )
        db.session.add(post)
        db.session.flush()

        for file in media_files:
            if not file or file.filename == '':
                continue
            media_url = upload_file_to_s3(file)
            post_media = PostMedia(
                file_name=file.filename,
                content_type=file.content_type,
                file_size=len(file.read()),
                media_url=media_url,
                parent_post=post.id
            )
            db.session.add(post_media)
            post.media_items.append(post_media)
       
        db.session.commit()
        
        return success_response({
            'post': post.to_dict(include_media=True if media_files else False)
        }, 'Post created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create post: {str(e)}', 500)

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
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
@jwt_required()
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
    from app.models.postLike import PostLike
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
@jwt_required()
def unlike_post(post_id):
    """Unlike a post"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return error_response('User ID is required', 400)
    
    from app.models.postLike import PostLike
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
@jwt_required()
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
@jwt_required()
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
    
@posts_bp.route('/<int:post_id>/save', methods=['POST'])
@jwt_required()
def save_post(post_id):
    """Save a post"""
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    data = request.get_json()
    user_id = data.get('user_id') or get_jwt_identity()
    
    if not user_id:
        return error_response('User not found', 400)
    
    # Check if user already saved the post
    from app.models.postSave import PostSave
    existing_save = PostSave.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if existing_save:
        return error_response('Post already saved by user', 409)
    
    try:
        # Create save record
        save = PostSave(post_id=post_id, user_id=user_id)
        db.session.add(save)
        
        # Increment post save count
        post.increment_saves()
        
        db.session.commit()
        return success_response({
            'post': post.to_dict(user_id=user_id),
            'save': save.to_dict()
        }, 'Post saved successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to save post: {str(e)}', 500)

@posts_bp.route('/<int:post_id>/unsave', methods=['POST'])
@jwt_required()
def unsave_post(post_id):
    """Unsave a post"""
    data = request.get_json()
    user_id = data.get('user_id') or get_jwt_identity()

    if not user_id:
        return error_response('User not found', 400)
    
    post = Post.query.get(post_id)
    if not post:
        return error_response('Post not found', 404)
    
    from app.models.postSave import PostSave
    save = PostSave.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if not save:
        return error_response('Save not found', 404)
    
    try:
        db.session.delete(save)
        post.decrement_saves()
        db.session.commit()
        
        return success_response({
            'post': post.to_dict(user_id=user_id)
        }, 'Post unsaved successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to unsave post: {str(e)}', 500)