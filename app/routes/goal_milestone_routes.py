from flask import Blueprint, request, jsonify
from app.models.goalMilstone import GoalMilestone
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

milestones_bp = Blueprint('milestones', __name__)

@milestones_bp.route('', methods=['GET'])
def get_milestones():
    """Get all milestones with filtering"""
    goal_id = request.args.get('goal_id', type=int)
    user_id = request.args.get('user_id', type=int)
    completed = request.args.get('completed', type=bool)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = GoalMilestone.query
    
    if goal_id:
        query = query.filter(GoalMilestone.goal_id == goal_id)
    if user_id:
        query = query.filter(GoalMilestone.user_id == user_id)
    if completed is not None:
        query = query.filter(GoalMilestone.is_completed == completed)
    
    result = paginate(query.order_by(GoalMilestone.order), page, per_page)
    
    return success_response({
        'milestones': [milestone.to_dict() for milestone in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@milestones_bp.route('/<int:milestone_id>', methods=['GET'])
def get_milestone(milestone_id):
    """Get single milestone by ID"""
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    return success_response({'milestone': milestone.to_dict()})

@milestones_bp.route('', methods=['POST'])
def create_milestone():
    """Create new milestone"""
    data = request.get_json()
    
    required_fields = ['goal_id', 'user_id', 'title']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: goal_id, user_id, title')
    
    try:
        milestone = GoalMilestone(
            goal_id=data['goal_id'],
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description'),
            order=data.get('order', 0)
        )
        
        db.session.add(milestone)
        db.session.commit()
        
        return success_response({
            'milestone': milestone.to_dict()
        }, 'Milestone created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create milestone: {str(e)}', 500)

@milestones_bp.route('/complete', methods=['POST'])
def complete_milestone():
    """Mark milestone as completed"""
    milestone_id = request.get_json().get('milestone_id')
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    try:
        milestone.complete()
        return success_response({
            'milestone': milestone.to_dict()
        }, 'Milestone completed successfully')
    except Exception as e:
        return error_response(f'Failed to complete milestone: {str(e)}', 500)

@milestones_bp.route('/uncomplete', methods=['POST'])
def uncomplete_milestone():
    """Mark milestone as not completed"""
    milestone_id = request.get_json().get('milestone_id')
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    try:
        milestone.uncomplete()
        return success_response({
            'milestone': milestone.to_dict()
        }, 'Milestone marked as incomplete')
    except Exception as e:
        return error_response(f'Failed to update milestone: {str(e)}', 500)

@milestones_bp.route('/<int:milestone_id>', methods=['PUT'])
def update_milestone(milestone_id):
    """Update milestone"""
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            milestone.title = data['title']
        if 'description' in data:
            milestone.description = data['description']
        if 'order' in data:
            milestone.update_order(data['order'])
        
        db.session.commit()
        return success_response({
            'milestone': milestone.to_dict()
        }, 'Milestone updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update milestone: {str(e)}', 500)

@milestones_bp.route('/<int:milestone_id>', methods=['DELETE'])
def delete_milestone(milestone_id):
    """Delete milestone"""
    milestone = GoalMilestone.query.get(milestone_id)
    if not milestone:
        return error_response('Milestone not found', 404)
    
    try:
        db.session.delete(milestone)
        db.session.commit()
        return success_response(message='Milestone deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete milestone: {str(e)}', 500)