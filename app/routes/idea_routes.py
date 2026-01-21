from flask import Blueprint, request
from app.models.idea import Idea
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.waitlist import Waitlist
import datetime
import json
from app.utils.upload_to_s3 import upload_file_to_s3
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
@jwt_required()
def create_idea():
    """Create new idea"""
    user_id = get_jwt_identity()
    
    # Get form data
    title = request.form.get('title')
    description = request.form.get('description')
    project_details = request.form.get('projectDetails')
    industry = request.form.get('industry')
    stage = request.form.get('stage')
    tags = request.form.get('tags')
    image_file = request.files.get('image')
    creator_first_name = request.form.get('creator_first_name')
    creator_last_name = request.form.get('creator_last_name')
    
    required_fields = {'title', 'description', 'projectDetails', 'industry', 'stage'}
    if not all(request.form.get(field) for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        # Parse tags from JSON string
        tags_list = json.loads(tags) if tags else []
        
        idea = Idea(
            title=title,
            description=description,
            project_details=project_details,
            industry=industry,
            stage=stage,
            tags=tags_list,
            creator_id=user_id,
            creator_first_name=creator_first_name,
            creator_last_name=creator_last_name,
        )
        
        # Handle image upload if provided
        if image_file:
            image_url = upload_file_to_s3(image_file, folder='ideas')
            idea.image_url = image_url 
        
        db.session.add(idea)
        waitlist_user = Waitlist.query.filter_by(id=user_id).first()
        if waitlist_user:
            today = datetime.datetime.now(datetime.timezone.utc).date()
            if waitlist_user.last_activity_at is None or waitlist_user.last_activity_at.date() < today:
                waitlist_user.add_points(Waitlist.POINTS_PER_IDEA, 'custom')
        db.session.commit()
        
        # Check achievements for idea creation
        AchievementService.check_achievements(user_id, 'ideas_created')
        
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
    
@ideas_bp.route('/images/<string:filename>', methods=['GET'])
def get_idea_image(filename):
    """Serve idea image files"""
    from flask import send_from_directory
    from app import UPLOAD_FOLDER
    print(UPLOAD_FOLDER, "filename:", filename)
    return send_from_directory(UPLOAD_FOLDER, filename) 
