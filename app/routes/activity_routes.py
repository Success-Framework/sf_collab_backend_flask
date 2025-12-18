from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.activity import Activity
from app.utils.helper import error_response, success_response, paginate
from datetime import datetime, timedelta
from sqlalchemy import func
    
activities_bp = Blueprint('activities', __name__, url_prefix='/api/activities')

@activities_bp.route('', methods=['GET'])
@jwt_required()
def get_activities():
    """Get all activities with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    
    query = Activity.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action:
        query = query.filter_by(action=action)
    
    if start_date:
        try:
            start_date_obj = datetime.fromisoformat(start_date)
            query = query.filter(Activity.created_at >= start_date_obj)
        except ValueError:
            return error_response('Invalid start_date format', 400)
    
    if end_date:
        try:
            end_date_obj = datetime.fromisoformat(end_date)
            query = query.filter(Activity.created_at <= end_date_obj)
        except ValueError:
            return error_response('Invalid end_date format', 400)
    
    result = paginate(query.order_by(Activity.created_at.desc()), page, per_page)
    
    return success_response({
        'activities': [activity.to_dict(include_user_info=True) for activity in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@activities_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """Get recent activities"""
    limit = request.args.get('limit', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', type=str)
    
    activities = Activity.get_recent_activities(
        limit=limit,
        user_id=user_id,
        action=action
    )
    
    return success_response({
        'activities': [activity.to_dict(include_user_info=True) for activity in activities]
    })

@activities_bp.route('/my-activities', methods=['GET'])
@jwt_required()
def get_my_activities():
    """Get current user's activities"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    action = request.args.get('action', type=str)
    
    query = Activity.query.filter_by(user_id=current_user_id)
    
    if action:
        query = query.filter_by(action=action)
    
    result = paginate(query.order_by(Activity.created_at.desc()), page, per_page)
    
    return success_response({
        'activities': [activity.to_dict(include_user_info=False) for activity in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

# @activities_bp.route('/stats', methods=['GET'])
# @jwt_required()
# def get_activity_stats():
#     """Get activity statistics"""
    
    
#     days = request.args.get('days', 7, type=int)
    
#     # Calculate date range
#     end_date = datetime.utcnow()
#     start_date = end_date - timedelta(days=days)
    
#     # Get daily activity counts
#     daily_counts = db.session.query(
#         func.date(Activity.created_at).label('date'),
#         func.count(Activity.id).label('count')
#     ).filter(
#         Activity.created_at >= start_date,
#         Activity.created_at <= end_date
#     ).group_by(
#         func.date(Activity.created_at)
#     ).order_by('date').all()
    
#     # Get action distribution
#     action_distribution = db.session.query(
#         Activity.action,
#         func.count(Activity.id).label('count')
#     ).filter(
#         Activity.created_at >= start_date,
#         Activity.created_at <= end_date
#     ).group_by(
#         Activity.action
#     ).order_by(func.count(Activity.id).desc()).all()
    
#     # Get top users
#     top_users = db.session.query(
#         Activity.user_id,
#         func.count(Activity.id).label('count')
#     ).filter(
#         Activity.created_at >= start_date,
#         Activity.created_at <= end_date,
#         Activity.user_id.isnot(None)
#     ).group_by(
#         Activity.user_id
#     ).order_by(func.count(Activity.id).desc()).limit(10).all()
    
#     return success_response({
#         'period': {
#             'start_date': start_date.isoformat(),
#             'end_date': end_date.isoformat(),
#             'days': days
#         },
#         'daily_counts': [
#             {'date': str(date), 'count': count}
#             for date, count in daily_counts
#         ],
#         'action_distribution': [
#             {'action': action, 'count': count}
#             for action, count in action_distribution
#         ],
#         'top_users': [
#             {'user_id': user_id, 'count': count}
#             for user_id, count in top_users
#         ]
#     })