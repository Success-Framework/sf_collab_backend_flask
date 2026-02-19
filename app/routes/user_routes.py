from flask import Blueprint, request, jsonify, send_from_directory
from app.models.user import User
from app.models.userRole import UserRole
from app.models.Enums import UserStatus, Privacy, Theme, EmailDigest
from app.utils.upload_to_s3 import upload_file_to_s3, get_public_url, generate_presigned_url
from app.extensions import db
from sqlalchemy import func
from app.utils.helper import error_response, success_response, paginate
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity
)
from app.models.Enums import UserRoles
from werkzeug.utils import secure_filename
from datetime import datetime
from app.services.email_service import EmailService
from app.utils.email_templates.email_templates import templates
import os 
email_service = EmailService()
contact_form_email_template = templates.get("contact_form_email")
users_bp = Blueprint('users', __name__)


# Upload configurations
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'user_files')
AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'user_avatars')

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip', 'mp4', 'mov', 'avi'}
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_avatar(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS

def validate_file_size(file, max_size=MAX_FILE_SIZE):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size

#! SAVE UPLOADED FILE
def save_uploaded_file(file, user_id, file_type='file'):
    """Save uploaded file and return file info"""
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{user_id}_{filename}"
    
    if file_type == 'avatar':
        upload_dir = AVATAR_UPLOAD_FOLDER
        max_size = MAX_AVATAR_SIZE
    else:
        upload_dir = UPLOAD_FOLDER
        max_size = MAX_FILE_SIZE
    
    # Validate file size
    if not validate_file_size(file, max_size):
        raise ValueError(f"File size exceeds maximum allowed size of {max_size // (1024 * 1024)}MB")
    
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    
    file_info = {
        'name': filename,
        'size': os.path.getsize(file_path),
        'type': file.content_type,
        'url': f"/uploads/{unique_filename}",
        'path': file_path,
        'filename': unique_filename
    }
    
    return file_info

#! HANDLE FILE UPLOADS
def handle_file_uploads(user_id, user, files):
    """Handle file uploads for user profile"""
    from app.routes.auth_routes import get_user_response_data
    
    uploaded_files = []
    
    try:
        # Handle profile picture upload
        if 'profile_picture' in files:
            file = files['profile_picture']
            if file and file.filename:
                if not allowed_avatar(file.filename):
                    raise ValueError('Invalid avatar file type. Allowed types: png, jpg, jpeg, gif')
                key = upload_file_to_s3(file, folder='uploads/avatars', public=True)
                user.profile_picture = get_public_url(key)
                uploaded_files.append({
                    'type': 'profile_picture',
                    'url': get_public_url(key),
                    'filename': file.filename
                })
        
        # Handle cover photo upload
        if 'cover_photo' in files:
            file = files['cover_photo']
            if file and file.filename:
                if not allowed_avatar(file.filename):
                    raise ValueError('Invalid cover photo file type. Allowed types: png, jpg, jpeg, gif')
                
                key = upload_file_to_s3(file, folder='uploads/avatars', public=True)
                file_info = {
                    'name': file.filename,
                    'url': get_public_url(key)
                }
                # Assuming you have a cover_photo field in your user model
                # If not, you can store it in profile_social_links or add the field
                if hasattr(user, 'cover_photo'):
                    user.cover_photo = file_info['url']
                uploaded_files.append({
                    'type': 'cover_photo',
                    'url': file_info['url'],
                    'filename': file_info['name']
                })
        
        # Handle document uploads
        if 'documents' in files:
            files_list = files.getlist('documents')
            for file in files_list:
                if file and file.filename:
                    if not allowed_file(file.filename):
                        raise ValueError('Invalid document file type')
                    
                    key = upload_file_to_s3(file, folder='uploads/docs', public=False)
                    file_info = {
                        'name': file.filename,
                        'url': generate_presigned_url(key),
                        'size': file.content_length
                    }
                    # Store document info in user profile or create a separate documents table
                    # For now, we'll just track the upload
                    uploaded_files.append({
                        'type': 'document',
                        'url': file_info['url'],
                        'filename': file_info['name'],
                        'size': file_info['size']
                    })
        
        db.session.commit()
        
        response_data = {
            'user': get_user_response_data(user),
            'uploaded_files': uploaded_files
        }
        
        return success_response(response_data, 'User updated successfully with file uploads')
    except Exception as e:
        db.session.rollback()
        for file_info in uploaded_files:
            if os.path.exists(file_info.get('path', '')):
                os.remove(file_info['path'])
        raise e

#! HANDLE USER DATA UPDATE
def handle_user_data_update(user_id, user, data):
    """Handle user data updates from JSON"""
    print(data, "DATA TO UPDATE")
    from app.routes.auth_routes import get_user_response_data
    
    # Update basic fields
    if 'firstName' in data:
        user.first_name = data['firstName']
    if 'lastName' in data:
        user.last_name = data['lastName']
    if 'email' in data:
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == data['email'], User.id != user_id).first()
        if existing_user:
            return error_response('Email already taken by another user', 409)
        user.email = data['email']
    if 'role' in data:
        # Only allow admin users to change roles
        current_user = User.query.get(get_jwt_identity())
        if current_user.role == 'admin':
            user.role = data['role']
    
    # Update computed stats if provided
    if 'xp_points' in data:
        user.xp_points = data['xp_points']
    if 'streak_days' in data:
        user.streak_days = data['streak_days']
    if 'total_revenue' in data:
        user.total_revenue = data['total_revenue']
    if 'satisfaction_percentage' in data:
        user.satisfaction_percentage = data['satisfaction_percentage']
    if 'active_startups_count' in data:
        user.active_startups_count = data['active_startups_count']
    
    # Update profile
    if 'profile' in data:
        user.update_profile(data['profile'])
    if 'status' in data:
        if data['status'] == 'active':
            user.activate()
        elif data['status'] == 'inactive':
            user.deactivate()
        elif data['status'] == 'banned':
            user.status = UserStatus.banned
    # Update preferences
    
    # Update notification settings
    if 'notificationSettings' in data:
        user.update_notification_settings(data['notificationSettings'])
    
    # Update password if provided
    if 'password' in data and 'currentPassword' in data:
        update_user_password(user, data['currentPassword'], data['password'])
    if 'roles' in data:
        # Only allow admin users to change roles
        current_user = User.query.get(get_jwt_identity())
        if current_user.is_admin() or current_user.id == user.id:

            # Delete all existing roles first
            UserRole.query.filter_by(user_id=user.id).delete()
            # Add new roles
            for role in data['roles']:
                userRole = UserRole(
                    user_id=user.id,
                    role=role
                )
                db.session.add(userRole)
    if 'preferences' in data:
        user.update_preferences(data['preferences'])

    db.session.commit()
    db.session.refresh(user)
    return success_response({'user': get_user_response_data(user)}, 'User updated successfully')

#! UPDATE USER PASSWORD
def update_user_password(user, current_password, new_password):
    """Update user password with validation"""
    if not user.check_password(current_password):
        raise ValueError('Current password is incorrect')
    
    if len(new_password) < 6:
        raise ValueError('New password must be at least 6 characters long')
    
    user.set_password(new_password)

#! SERVE UPLOADED FILES
@users_bp.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

#! SERVE AVATAR FILES
@users_bp.route('/avatars/<filename>')
def serve_avatar_file(filename):
    """Serve avatar files"""
    return send_from_directory(AVATAR_UPLOAD_FOLDER, filename)
    
    
#! GET ALL USERS WITH PAGINATION AND FILTERING
@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=str)
    role = request.args.get('role', type=str)
    search = request.args.get('search', type=str)
    query = User.query
    if page == 1:
        query = query.order_by(User.created_at.desc())
    else:
        query = query.order_by(
            User.created_at.desc(),
            func.random()
        )
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
        'users': [user.to_dict(public=True) for user in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

#! GET SINGLE USER BY ID
@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get single user by ID"""
    user = User.query.get(user_id)
    include_stats = request.args.get('include_stats', 'false').lower() == 'true'
    if not user:
        return error_response('User not found', 404)
    
    # Check if the requesting user is viewing their own profile
    current_user_id = get_jwt_identity()
    is_own_profile = int(current_user_id) == int(user_id)
    
    return success_response({'user': user.to_dict(include_statistics=include_stats, public=not is_own_profile)}, 'User retrieved successfully')

#! CREATE NEW USER
@users_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """Create new user"""
    data = request.get_json()
    user_id = get_jwt_identity()
    if not user_id:
        return error_response('Unauthorized', 401)

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
            email=data['email']
        )
        
        user.set_password(data['password'])
        
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

#! UPDATE USER
@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user with file upload support"""
    current_user_id = get_jwt_identity()
    
    # Check if user is updating their own profile or is admin
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    # Authorization check - users can only update their own profile unless they're admin
    current_user = User.query.get(current_user_id)
    isAdmin = current_user.is_admin() if current_user else False
    if int(user_id) != int(current_user_id) and not isAdmin:
        return error_response('Unauthorized to update this user', 403)
    
    try:
        # Check if request contains files
        if request.files:
            return handle_file_uploads(user_id, user, request.files)
        
        # Handle JSON data updates
        if not request.get_json(silent=True):
            data = request.form.to_dict()
        else:
            data = request.get_json()  
        return handle_user_data_update(user_id, user, data)
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update user: {str(e)}', 500)

#! DELETE USER
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user"""
    token_user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if int(token_user_id) != int(user_id):
        return error_response('Unauthorized to delete this user', 403)
    if not user:
        return error_response('User not found', 404)
    
    try:
        db.session.delete(user)
        db.session.commit()
        
        return success_response(message='User deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete user: {str(e)}', 500)

#! UPDATE USER ACTIVITY AND STREAK
@users_bp.route('/<int:user_id>/activity', methods=['POST'])
@jwt_required()
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

#! ADD XP POINTS TO USER
@users_bp.route('/<int:user_id>/xp', methods=['POST'])
@jwt_required()
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

#! VERIFY USER EMAIL
@users_bp.route('/<int:user_id>/verify-email', methods=['POST'])
@jwt_required()
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
#! GET ALL USER ROLES
@users_bp.route('/roles', methods=['GET'])
def get_user_roles():
    """Get all available user roles"""

    roles = [role.value for role in UserRoles if role.value != 'admin']
    return success_response({'roles': roles})
#! UPDATE USER STATUS
@users_bp.route('/<int:user_id>/status', methods=['PUT'])
@jwt_required()
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
    

# Send email to admin (contact)
@users_bp.route('/contact', methods=['POST'])
def submit_contact_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    print(name, email, message)
    if not name or not email or not message:
        return error_response('Name, email, and message are required', 400)
    
    try:
        # Handle file attachments
        uploaded_files = []
        if 'files' in request.files:
            files_list = request.files.getlist('files')
            for file in files_list:
                if file and file.filename:
                    if not allowed_file(file.filename):
                        return error_response('Invalid file type', 400)
                    
                    if not validate_file_size(file):
                        return error_response('File size exceeds maximum allowed', 400)
                    
                    file_info = save_uploaded_file(file, 0, 'file')
                    uploaded_files.append({
                        'name': file_info['name'],
                        'path': file_info['path'],
                        'size': file_info['size']
                    })
        
        email_service.send_email(
            recipient=os.getenv('SUPPORT_EMAIL'),
            subject=f"New Contact Form Submission from {name}",
            body=contact_form_email_template(
                data={
                    "user": {
                        "name": name,
                        "email": email
                    },
                    "metadata": {
                        "message": message,
                       
                    }
                },
                see_email_template=False
            ),
            attachments=uploaded_files
        )
        return success_response(message='Contact form submitted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to submit contact form: {str(e)}', 500)
@users_bp.route('/my-current-plan', methods=['GET'])
@jwt_required()
def get_plan_id():
    """Get current plan ID for the user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    current_founder_plan = user.founder_plan_id
    current_builder_plan = user.builder_plan_id
    if not current_founder_plan:
        return success_response({'founder_plan': None, 'builder_plan': None}, 'No active plan found')
    
    return success_response({'founder_plan': current_founder_plan, 'builder_plan': current_builder_plan}, 'Current plan retrieved successfully')