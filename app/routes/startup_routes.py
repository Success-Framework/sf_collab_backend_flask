from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.startup import Startup
from app.models.startup_document import StartupDocument
from app.models.startUpMember import StartupMember
from app.models.user import User
from app.models.joinRequest import JoinRequest
from app.models.Enums import JoinRequestStatus
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from app.models.userRole import UserRole
import os 
from io import BytesIO
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import shutil
from app.utils.startup_permissions import (
    get_current_user_startup_role,
    can_view_full_details,
    can_manage_documents,
    can_manage_members,
    can_edit_startup_core_info
)


startups_bp = Blueprint('startups', __name__)

# Upload configurations
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'startups')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file, max_size=MAX_FILE_SIZE):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size

def generate_unique_filename(original_filename):
    """Generate unique filename to avoid conflicts"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    random_str = os.urandom(4).hex()
    file_extension = os.path.splitext(original_filename)[1]
    return f"{timestamp}_{random_str}{file_extension}"

#! FOR EVERYONE (Public - no auth required)
@startups_bp.route('', methods=['GET'])
@jwt_required()
def get_startups():
    """Get all startups with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    industry = request.args.get('industry', type=str)
    stage = request.args.get('stage', type=str)
    search = request.args.get('search', type=str)
    # New funding range parameters
    min_funding = request.args.get('min_funding', type=float)
    max_funding = request.args.get('max_funding', type=float)
    
    query = Startup.query
     # Apply filters
    if industry:
        query = query.filter(Startup.industry.ilike(f'%{industry}%'))
    if stage:
        query = query.filter(Startup.stage == stage)
    if search:
        query = query.filter(
            (Startup.name.ilike(f'%{search}%')) |
            (Startup.description.ilike(f'%{search}%'))
        )
    
    if min_funding is not None:
        query = query.filter(Startup.funding_amount >= min_funding)
    if max_funding is not None:
        query = query.filter(Startup.funding_amount <= max_funding)
    
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'startups': [startup.to_dict() for startup in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

#! GET SINGLE STARTUP (Public - no auth required)
@startups_bp.route('/<int:startup_id>', methods=['GET'])
@jwt_required()
def get_startup(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    startup.increment_views()

    role = get_current_user_startup_role(startup_id)

    if role == 'none':
        # Very limited view for normal logged-in users
        data = {
            'id': startup.id,
            'name': startup.name,
            'industry': startup.industry,
            'stage': startup._enum_to_value(startup.stage),
            'description': (startup.description or '')[:350] + '...',
            'logo_url': startup.logo_url,
            'banner_url': startup.banner_url,
            'member_count': startup.member_count,
            'views': startup.views,
            'createdAt': startup.created_at.isoformat(),
            'access_level': 'public_limited'
        }
    else:
        # Full view for anyone related to the startup
        data = startup.to_dict()
        data['access_level'] = role

    return success_response({'startup': data})

#! REGISTER NEW STARTUP
@startups_bp.route('/register', methods=['POST'])
@jwt_required()
def register_startup():
    """Register new startup with file uploads to file system"""
    current_user_id = get_jwt_identity()
    
    try:
        # Check if request has form data
        print("FORM:", request.form)
        print("FILES:", request.files)

        if not request.form:
            return error_response('Form data required', 400)
        
        data = request.form
        files = request.files
        
        required_fields = ['name', 'industry']
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields')
        
        # Check if startup name already exists
        if Startup.query.filter_by(name=data['name']).first():
            return error_response('Startup name already exists', 409)
        
        # Get current user info
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('User not found', 404)
        
        # Parse roles if it's a string (JSON)
        roles_data = data.get('roles', {})
        if isinstance(roles_data, str):
            try:
                roles_data = json.loads(roles_data)
            except json.JSONDecodeError:
                roles_data = {}
        
        # Parse tech stack if provided
        tech_stack_data = data.get('tech_stack', [])
        if isinstance(tech_stack_data, str):
            try:
                tech_stack_data = json.loads(tech_stack_data)
            except json.JSONDecodeError:
                tech_stack_data = []
        
        # Calculate total positions from roles data
        total_positions = 0
        if roles_data:
            # If roles_data is a dictionary with role objects containing positionsNumber
            for role_key, role_value in roles_data.items():
                if isinstance(role_value, dict) and 'positionsNumber' in role_value:
                    total_positions += int(role_value.get('positionsNumber', 0))
                else:
                    # Fallback: count each role as 1 position
                    total_positions += 1
        else:
            # Fallback to form data positions
            total_positions = int(data.get('positions', 0))
        
        # Create startup first to get ID
        startup = Startup(
            name=data['name'],
            industry=data['industry'],
            location=data.get('location'),
            description=data.get('description'),
            stage=data.get('stage', 'idea'),
            positions=total_positions,  # Use calculated total positions
            roles=roles_data,
            
            tech_stack=tech_stack_data,
            
            revenue=float(data.get('revenue', 0)),
            funding_amount=float(data.get('funding_amount', 0)),
            funding_round=data.get('funding_round', 'pre-seed'),
            burn_rate=float(data.get('burn_rate', 0)),
            runway_months=int(data.get('runway_months', 0)),
            valuation=float(data.get('valuation', 0)),
            financial_notes=data.get('financial_notes', ''),
            creator_id=current_user_id,
            creator_first_name=current_user.first_name,
            creator_last_name=current_user.last_name
        )
        
        db.session.add(startup)
        db.session.commit()
        
        # Create startup-specific upload directory
        startup_upload_dir = os.path.join(UPLOAD_FOLDER, str(startup.id))
        os.makedirs(startup_upload_dir, exist_ok=True)
        
        # Handle logo upload to file system
        if 'logo' in files:
            logo_file = files['logo']
            if logo_file and logo_file.filename != '' and allowed_file(logo_file.filename):
                if validate_file_size(logo_file):
                    filename = secure_filename(logo_file.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
                    logo_path = os.path.join(startup_upload_dir, unique_filename)
                    logo_file.save(logo_path)
                    
                    # Save both local path (for existing routes) and URL path
                    startup.logo_path = logo_path
                    startup.logo_url = f"/startups/{startup.id}/logo"  # URL for frontend
                    startup.logo_content_type = logo_file.content_type
        
        # Handle banner upload to file system
        if 'banner' in files:
            banner_file = files['banner']
            if banner_file and banner_file.filename != '' and allowed_file(banner_file.filename):
                if validate_file_size(banner_file):
                    filename = secure_filename(banner_file.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
                    banner_path = os.path.join(startup_upload_dir, unique_filename)
                    banner_file.save(banner_path)
                    
                    # Save both local path (for existing routes) and URL path
                    startup.banner_path = banner_path
                    startup.banner_url = f"/startups/{startup.id}/banner"  # URL for frontend
                    startup.banner_content_type = banner_file.content_type

        # Handle document uploads to file system
        document_files = files.getlist('documents')
        for doc_file in document_files:
            if doc_file and doc_file.filename != '' and allowed_file(doc_file.filename):
                if validate_file_size(doc_file):
                    filename = secure_filename(doc_file.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
                    doc_path = os.path.join(startup_upload_dir, unique_filename)
                    doc_file.save(doc_path)
                    
                    # For documents, we'll use the existing download route
                    file_url = f"/startups/{startup.id}/documents/{unique_filename}"
                    
                    startup.add_document(
                        filename=doc_file.filename,
                        file_path=doc_path,  # Keep local path for existing download route
                        file_url=file_url,
                        content_type=doc_file.content_type,
                        document_type=data.get('document_type', 'general')
                    )
        
        # Add user to userRoles as founder
        new_user_role = UserRole(
            user_id=current_user_id,
            role='founder'
        )
        db.session.add(new_user_role)
        db.session.commit()
        
        # Add creator as first member
        startup.add_member(
            current_user_id,
            current_user.first_name,
            current_user.last_name,
            'founder'
        )
        
        
        return success_response({
            'startup': startup.to_dict(),
            'role': 'founder'
            }, 'Startup created successfully', 201)
        
    except Exception as e:
        db.session.rollback()
        # Clean up uploaded files if registration fails
        if 'startup' in locals() and startup.id:
            startup_upload_dir = os.path.join(UPLOAD_FOLDER, str(startup.id))
            if os.path.exists(startup_upload_dir):
                shutil.rmtree(startup_upload_dir)
        return error_response(f'Failed to create startup: {str(e)}', 500)

#! UPDATE STARTUP
@startups_bp.route('/<int:startup_id>', methods=['PUT'])
@jwt_required()
def update_startup(startup_id):
    """Update startup"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get(startup_id)
    if not startup:
        return error_response('Startup not found', 404)
    
    # Check if user is authorized to update this startup
    if not can_edit_startup_core_info(startup_id):
        return error_response("Only the startup owner can update core information", 403)
    
    data = request.get_json()
    
    try:
        # Basic startup info
        if 'name' in data:
            # Check if name is being changed and if new name already exists
            if data['name'] != startup.name and Startup.query.filter_by(name=data['name']).first():
                return error_response('Startup name already exists', 409)
            startup.name = data['name']
        if 'industry' in data:
            startup.industry = data['industry']
        if 'location' in data:
            startup.location = data['location']
        if 'description' in data:
            startup.description = data['description']
        if 'stage' in data:
            startup.update_stage(data['stage'])
        if 'positions' in data:
            startup.positions = data['positions']
        if 'roles' in data:
            startup.roles = data['roles']
        
        # Financial fields
        if 'revenue' in data:
            startup.revenue = float(data['revenue']) if data['revenue'] is not None else 0.0
        if 'funding_amount' in data:
            startup.funding_amount = float(data['funding_amount']) if data['funding_amount'] is not None else 0.0
        if 'funding_round' in data:
            startup.funding_round = data['funding_round']
        if 'burn_rate' in data:
            startup.burn_rate = float(data['burn_rate']) if data['burn_rate'] is not None else 0.0
        if 'runway_months' in data:
            startup.runway_months = int(data['runway_months']) if data['runway_months'] is not None else 0
        if 'valuation' in data:
            startup.valuation = float(data['valuation']) if data['valuation'] is not None else 0.0
        if 'financial_notes' in data:
            startup.financial_notes = data['financial_notes']
        
        if 'tech_stack' in data:
            startup.tech_stack = data['tech_stack']
            
        # Recalculate total positions if roles are updated
        if 'roles' in data and data['roles']:
            total_positions = 0
            roles_data = data['roles']
            
            # Handle both old and new roles structure
            for role_key, role_value in roles_data.items():
                if isinstance(role_value, dict):
                    # New structure: { "Role Title": { "roleType": "Full Time", "positionsNumber": 2 } }
                    positions = role_value.get('positionsNumber', 1)
                    total_positions += int(positions) if positions is not None else 1
                else:
                    # Old structure: { "Role Title": "Full Time" } - count as 1 position per role
                    total_positions += 1
            
            startup.positions = total_positions
        
        db.session.commit()
        return success_response({'startup': startup.to_dict()}, 'Startup updated successfully')
    except ValueError as e:
        db.session.rollback()
        return error_response(f'Invalid data format: {str(e)}', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update startup: {str(e)}', 500)
        
#! GET STARTUP MEMBERS
@startups_bp.route('/<int:startup_id>/members', methods=['GET'])
@jwt_required()
def get_startup_members(startup_id):
    """Get startup members"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get(startup_id)
    if not startup:
        return error_response('Startup not found', 404)
    
    # Check if user has access to this startup
    if not can_view_full_details(startup_id):
        return error_response("You need to be a member to see the team", 403)
    
    members = startup.get_active_members()
    return success_response({
        'members': [member.to_dict() for member in members]
    })

#! ADD STARTUP MEMBER
@startups_bp.route('/<int:startup_id>/members', methods=['POST'])
@jwt_required()
def add_startup_member(startup_id):
    """Add member to startup"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get(startup_id)
    if not startup:
        return error_response('Startup not found', 404)
    
    # Check if user is authorized to add members
    if not can_manage_members(startup_id):
        return error_response("Only owner or founder can add members", 403)
    
    data = request.get_json()
    required_fields = ['user_id', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, first_name, last_name')
    
    try:
        member = startup.add_member(
            data['user_id'],
            data['first_name'],
            data['last_name'],
            data.get('role', 'member')
        )
        return success_response({'member': member.to_dict()}, 'Member added successfully')
    except Exception as e:
        return error_response(f'Failed to add member: {str(e)}', 500)

#! REMOVE STARTUP MEMBER
@startups_bp.route('/<int:startup_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_startup_member(startup_id, member_id):
    """Remove member from startup"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get(startup_id)
    if not startup:
        return error_response('Startup not found', 404)
    
    # Check if user is authorized to remove members
    if not has_startup_management_access(current_user_id, startup_id):
        return error_response('Unauthorized to remove members from this startup', 403)
    
    try:
        startup.remove_member(member_id)
        return success_response(message='Member removed successfully')
    except Exception as e:
        return error_response(f'Failed to remove member: {str(e)}', 500)

#! DELETE STARTUP
@startups_bp.route('/<int:startup_id>', methods=['DELETE'])
@jwt_required()
def delete_startup(startup_id):
    """Delete startup and all associated files"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get(startup_id)
    if not startup:
        return error_response('Startup not found', 404)
    
    # Check if user is authorized to delete this startup
    if not has_startup_management_access(current_user_id, startup_id):
        return error_response('Unauthorized to delete this startup', 403)
    
    try:
        # Delete associated files from file system
        startup_upload_dir = os.path.join(UPLOAD_FOLDER, str(startup_id))
        if os.path.exists(startup_upload_dir):
            shutil.rmtree(startup_upload_dir)
        
        # Delete from database
        db.session.delete(startup)
        db.session.commit()
        return success_response(message='Startup deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete startup: {str(e)}', 500)

#! GET STARTUP LOGO (Public - no auth required)
@startups_bp.route('/<int:startup_id>/logo')
def get_startup_logo(startup_id):
    """Get startup logo from file system"""
    startup = Startup.query.get_or_404(startup_id)
    if not startup.logo_path or not os.path.exists(startup.logo_path):
        return error_response('Logo not found', 404)
    
    return send_file(
        startup.logo_path,
        mimetype=startup.logo_content_type,
        as_attachment=False,
        download_name=f'logo_{startup.name}{os.path.splitext(startup.logo_path)[1]}'
    )

#! GET STARTUP BANNER (Public - no auth required)
@startups_bp.route('/<int:startup_id>/banner')
def get_startup_banner(startup_id):
    """Get startup banner from file system"""
    startup = Startup.query.get_or_404(startup_id)
    if not startup.banner_path or not os.path.exists(startup.banner_path):
        return error_response('Banner not found', 404)
    
    return send_file(
        startup.banner_path,
        mimetype=startup.banner_content_type,
        as_attachment=False,
        download_name=f'banner_{startup.name}{os.path.splitext(startup.banner_path)[1]}'
    )

#! GET STARTUP DOCUMENTS
@startups_bp.route('/<int:startup_id>/documents', methods=['GET'])
@jwt_required()
def get_startup_documents(startup_id):
    """Get all startup documents"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get_or_404(startup_id)
    
    # Check if user has access to this startup
    if not can_view_full_details(startup_id):
        return error_response("You need to be a member of this startup to view documents", 403)
    # if not has_startup_access(current_user_id, startup_id):
    #     return error_response('Unauthorized to access this startup documents', 403)
    
    documents = [doc.to_dict() for doc in startup.get_documents()]
    return success_response({'documents': documents})

#! SERVE STARTUP FILE (Public - no auth required)
@startups_bp.route('/uploads/<int:startup_id>/<filename>', methods=['GET'])
def serve_startup_file(startup_id, filename):
    """Serve uploaded startup files directly"""
    try:
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)
        
        # Security check
        file_path = os.path.join(UPLOAD_FOLDER, str(startup_id), filename)
        
        if not os.path.exists(file_path):
            return error_response('File not found', 404)
        
        # Check if file is in the startup's upload directory
        expected_dir = os.path.join(UPLOAD_FOLDER, str(startup_id))
        if not os.path.commonpath([file_path, expected_dir]) == expected_dir:
            return error_response('Access denied', 403)
        
        return send_file(file_path)
        
    except Exception as e:
        return error_response(f'Failed to serve file: {str(e)}', 500)
        
#! DOWNLOAD DOCUMENT
@startups_bp.route('/<int:startup_id>/documents/<int:document_id>/download')
@jwt_required()
def download_document(startup_id, document_id):
    """Download a specific document from file system"""
    current_user_id = get_jwt_identity()
    
    document = StartupDocument.query.filter_by(id=document_id, startup_id=startup_id).first_or_404()
    
    # Check if user has access to this startup
    if not has_startup_access(current_user_id, startup_id):
        return error_response('Unauthorized to download this document', 403)
    
    if not os.path.exists(document.file_path):
        return error_response('File not found on server', 404)
    
    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.filename
    )

#! UPLOAD DOCUMENT
@startups_bp.route('/<int:startup_id>/documents', methods=['POST'])
@jwt_required()
def upload_document(startup_id):
    """Upload additional documents to startup"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get_or_404(startup_id)
    if not can_manage_documents(startup_id):
        return error_response("Only owner or founder can upload documents", 403)
    # Check if user is authorized to upload documents
    if not has_startup_management_access(current_user_id, startup_id):
        return error_response('Unauthorized to upload documents to this startup', 403)
    
    if 'document' not in request.files:
        return error_response('No document provided')
    
    document_file = request.files['document']
    if document_file.filename == '':
        return error_response('No file selected')
    
    if not allowed_file(document_file.filename):
        return error_response('File type not allowed')
    
    if not validate_file_size(document_file):
        return error_response('File size too large')
    
    try:
        # Create startup upload directory if it doesn't exist
        startup_upload_dir = os.path.join(UPLOAD_FOLDER, str(startup_id))
        os.makedirs(startup_upload_dir, exist_ok=True)
        
        # Save file to file system
        unique_filename = generate_unique_filename(document_file.filename)
        doc_path = os.path.join(startup_upload_dir, unique_filename)
        document_file.save(doc_path)
        
        # Create document with file_url
        file_url = f"/api/startups/uploads/{startup_id}/{unique_filename}"
        
        document = StartupDocument(
            startup_id=startup_id,
            filename=document_file.filename,
            file_path=doc_path,
            file_url=file_url,  # Set the file_url
            content_type=document_file.content_type,
            document_type=request.form.get('document_type', 'general'),
            file_size=os.path.getsize(doc_path) if os.path.exists(doc_path) else 0
        )
        db.session.add(document)
        db.session.commit()
        
        return success_response({'document': document.to_dict()}, 'Document uploaded successfully')
    except Exception as e:
        return error_response(f'Failed to upload document: {str(e)}', 500)
        
#! DELETE DOCUMENT
@startups_bp.route('/<int:startup_id>/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(startup_id, document_id):
    """Delete a document from startup"""
    current_user_id = get_jwt_identity()
    
    document = StartupDocument.query.filter_by(id=document_id, startup_id=startup_id).first_or_404()
    
    # Check if user is authorized to delete documents
    if not can_manage_documents(startup_id):
        return error_response("Only owner or founder can delete documents", 403)
    
    try:
        # Delete file from file system
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        return success_response(message='Document deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete document: {str(e)}', 500)

#! GET USER'S STARTUPS
@startups_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_startups(user_id):
    """Get all startups created by a specific user"""
    current_user_id = get_jwt_identity()
    
    # Users can only see their own startups unless they're admin
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users startups', 403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Startup.query.filter_by(creator_id=user_id)
    result = paginate(query, page, per_page)
    
    return success_response({
        'startups': [startup.to_dict() for startup in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

#! GET STARTUP STATS
@startups_bp.route('/<int:startup_id>/stats', methods=['GET'])
@jwt_required()
def get_startup_stats(startup_id):
    """Get startup statistics"""
    current_user_id = get_jwt_identity()
    
    startup = Startup.query.get_or_404(startup_id)
    
    # Check if user has access to this startup
    if not has_startup_access(current_user_id, startup_id):
        return error_response('Unauthorized to access this startup stats', 403)
    
    stats = {
        'views': startup.views,
        'member_count': startup.member_count,
        'positions': startup.positions,
        'created_at': startup.created_at.isoformat(),
        'stage': startup._enum_to_value(startup.stage)
    }
    
    return success_response({'stats': stats})

#! GET AVAILABLE INDUSTRIES AND STAGES (Public - no auth required)
@startups_bp.route('/industries', methods=['GET'])
def get_industries():
    """Get list of all available industries"""
    industries = db.session.query(Startup.industry).distinct().all()
    industry_list = [industry[0] for industry in industries if industry[0]]
    
    return success_response({'industries': industry_list})

@startups_bp.route('/stages', methods=['GET'])
def get_stages():
    """Get list of all available startup stages"""
    from app.models.startup import StartupStage
    stages = [stage.value for stage in StartupStage]
    
    return success_response({'stages': stages})


@startups_bp.route('/<int:startup_id>/join-requests', methods=['GET'])
@jwt_required()
def get_join_requests(startup_id):
    """
    Get all join requests for a startup (pending + processed)
    Only owner or founder members can see this
    """
    if not can_manage_members(startup_id):
        return error_response(
            "Only the startup owner or founders can view join requests", 
            403
        )

    startup = Startup.query.get_or_404(startup_id)

    # Optional: filter by status
    status_filter = request.args.get('status', 'pending')  # default: pending
    valid_statuses = ['pending', 'approved', 'rejected', 'cancelled', 'all']
    if status_filter not in valid_statuses:
        status_filter = 'pending'

    query = startup.join_requests
    if status_filter != 'all':
        query = query.filter_by(status=JoinRequestStatus(status_filter))

    requests = query.order_by(JoinRequest.created_at.desc()).all()

    return success_response({
        'requests': [req.to_dict() for req in requests],
        'count': len(requests),
        'filter': status_filter,
        'current_user_role': get_current_user_startup_role(startup_id)
    })

@startups_bp.route('/<int:startup_id>/join-requests/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_join_request(startup_id, request_id):
    """
    Accept a pending join request and automatically add the user as a member
    """
    if not can_manage_members(startup_id):
        return error_response(
            "Only the startup owner or founders can accept join requests", 
            403
        )

    join_request = JoinRequest.query.filter_by(
        id=request_id,
        startup_id=startup_id,
        status=JoinRequestStatus.pending
    ).first()

    if not join_request:
        return error_response("Join request not found or already processed", 404)

    try:
        # The approve method already handles adding the member
        new_member = join_request.approve()

        return success_response({
            'message': "Join request accepted. User added as team member.",
            'new_member': {
                'userId': new_member.user_id,
                'role': new_member.role,
                'joinedAt': new_member.joined_at.isoformat() if hasattr(new_member, 'joined_at') else None
            }
        }, status=200)

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to accept request: {str(e)}", 500)

@startups_bp.route('/<int:startup_id>/join-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_join_request(startup_id, request_id):
    """
    Reject a pending join request
    """
    if not can_manage_members(startup_id):
        return error_response(
            "Only the startup owner or founders can reject join requests", 
            403
        )

    join_request = JoinRequest.query.filter_by(
        id=request_id,
        startup_id=startup_id,
        status=JoinRequestStatus.pending
    ).first()

    if not join_request:
        return error_response("Join request not found or already processed", 404)

    try:
        join_request.reject()
        return success_response({
            "message": "Join request rejected successfully",
            "request_id": request_id
        })

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to reject request: {str(e)}", 500)


# Optional: Allow user to cancel their own request
@startups_bp.route('/join-requests/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_my_join_request(request_id):
    """
    Let the requesting user cancel their own pending join request
    """
    current_user_id = get_jwt_identity()
    
    join_request = JoinRequest.query.filter_by(
        id=request_id,
        user_id=current_user_id,
        status=JoinRequestStatus.pending
    ).first()

    if not join_request:
        return error_response("Request not found, not yours, or already processed", 404)

    try:
        join_request.cancel()
        return success_response({
            "message": "Your join request has been cancelled",
            "request_id": request_id
        })

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to cancel request: {str(e)}", 500)

# Helper functions for authorization
def has_startup_access(user_id, startup_id):
    """Check if user has access to view startup data"""
    # Admin users can access all startups
    current_user = User.query.get(user_id)
    if current_user and current_user.role == 'admin':
        return True
    
    # Check if user is a member of the startup
    membership = StartupMember.query.filter_by(
        user_id=user_id, 
        startup_id=startup_id
    ).first()
    
    return membership is not None

def has_startup_management_access(user_id, startup_id):
    """Check if user has permission to manage startup data"""
    # Admin users can manage all startups
    current_user = User.query.get(user_id)
    if current_user and current_user.role == 'admin':
        return True
    
    # Check if user is the creator or has admin/manager role in the startup
    startup = Startup.query.get(startup_id)
    if startup and startup.creator_id == user_id:
        return True
    
    # Check if user is an admin or manager of the startup
    membership = StartupMember.query.filter_by(
        user_id=user_id, 
        startup_id=startup_id
    ).first()
    
    return membership and membership.role in ['admin', 'manager', 'founder', 'owner']