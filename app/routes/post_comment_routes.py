from flask import Blueprint, request, jsonify
from app.models.postComment import PostComment
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

post_comments_bp = Blueprint('post_comments', __name__)

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
def create_post_comment():
    """Create new post comment"""
    data = request.get_json()
    
    required_fields = ['post_id', 'content', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
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
        from models.post import Post
        post = Post.query.get(data['post_id'])
        if post:
            post.increment_comments()
        
        db.session.commit()
        
        return success_response({
            'comment': comment.to_dict()
        }, 'Comment created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create comment: {str(e)}', 500)

@post_comments_bp.route('/<int:comment_id>', methods=['PUT'])
def update_post_comment(comment_id):
    """Update post comment"""
    comment = PostComment.query.get(comment_id)
    if not comment:
        return error_response('Post comment not found', 404)
    
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
def delete_post_comment(comment_id):
    """Delete post comment"""
    comment = PostComment.query.get(comment_id)
    if not comment:
        return error_response('Post comment not found', 404)
    
    try:
        # Decrement post comment count
        from models.post import Post
        post = Post.query.get(comment.post_id)
        if post:
            post.decrement_comments()
        
        db.session.delete(comment)
        db.session.commit()
        
        return success_response(message='Comment deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete comment: {str(e)}', 500)