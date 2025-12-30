from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.permission import Permission
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

permissions_bp = Blueprint('permissions', __name__)

@permissions_bp.route('', methods=['GET'])
@jwt_required()
def get_permissions():
    """Get all permissions with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1000, type=int)
    search = request.args.get('search', type=str)
    
    query = Permission.query
    
    if search:
        query = query.filter(
            (Permission.key.ilike(f'%{search}%')) |
            (Permission.description.ilike(f'%{search}%'))
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'permissions': [permission.to_dict() for permission in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@permissions_bp.route('/<int:permission_id>', methods=['GET'])
@jwt_required()
def get_permission(permission_id):
    """Get single permission by ID"""
    permission = Permission.query.get(permission_id)
    if not permission:
        return error_response('Permission not found', 404)
    
    include_counts = request.args.get('include_counts', 'false').lower() == 'true'
    data = permission.to_dict()
    
    if include_counts:
        data['user_count'] = permission.get_user_count()
        data['pending_requests'] = len(permission.get_pending_requests())
    
    return success_response({
        'permission': data
    })

@permissions_bp.route('', methods=['POST'])
@jwt_required()
def create_permission():
    """Create new permission"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    
    required_fields = ['key', 'description']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: key, description')
    
    # Check if permission key already exists
    if Permission.query.filter_by(key=data['key']).first():
        return error_response('Permission key already exists', 400)
    
    try:
        permission = Permission(
            key=data['key'],
            description=data['description'],
            category=data['category']
        )
        
        db.session.add(permission)
        db.session.commit()
        
        return success_response({
            'permission': permission.to_dict()
        }, 'Permission created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create permission: {str(e)}', 500)

@permissions_bp.route('/<int:permission_id>', methods=['PUT'])
@jwt_required()
def update_permission(permission_id):
    """Update permission"""
    permission = Permission.query.get(permission_id)
    if not permission:
        return error_response('Permission not found', 404)
    
    data = request.get_json()
    
    try:
        if 'key' in data and data['key'] != permission.key:
            # Check if new key already exists
            if Permission.query.filter(Permission.key == data['key'], Permission.id != permission_id).first():
                return error_response('Permission key already exists', 400)
            permission.key = data['key']
        
        if 'description' in data:
            permission.description = data['description']
        
        if 'category' in data:
            permission.category = data['category']
        
        db.session.commit()
        
        return success_response({
            'permission': permission.to_dict()
        }, 'Permission updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update permission: {str(e)}', 500)

@permissions_bp.route('/<int:permission_id>', methods=['DELETE'])
@jwt_required()
def delete_permission(permission_id):
    """Delete permission"""
    permission = Permission.query.get(permission_id)
    if not permission:
        return error_response('Permission not found', 404)
    
    # Check if permission is in use
    if permission.user_permissions.count() > 0:
        return error_response('Cannot delete permission that is assigned to users', 400)
    
    try:
        db.session.delete(permission)
        db.session.commit()
        return success_response(message='Permission deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete permission: {str(e)}', 500)

@permissions_bp.route('/<int:permission_id>/users', methods=['GET'])
@jwt_required()
def get_permission_users(permission_id):
    """Get users with this permission"""
    permission = Permission.query.get(permission_id)
    if not permission:
        return error_response('Permission not found', 404)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    only_active = request.args.get('only_active', 'true').lower() == 'true'
    
    query = permission.user_permissions
    
    if only_active:
        from datetime import datetime
        now = datetime.utcnow()
        query = query.filter(
            (Permission.user_permissions.starts_at == None) | 
            (Permission.user_permissions.starts_at <= now),
            (Permission.user_permissions.expires_at == None) | 
            (Permission.user_permissions.expires_at > now)
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'permission': permission.to_dict(),
        'user_permissions': [up.to_dict(include_user_info=True) for up in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })