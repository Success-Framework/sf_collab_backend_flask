from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.accessRequest import AccessRequest
from app.models.permission import Permission
from app.extensions import db
from datetime import datetime
from app.utils.helper import error_response, success_response, paginate

access_requests_bp = Blueprint('access_requests', __name__)

@access_requests_bp.route('', methods=['GET'])
@jwt_required()
def get_access_requests():
    """Get all access requests with filtering"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    permission_id = request.args.get('permission_id', type=int)
    status = request.args.get('status', type=str)
    
    query = AccessRequest.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if permission_id:
        query = query.filter_by(permission_id=permission_id)
    
    if status:
        query = query.filter_by(status=status)
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'access_requests': [ar.to_dict(include_user_info=True) for ar in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@access_requests_bp.route('/<int:request_id>', methods=['GET'])
@jwt_required()
def get_access_request(request_id):
    """Get single access request by ID"""
    access_request = AccessRequest.query.get(request_id)
    if not access_request:
        return error_response('Access request not found', 404)
    
    return success_response({
        'access_request': access_request.to_dict(include_user_info=True)
    })

@access_requests_bp.route('', methods=['POST'])
@jwt_required()
def create_access_request():
    """Create new access request"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    
    required_fields = ['permission_id', 'reason']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: permission_id, reason')
    
    # Check if permission exists
    permission = Permission.query.get(data['permission_id'])
    if not permission:
        return error_response('Permission not found', 404)
    
    # Check if user already has this permission
    from app.models.userPermission import UserPermission
    existing_permission = UserPermission.query.filter_by(
        user_id=current_user_id,
        permission_id=data['permission_id']
    ).first()
    
    if existing_permission and existing_permission.is_active():
        return error_response('You already have this permission', 400)
    
    # Check for pending request
    pending_request = AccessRequest.query.filter_by(
        user_id=current_user_id,
        permission_id=data['permission_id'],
        status='pending'
    ).first()
    
    if pending_request:
        return error_response('You already have a pending request for this permission', 400)
    
    try:
        access_request = AccessRequest(
            user_id=current_user_id,
            permission_id=data['permission_id'],
            reason=data['reason'],
            expires_at=datetime.fromisoformat(data['expires_at']) if 'expires_at' in data and data['expires_at'] else None
        )
        
        db.session.add(access_request)
        db.session.commit()
        
        return success_response({
            'access_request': access_request.to_dict(include_user_info=True)
        }, 'Access request submitted successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to submit access request: {str(e)}', 500)

@access_requests_bp.route('/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def approve_access_request(request_id):
    """Approve access request"""
    current_user_id = get_jwt_identity()
    
    access_request = AccessRequest.query.get(request_id)
    if not access_request:
        return error_response('Access request not found', 404)
    
    if access_request.status != 'pending':
        return error_response(f'Access request is already {access_request.status}', 400)
    
    data = request.get_json()
    
    try:
        expires_at = None
        if 'expires_at' in data and data['expires_at']:
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        # Approve the request
        user_permission = access_request.approve(
            reviewer_id=current_user_id,
            expires_at=expires_at
        )
        
        return success_response({
            'access_request': access_request.to_dict(include_user_info=True),
            'user_permission': user_permission.to_dict(include_user_info=True)
        }, 'Access request approved successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to approve access request: {str(e)}', 500)

@access_requests_bp.route('/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_access_request(request_id):
    """Reject access request"""
    current_user_id = get_jwt_identity()
    
    access_request = AccessRequest.query.get(request_id)
    if not access_request:
        return error_response('Access request not found', 404)
    
    if access_request.status != 'pending':
        return error_response(f'Access request is already {access_request.status}', 400)
    
    data = request.get_json()
    
    try:
        rejection_reason = data.get('rejection_reason')
        access_request.reject(
            reviewer_id=current_user_id,
            reason=rejection_reason
        )
        
        return success_response({
            'access_request': access_request.to_dict(include_user_info=True)
        }, 'Access request rejected successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reject access request: {str(e)}', 500)

@access_requests_bp.route('/my-requests', methods=['GET'])
@jwt_required()
def get_my_access_requests():
    """Get current user's access requests"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=str)
    
    query = AccessRequest.query.filter_by(user_id=current_user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'access_requests': [ar.to_dict(include_user_info=False) for ar in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })