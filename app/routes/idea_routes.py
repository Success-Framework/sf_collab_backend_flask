from flask import Blueprint, request, jsonify
from app.models.idea import Idea
from app.models.ideaComment import IdeaComment
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from flask_jwt_extended import jwt_required, get_jwt_identity
ideas_bp = Blueprint('ideas', __name__)

@ideas_bp.route('', methods=['GET'])
@jwt_required()
def get_ideas():
    """Get all ideas with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    industry = request.args.get('industry', type=str)
    stage = request.args.get('stage', type=str)
    creator_id = request.args.get('creator_id', type=int)
    search = request.args.get('search', type=str)
    
    query = Idea.query
    
    if industry:
        query = query.filter(Idea.industry.ilike(f'%{industry}%'))
    if stage:
        query = query.filter(Idea.stage == stage)
    if creator_id:
        query = query.filter(Idea.creator_id == creator_id)
    if search:
        query = query.filter(
            (Idea.title.ilike(f'%{search}%')) |
            (Idea.description.ilike(f'%{search}%')) |
            (Idea.project_details.ilike(f'%{search}%'))
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'ideas': [idea.to_dict() for idea in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@ideas_bp.route('/<int:idea_id>', methods=['GET'])
def get_idea(idea_id):
    """Get single idea by ID"""
    idea = Idea.query.get(idea_id)
    if not idea:
        return error_response('Idea not found', 404)
    
    # Increment views
    idea.increment_views()
    
    include_comments = request.args.get('include_comments', 'false').lower() == 'true'
    
    return success_response({
        'idea': idea.to_dict(include_comments=include_comments)
    })

@ideas_bp.route('', methods=['POST'])
def create_idea():
    """Create new idea"""
    data = request.get_json()
    
    required_fields = ['title', 'description', 'project_details', 'industry', 'stage', 'creator_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        idea = Idea(
            title=data['title'],
            description=data['description'],
            project_details=data['project_details'],
            industry=data['industry'],
            stage=data['stage'],
            tags=data.get('tags', []),
            creator_id=data['creator_id'],
            creator_first_name=data.get('creator_first_name'),
            creator_last_name=data.get('creator_last_name')
        )
        
        db.session.add(idea)
        db.session.commit()
        
        # Check achievements for idea creation
        AchievementService.check_achievements(data['creator_id'], 'ideas_created')
        
        return success_response({
            'idea': idea.to_dict()
        }, 'Idea created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create idea: {str(e)}', 500)

@ideas_bp.route('/<int:idea_id>', methods=['PUT'])
def update_idea(idea_id):
    """Update idea"""
    idea = Idea.query.get(idea_id)
    if not idea:
        return error_response('Idea not found', 404)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            idea.title = data['title']
        if 'description' in data:
            idea.description = data['description']
        if 'project_details' in data:
            idea.project_details = data['project_details']
        if 'industry' in data:
            idea.industry = data['industry']
        if 'stage' in data:
            idea.update_stage(data['stage'])
        if 'tags' in data:
            idea.tags = data['tags']
        
        db.session.commit()
        
        return success_response({
            'idea': idea.to_dict()
        }, 'Idea updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update idea: {str(e)}', 500)

@ideas_bp.route('/<int:idea_id>/like', methods=['POST'])
def like_idea(idea_id):
    """Like an idea"""
    idea = Idea.query.get(idea_id)
    if not idea:
        return error_response('Idea not found', 404)
    
    try:
        idea.increment_likes()
        
        # Check achievements for likes received
        AchievementService.check_achievements(idea.creator_id, 'likes_received')
        
        return success_response({
            'idea': idea.to_dict()
        }, 'Idea liked successfully')
    except Exception as e:
        return error_response(f'Failed to like idea: {str(e)}', 500)

@ideas_bp.route('/<int:idea_id>/team-members', methods=['POST'])
def add_team_member(idea_id):
    """Add team member to idea"""
    idea = Idea.query.get(idea_id)
    if not idea:
        return error_response('Idea not found', 404)
    
    data = request.get_json()
    required_fields = ['name', 'position']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: name, position')
    
    try:
        member = idea.add_team_member(
            name=data['name'],
            position=data['position'],
            skills=data.get('skills')
        )
        
        return success_response({
            'team_member': {
                'name': member.name,
                'position': member.position,
                'skills': member.skills
            }
        }, 'Team member added successfully')
    except Exception as e:
        return error_response(f'Failed to add team member: {str(e)}', 500)

@ideas_bp.route('/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    """Delete idea"""
    idea = Idea.query.get(idea_id)
    if not idea:
        return error_response('Idea not found', 404)
    
    try:
        db.session.delete(idea)
        db.session.commit()
        return success_response(message='Idea deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete idea: {str(e)}', 500)