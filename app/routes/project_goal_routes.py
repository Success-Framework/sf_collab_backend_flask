from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.projectGoal import ProjectGoal
from app.models.goalMilstone import GoalMilestone
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

project_goals_bp = Blueprint('project_goals', __name__, url_prefix='/api/project-goals')

@project_goals_bp.route('', methods=['GET'])
def get_project_goals():
    """Get all project goals with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=str)
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    include_milestones = request.args.get('include_milestones', 'false').lower() == 'true'
    
    query = ProjectGoal.query
    
    if status:
        query = query.filter(ProjectGoal.status == status)
    if user_id:
        query = query.filter(ProjectGoal.user_id == user_id)
    if startup_id:
        query = query.filter(ProjectGoal.startup_id == startup_id)
    
    result = paginate(query.order_by(ProjectGoal.created_at.desc()), page, per_page)
    
    return success_response({
        'project_goals': [goal.to_dict(include_milestones=include_milestones) for goal in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@project_goals_bp.route('/<int:goal_id>', methods=['GET'])
def get_project_goal(goal_id):
    """Get single project goal by ID"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    include_milestones = request.args.get('include_milestones', 'false').lower() == 'true'
    
    return success_response({
        'project_goal': goal.to_dict(include_milestones=include_milestones)
    })

@project_goals_bp.route('', methods=['POST'])
def create_project_goal():
    """Create new project goal"""
    data = request.get_json()
    
    required_fields = ['title', 'user_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: title, user_id')
    
    try:
        goal = ProjectGoal(
            title=data['title'],
            user_id=data['user_id'],
            startup_id=data.get('startup_id'),
            description=data.get('description'),
            milestones_total=data.get('milestones_total', 0),
            target_date=datetime.fromisoformat(data['target_date'].replace('Z', '+00:00')) if data.get('target_date') else None,
            next_milestone=data.get('next_milestone')
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return success_response({
            'project_goal': goal.to_dict()
        }, 'Project goal created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create project goal: {str(e)}', 500)

@project_goals_bp.route('/<int:goal_id>', methods=['PUT'])
def update_project_goal(goal_id):
    """Update project goal"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            goal.title = data['title']
        if 'description' in data:
            goal.description = data['description']
        if 'milestones_total' in data:
            goal.milestones_total = data['milestones_total']
        if 'target_date' in data:
            goal.target_date = datetime.fromisoformat(data['target_date'].replace('Z', '+00:00')) if data['target_date'] else None
        if 'next_milestone' in data:
            goal.next_milestone = data['next_milestone']
        
        goal.update_progress()
        db.session.commit()
        
        return success_response({
            'project_goal': goal.to_dict()
        }, 'Project goal updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update project goal: {str(e)}', 500)

@project_goals_bp.route('/<int:goal_id>/progress', methods=['PUT'])
def update_goal_progress(goal_id):
    """Update goal progress"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    data = request.get_json()
    
    try:
        completed = data.get('milestones_completed')
        total = data.get('milestones_total')
        goal.update_progress(completed, total)
        
        return success_response({
            'project_goal': goal.to_dict()
        }, 'Progress updated successfully')
    except Exception as e:
        return error_response(f'Failed to update progress: {str(e)}', 500)

@project_goals_bp.route('/<int:goal_id>/milestone/complete', methods=['POST'])
def complete_milestone(goal_id):
    """Complete a milestone"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    try:
        goal.complete_milestone()
        return success_response({
            'project_goal': goal.to_dict()
        }, 'Milestone completed successfully')
    except Exception as e:
        return error_response(f'Failed to complete milestone: {str(e)}', 500)

@project_goals_bp.route('/<int:goal_id>/milestones', methods=['POST'])
def add_milestone_to_goal(goal_id):
    """Add milestone to goal"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return error_response('Title is required', 400)
    
    try:
        milestone = goal.add_milestone(
            title=title,
            description=data.get('description'),
            order=data.get('order')
        )
        
        return success_response({
            'milestone': milestone.to_dict(),
            'project_goal': goal.to_dict()
        }, 'Milestone added successfully')
    except Exception as e:
        return error_response(f'Failed to add milestone: {str(e)}', 500)

@project_goals_bp.route('/<int:goal_id>/milestones', methods=['GET'])
def get_goal_milestones(goal_id):
    """Get milestones for a goal"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    completed_only = request.args.get('completed_only', 'false').lower() == 'true'
    
    milestones = goal.get_milestones(completed_only=completed_only)
    
    return success_response({
        'milestones': [milestone.to_dict() for milestone in milestones],
        'goal': goal.to_dict()
    })

@project_goals_bp.route('/<int:goal_id>/status', methods=['PUT'])
def update_goal_status(goal_id):
    """Update goal status"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return error_response('Status is required', 400)
    
    try:
        goal.change_status(new_status)
        return success_response({
            'project_goal': goal.to_dict()
        }, 'Status updated successfully')
    except Exception as e:
        return error_response(f'Failed to update status: {str(e)}', 500)

@project_goals_bp.route('/<int:goal_id>', methods=['DELETE'])
def delete_project_goal(goal_id):
    """Delete project goal"""
    goal = ProjectGoal.query.get(goal_id)
    if not goal:
        return error_response('Project goal not found', 404)
    
    try:
        db.session.delete(goal)
        db.session.commit()
        return success_response(message='Project goal deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete project goal: {str(e)}', 500)

# Milestone-specific routes
@project_goals_bp.route('/milestones/<int:milestone_id>/complete', methods=['POST'])
def complete_specific_milestone(milestone_id):
    """Complete a specific milestone"""
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    try:
        milestone.complete()
        return success_response({
            'milestone': milestone.to_dict(),
            'project_goal': milestone.goal.to_dict()
        }, 'Milestone completed successfully')
    except Exception as e:
        return error_response(f'Failed to complete milestone: {str(e)}', 500)

@project_goals_bp.route('/milestones/<int:milestone_id>/uncomplete', methods=['POST'])
def uncomplete_specific_milestone(milestone_id):
    """Mark milestone as not completed"""
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    try:
        milestone.uncomplete()
        return success_response({
            'milestone': milestone.to_dict(),
            'project_goal': milestone.goal.to_dict()
        }, 'Milestone marked as incomplete')
    except Exception as e:
        return error_response(f'Failed to update milestone: {str(e)}', 500)