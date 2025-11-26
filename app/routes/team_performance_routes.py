from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models.teamPerformance import TeamPerformance
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

team_performance_bp = Blueprint('team_performance', __name__, url_prefix='/api/team-performance')

@team_performance_bp.route('', methods=['GET'])
def get_team_performance():
    """Get all team performance records with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    startup_id = request.args.get('startup_id', type=int)
    current_only = request.args.get('current_only', type=bool)
    
    query = TeamPerformance.query
    
    if startup_id:
        query = query.filter(TeamPerformance.startup_id == startup_id)
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
def get_team_performance_record(record_id):
    """Get single team performance record by ID"""
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    return success_response({'performance_record': record.to_dict()})

@team_performance_bp.route('', methods=['POST'])
def create_team_performance_record():
    """Create new team performance record"""
    data = request.get_json()
    
    required_fields = ['startup_id', 'period_start', 'period_end']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: startup_id, period_start, period_end')
    
    try:
        record = TeamPerformance(
            startup_id=data['startup_id'],
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
def update_team_performance_record(record_id):
    """Update team performance record"""
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
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
def increment_tasks_completed(record_id):
    """Increment tasks completed"""
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    data = request.get_json()
    count = data.get('count', 1)
    
    try:
        record.increment_tasks_completed(count)
        return success_response({'performance_record': record.to_dict()}, 'Tasks count updated successfully')
    except Exception as e:
        return error_response(f'Failed to update tasks count: {str(e)}', 500)

@team_performance_bp.route('/<int:record_id>', methods=['DELETE'])
def delete_team_performance_record(record_id):
    """Delete team performance record"""
    record = TeamPerformance.query.get(record_id)
    if not record:
        return error_response('Team performance record not found', 404)
    
    try:
        db.session.delete(record)
        db.session.commit()
        return success_response(message='Performance record deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete performance record: {str(e)}', 500)