from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models.ResourceView import ResourceView
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

resource_views_bp = Blueprint('resource_views', __name__, url_prefix='/api/resource-views')

@resource_views_bp.route('', methods=['GET'])
def get_resource_views():
    """Get all resource views with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    resource_id = request.args.get('resource_id', type=int)
    user_id = request.args.get('user_id', type=int)
    recent_only = request.args.get('recent_only', 'false').lower() == 'true'
    
    query = ResourceView.query
    
    if resource_id:
        query = query.filter(ResourceView.resource_id == resource_id)
    if user_id:
        query = query.filter(ResourceView.user_id == user_id)
    if recent_only:
        day_ago = datetime.utcnow() - timedelta(days=1)
        query = query.filter(ResourceView.viewed_at >= day_ago)
    
    result = paginate(query.order_by(ResourceView.viewed_at.desc()), page, per_page)
    
    return success_response({
        'views': [view.to_dict() for view in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@resource_views_bp.route('/<int:view_id>', methods=['GET'])
def get_resource_view(view_id):
    """Get single resource view by ID"""
    view = ResourceView.query.get(view_id)
    if not view:
        return error_response('Resource view not found', 404)
    
    return success_response({'view': view.to_dict()})

@resource_views_bp.route('', methods=['POST'])
def create_resource_view():
    """Create new resource view"""
    data = request.get_json()
    
    required_fields = ['resource_id', 'user_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: resource_id, user_id')
    
    # Check if view already exists in the last hour (prevent spam)
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    existing = ResourceView.query.filter(
        ResourceView.resource_id == data['resource_id'],
        ResourceView.user_id == data['user_id'],
        ResourceView.viewed_at >= hour_ago
    ).first()
    
    if existing:
        # Update the existing view timestamp
        existing.viewed_at = datetime.utcnow()
        db.session.commit()
        return success_response({
            'view': existing.to_dict()
        }, 'View timestamp updated')
    
    try:
        view = ResourceView(
            resource_id=data['resource_id'],
            user_id=data['user_id']
        )
        
        db.session.add(view)
        
        # Increment resource view count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(data['resource_id'])
        if resource:
            resource.increment_views()
        
        db.session.commit()
        
        return success_response({
            'view': view.to_dict()
        }, 'Resource view recorded successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to record view: {str(e)}', 500)

@resource_views_bp.route('/resource/<int:resource_id>/count', methods=['GET'])
def get_resource_view_count(resource_id):
    """Get view count for a resource"""
    count = ResourceView.query.filter_by(resource_id=resource_id).count()
    
    return success_response({
        'resource_id': resource_id,
        'view_count': count
    })

@resource_views_bp.route('/user/<int:user_id>/resource/<int:resource_id>', methods=['GET'])
def check_user_viewed_resource(user_id, resource_id):
    """Check if user has viewed a resource"""
    view = ResourceView.query.filter_by(
        user_id=user_id,
        resource_id=resource_id
    ).first()
    
    return success_response({
        'has_viewed': view is not None,
        'view': view.to_dict() if view else None
    })

@resource_views_bp.route('/analytics/popular', methods=['GET'])
def get_popular_resources():
    """Get most popular resources by views"""
    limit = request.args.get('limit', 10, type=int)
    days = request.args.get('days', 30, type=int)
    
    from sqlalchemy import func
    
    # Calculate date cutoff
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get popular resources
    popular_resources = db.session.query(
        ResourceView.resource_id,
        func.count(ResourceView.id).label('view_count')
    ).filter(
        ResourceView.viewed_at >= cutoff_date
    ).group_by(
        ResourceView.resource_id
    ).order_by(
        func.count(ResourceView.id).desc()
    ).limit(limit).all()
    
    # Get resource details
    from models.knowledge import Knowledge
    result = []
    for resource_id, view_count in popular_resources:
        resource = Knowledge.query.get(resource_id)
        if resource:
            result.append({
                'resource': resource.to_dict(),
                'view_count': view_count
            })
    
    return success_response({
        'popular_resources': result,
        'period_days': days
    })

@resource_views_bp.route('/<int:view_id>', methods=['DELETE'])
def delete_resource_view(view_id):
    """Delete resource view"""
    view = ResourceView.query.get(view_id)
    if not view:
        return error_response('Resource view not found', 404)
    
    try:
        # Decrement resource view count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(view.resource_id)
        if resource and resource.views > 0:
            resource.views -= 1
            db.session.commit()
        
        db.session.delete(view)
        db.session.commit()
        
        return success_response(message='View record deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete view record: {str(e)}', 500)