from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.Enums import UserStatus, Privacy, Theme, EmailDigest
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
def get_users():
    """Get all users with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=str)
    role = request.args.get('role', type=str)
    search = request.args.get('search', type=str)
    
    query = User.query
    
    # Apply filters
    if status:
        query = query.filter(User.status == UserStatus(status))
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'users': [user.to_dict() for user in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user by ID"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    return success_response({'user': user.to_dict()})

@users_bp.route('', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    
    # Check required fields
    required_fields = ['first_name', 'last_name', 'email', 'password']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: first_name, last_name, email, password')
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return error_response('Email already exists', 409)
    
    try:
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password']  # Should be hashed in production
        )
        
        # Optional fields
        if 'role' in data:
            user.role = data['role']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        if 'profile_bio' in data:
            user.profile_bio = data['profile_bio']
        if 'profile_company' in data:
            user.profile_company = data['profile_company']
        
        db.session.add(user)
        db.session.commit()
        
        return success_response({'user': user.to_dict()}, 'User created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create user: {str(e)}', 500)

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    data = request.get_json()
    
    try:
        # Update basic fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing_user:
                return error_response('Email already taken by another user', 409)
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        
        # Update profile
        if 'profile' in data:
            user.update_profile(data['profile'])
        
        # Update preferences
        if 'preferences' in data:
            user.update_preferences(data['preferences'])
        
        # Update notification settings
        if 'notificationSettings' in data:
            user.update_notification_settings(data['notificationSettings'])
        
        db.session.commit()
        
        return success_response({'user': user.to_dict()}, 'User updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update user: {str(e)}', 500)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    try:
        db.session.delete(user)
        db.session.commit()
        
        return success_response(message='User deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete user: {str(e)}', 500)

@users_bp.route('/<int:user_id>/activity', methods=['POST'])
def update_user_activity(user_id):
    """Update user's last activity and streak"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    try:
        user.update_last_activity()
        return success_response({'user': user.to_dict()}, 'Activity updated successfully')
    except Exception as e:
        return error_response(f'Failed to update activity: {str(e)}', 500)

@users_bp.route('/<int:user_id>/xp', methods=['POST'])
def add_user_xp(user_id):
    """Add XP points to user"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    data = request.get_json()
    points = data.get('points', 0)
    
    if points <= 0:
        return error_response('Points must be positive', 400)
    
    try:
        user.add_xp_points(points)
        return success_response({'user': user.to_dict()}, f'{points} XP points added successfully')
    except Exception as e:
        return error_response(f'Failed to add XP points: {str(e)}', 500)

@users_bp.route('/<int:user_id>/verify-email', methods=['POST'])
def verify_user_email(user_id):
    """Verify user's email"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    try:
        user.verify_email()
        return success_response({'user': user.to_dict()}, 'Email verified successfully')
    except Exception as e:
        return error_response(f'Failed to verify email: {str(e)}', 500)

@users_bp.route('/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    """Update user status (active/inactive)"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['active', 'inactive']:
        return error_response('Status must be "active" or "inactive"', 400)
    
    try:
        if status == 'active':
            user.activate()
        else:
            user.deactivate()
        
        return success_response({'user': user.to_dict()}, f'User status updated to {status}')
    except Exception as e:
        return error_response(f'Failed to update status: {str(e)}', 500)