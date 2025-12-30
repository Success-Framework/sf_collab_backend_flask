from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.teamPerformance import TeamPerformance
from app.models.user import User
from app.models.startup import Startup
from app.models.startUpMember import StartupMember
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

team_performance_bp = Blueprint('team_performance', __name__)

@team_performance_bp.route('', methods=['GET'])
@jwt_required()
def get_team_performance():
    """Get all team performance records with filtering"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    startup_id = request.args.get('startup_id', type=int)
    current_only = request.args.get('current_only', type=bool)
    
    # Check if user has access to the requested startup
    if startup_id:
        if not has_startup_access(current_user_id, startup_id):
            return error_response('Unauthorized to access this startup performance data', 403)
        query = TeamPerformance.query.filter(TeamPerformance.startup_id == startup_id)
    else:
        # If no startup_id specified, get all startups user has access to
        accessible_startup_ids = get_accessible_startup_ids(current_user_id)
        query = TeamPerformance.query.filter(TeamPerformance.startup_id.in_(accessible_startup_ids))
    
    if current_only:
        now = datetime.utcnow()
        query = query.filter(
            TeamPerformance.period_start <= now,
            TeamPerformance.period_end >= now
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'performance_records': [record.to_dict() for record in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@team_performance_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_team_performance_record(record_id):
    """Get single team performance record by ID"""
    current_user_id = get_jwt_identity()
    
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    # Check if user has access to this startup's performance data
    if not has_startup_access(current_user_id, record.startup_id):
        return error_response('Unauthorized to access this performance record', 403)
    
    return success_response({'performance_record': record.to_dict()})

@team_performance_bp.route('', methods=['POST'])
@jwt_required()
def create_team_performance_record():
    """Create new team performance record"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['startup_id', 'period_start', 'period_end']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: startup_id, period_start, period_end')
    
    # Check if user has permission to create performance records for this startup
    startup_id = data['startup_id']
    if not has_startup_management_access(current_user_id, startup_id):
        return error_response('Unauthorized to create performance records for this startup', 403)
    
    try:
        record = TeamPerformance(
            startup_id=startup_id,
            score_percentage=data.get('score_percentage', 0),
            active_members=data.get('active_members', 0),
            tasks_completed=data.get('tasks_completed', 0),
            productivity_level=data.get('productivity_level', 'medium'),
            period_start=datetime.fromisoformat(data['period_start']),
            period_end=datetime.fromisoformat(data['period_end'])
        )
        
        db.session.add(record)
        db.session.commit()
        
        return success_response({'performance_record': record.to_dict()}, 'Performance record created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create performance record: {str(e)}', 500)

@team_performance_bp.route('/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_team_performance_record(record_id):
    """Update team performance record"""
    current_user_id = get_jwt_identity()
    
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    # Check if user has permission to update this performance record
    if not has_startup_management_access(current_user_id, record.startup_id):
        return error_response('Unauthorized to update this performance record', 403)
    
    data = request.get_json()
    
    try:
        if 'score_percentage' in data:
            record.update_score(data['score_percentage'])
        if 'active_members' in data:
            record.update_active_members(data['active_members'])
        if 'tasks_completed' in data:
            record.tasks_completed = data['tasks_completed']
        if 'productivity_level' in data:
            record.productivity_level = data['productivity_level']
        
        db.session.commit()
        return success_response({'performance_record': record.to_dict()}, 'Performance record updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update performance record: {str(e)}', 500)

@team_performance_bp.route('/<int:record_id>/tasks', methods=['POST'])
@jwt_required()
def increment_tasks_completed(record_id):
    """Increment tasks completed"""
    current_user_id = get_jwt_identity()
    
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    # Check if user has permission to update this performance record
    if not has_startup_management_access(current_user_id, record.startup_id):
        return error_response('Unauthorized to update this performance record', 403)
    
    data = request.get_json()
    count = data.get('count', 1)
    
    try:
        record.increment_tasks_completed(count)
        return success_response({'performance_record': record.to_dict()}, 'Tasks count updated successfully')
    except Exception as e:
        return error_response(f'Failed to update tasks count: {str(e)}', 500)

@team_performance_bp.route('/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_team_performance_record(record_id):
    """Delete team performance record"""
    current_user_id = get_jwt_identity()
    
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    # Check if user has permission to delete this performance record
    if not has_startup_management_access(current_user_id, record.startup_id):
        return error_response('Unauthorized to delete this performance record', 403)
    
    try:
        db.session.delete(record)
        db.session.commit()
        return success_response(message='Performance record deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete performance record: {str(e)}', 500)

@team_performance_bp.route('/startup/<int:startup_id>/current', methods=['GET'])
@jwt_required()
def get_current_team_performance(startup_id):
    """Get current team performance for a specific startup"""
    current_user_id = get_jwt_identity()
    
    # Check if user has access to this startup's performance data
    if not has_startup_access(current_user_id, startup_id):
        return error_response('Unauthorized to access this startup performance data', 403)
    
    now = datetime.utcnow()
    record = TeamPerformance.query.filter(
        TeamPerformance.startup_id == startup_id,
        TeamPerformance.period_start <= now,
        TeamPerformance.period_end >= now
    ).first()
    
    if not record:
        return error_response('No current performance record found', 404)
    
    return success_response({'performance_record': record.to_dict()})

# Helper functions for authorization
def has_startup_access(user_id, startup_id):
    """Check if user has access to view startup performance data"""
    # Admin users can access all startups
    current_user = User.query.get(user_id)
    if current_user :
        return True
    
    # Check if user is a member of the startup
    membership = StartupMember.query.filter_by(
        user_id=user_id, 
        startup_id=startup_id
    ).first()
    
    return membership is not None

def has_startup_management_access(user_id, startup_id):
    """Check if user has permission to manage startup performance data"""
    # Admin users can manage all startups
    current_user = User.query.get(user_id)
    if current_user :
        return True
    
    # Check if user is an admin or manager of the startup
    membership = StartupMember.query.filter_by(
        user_id=user_id, 
        startup_id=startup_id
    ).first()
    
    return membership and membership.role in ['admin', 'manager', 'owner']

def get_accessible_startup_ids(user_id):
    """Get list of startup IDs that the user can access"""
    # Admin users can access all startups
    current_user = User.query.get(user_id)
    if current_user :
        return [startup.id for startup in Startup.query.all()]
    
    # Get startups where user is a member
    memberships = StartupMember.query.filter_by(user_id=user_id).all()
    return [membership.startup_id for membership in memberships]