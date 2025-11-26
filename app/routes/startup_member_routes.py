from flask import Blueprint, request, jsonify
from app.models.startUpMember import StartupMember
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

startup_members_bp = Blueprint('startup_members', __name__, url_prefix='/api/startup-members')

@startup_members_bp.route('', methods=['GET'])
def get_startup_members():
    """Get all startup members with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    startup_id = request.args.get('startup_id', type=int)
    user_id = request.args.get('user_id', type=int)
    is_active = request.args.get('is_active', type=bool)
    
    query = StartupMember.query
    
    if startup_id:
        query = query.filter(StartupMember.startup_id == startup_id)
    if user_id:
        query = query.filter(StartupMember.user_id == user_id)
    if is_active is not None:
        query = query.filter(StartupMember.is_active == is_active)
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'members': [member.to_dict() for member in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@startup_members_bp.route('/<int:member_id>', methods=['GET'])
def get_startup_member(member_id):
    """Get single startup member by ID"""
    member = StartupMember.query.get(member_id)
    if not member:
        return error_response('Startup member not found', 404)
    
    return success_response({'member': member.to_dict()})

@startup_members_bp.route('/<int:member_id>/role', methods=['PUT'])
def update_member_role(member_id):
    """Update member role"""
    member = StartupMember.query.get(member_id)
    if not member:
        return error_response('Startup member not found', 404)
    
    data = request.get_json()
    new_role = data.get('role')
    
    if not new_role:
        return error_response('Role is required', 400)
    
    try:
        member.update_role(new_role)
        return success_response({'member': member.to_dict()}, 'Role updated successfully')
    except Exception as e:
        return error_response(f'Failed to update role: {str(e)}', 500)

@startup_members_bp.route('/<int:member_id>/deactivate', methods=['POST'])
def deactivate_member(member_id):
    """Deactivate member"""
    member = StartupMember.query.get(member_id)
    if not member:
        return error_response('Startup member not found', 404)
    
    try:
        member.deactivate()
        return success_response({'member': member.to_dict()}, 'Member deactivated successfully')
    except Exception as e:
        return error_response(f'Failed to deactivate member: {str(e)}', 500)

@startup_members_bp.route('/<int:member_id>/activate', methods=['POST'])
def activate_member(member_id):
    """Activate member"""
    member = StartupMember.query.get(member_id)
    if not member:
        return error_response('Startup member not found', 404)
    
    try:
        member.activate()
        return success_response({'member': member.to_dict()}, 'Member activated successfully')
    except Exception as e:
        return error_response(f'Failed to activate member: {str(e)}', 500)