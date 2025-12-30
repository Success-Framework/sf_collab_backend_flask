from flask import Blueprint, request, jsonify
from app.models.teamMember import TeamMember
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

team_members_bp = Blueprint('team_members', __name__)

@team_members_bp.route('', methods=['GET'])
def get_team_members():
    """Get all team members with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    idea_id = request.args.get('idea_id', type=int)
    
    query = TeamMember.query
    
    if idea_id:
        query = query.filter(TeamMember.idea_id == idea_id)
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'team_members': [member.to_dict() for member in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@team_members_bp.route('/<int:member_id>', methods=['GET'])
def get_team_member(member_id):
    """Get single team member by ID"""
    member = TeamMember.query.get(member_id)
    if not member:
        return error_response('Team member not found', 404)
    
    return success_response({'team_member': member.to_dict()})

@team_members_bp.route('', methods=['POST'])
def create_team_member():
    """Create new team member"""
    data = request.get_json()
    
    required_fields = ['name', 'idea_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: name, idea_id')
    
    try:
        member = TeamMember(
            name=data['name'],
            idea_id=data['idea_id'],
            position=data.get('position'),
            skills=data.get('skills', {})
        )
        
        db.session.add(member)
        db.session.commit()
        
        return success_response({'team_member': member.to_dict()}, 'Team member created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create team member: {str(e)}', 500)

@team_members_bp.route('/<int:member_id>', methods=['PUT'])
def update_team_member(member_id):
    """Update team member"""
    member = TeamMember.query.get(member_id)
    if not member:
        return error_response('Team member not found', 404)
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            member.name = data['name']
        if 'position' in data:
            member.position = data['position']
        if 'skills' in data:
            member.update_skills(data['skills'])
        
        db.session.commit()
        return success_response({'team_member': member.to_dict()}, 'Team member updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update team member: {str(e)}', 500)

@team_members_bp.route('/<int:member_id>/skills', methods=['POST'])
def add_team_member_skill(member_id):
    """Add skill to team member"""
    member = TeamMember.query.get(member_id)
    if not member:
        return error_response('Team member not found', 404)
    
    data = request.get_json()
    skill_name = data.get('skill_name')
    proficiency = data.get('proficiency', 'intermediate')
    
    if not skill_name:
        return error_response('Skill name is required', 400)
    
    try:
        member.add_skill(skill_name, proficiency)
        return success_response({'team_member': member.to_dict()}, 'Skill added successfully')
    except Exception as e:
        return error_response(f'Failed to add skill: {str(e)}', 500)

@team_members_bp.route('/<int:member_id>', methods=['DELETE'])
def delete_team_member(member_id):
    """Delete team member"""
    member = TeamMember.query.get(member_id)
    if not member:
        return error_response('Team member not found', 404)
    
    try:
        db.session.delete(member)
        db.session.commit()
        return success_response(message='Team member deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete team member: {str(e)}', 500)