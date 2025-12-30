from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.ResourceLike import ResourceLike
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

resource_likes_bp = Blueprint('resource_likes', __name__)

@resource_likes_bp.route('', methods=['GET'])
def get_resource_likes():
    """Get all resource likes with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    resource_id = request.args.get('resource_id', type=int)
    user_id = request.args.get('user_id', type=int)
    recent_only = request.args.get('recent_only', 'false').lower() == 'true'
    
    query = ResourceLike.query
    
    if resource_id:
        query = query.filter(ResourceLike.resource_id == resource_id)
    if user_id:
        query = query.filter(ResourceLike.user_id == user_id)
    if recent_only:
        from datetime import timedelta
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        query = query.filter(ResourceLike.liked_at >= hour_ago)
    
    result = paginate(query.order_by(ResourceLike.liked_at.desc()), page, per_page)
    
    return success_response({
        'likes': [like.to_dict() for like in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@resource_likes_bp.route('/<int:like_id>', methods=['GET'])
def get_resource_like(like_id):
    """Get single resource like by ID"""
    like = ResourceLike.query.get(like_id)
    if not like:
        return error_response('Resource like not found', 404)
    
    return success_response({'like': like.to_dict()})

@resource_likes_bp.route('', methods=['POST'])
def create_resource_like():
    """Create new resource like"""
    data = request.get_json()
    
    required_fields = ['resource_id', 'user_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: resource_id, user_id')
    
    # Check if like already exists
    existing = ResourceLike.query.filter_by(
        resource_id=data['resource_id'],
        user_id=data['user_id']
    ).first()
    
    if existing:
        return error_response('Resource already liked by user', 409)
    
    try:
        like = ResourceLike(
            resource_id=data['resource_id'],
            user_id=data['user_id']
        )
        
        db.session.add(like)
        
        # Increment resource like count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(data['resource_id'])
        if resource:
            resource.increment_likes()
        
        db.session.commit()
        
        return success_response({
            'like': like.to_dict()
        }, 'Resource liked successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to like resource: {str(e)}', 500)

@resource_likes_bp.route('/resource/<int:resource_id>/user/<int:user_id>', methods=['DELETE'])
def unlike_resource(resource_id, user_id):
    """Unlike a resource"""
    like = ResourceLike.query.filter_by(
        resource_id=resource_id,
        user_id=user_id
    ).first()
    
    if not like:
        return error_response('Like not found', 404)
    
    try:
        # Decrement resource like count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(resource_id)
        if resource:
            resource.decrement_likes()
        
        db.session.delete(like)
        db.session.commit()
        
        return success_response(message='Resource unliked successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to unlike resource: {str(e)}', 500)

@resource_likes_bp.route('/resource/<int:resource_id>/count', methods=['GET'])
def get_resource_like_count(resource_id):
    """Get like count for a resource"""
    count = ResourceLike.query.filter_by(resource_id=resource_id).count()
    
    return success_response({
        'resource_id': resource_id,
        'like_count': count
    })

@resource_likes_bp.route('/user/<int:user_id>/resource/<int:resource_id>', methods=['GET'])
def check_user_liked_resource(user_id, resource_id):
    """Check if user has liked a resource"""
    like = ResourceLike.query.filter_by(
        user_id=user_id,
        resource_id=resource_id
    ).first()
    
    return success_response({
        'has_liked': like is not None,
        'like': like.to_dict() if like else None
    })

@resource_likes_bp.route('/<int:like_id>', methods=['DELETE'])
def delete_resource_like(like_id):
    """Delete resource like"""
    like = ResourceLike.query.get(like_id)
    if not like:
        return error_response('Resource like not found', 404)
    
    try:
        # Decrement resource like count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(like.resource_id)
        if resource:
            resource.decrement_likes()
        
        db.session.delete(like)
        db.session.commit()
        
        return success_response(message='Like deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete like: {str(e)}', 500)