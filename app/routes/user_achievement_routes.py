from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.userAchievement import UserAchievement
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

user_achievements_bp = Blueprint('user_achievements', __name__)

@user_achievements_bp.route('', methods=['GET'])
@jwt_required()
def get_user_achievements():
    """Get all user achievements with filtering"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    is_completed = request.args.get('is_completed', type=bool)
    
    # Default to current user's achievements if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to view other users' achievements
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users achievements', 403)
    
    query = UserAchievement.query.filter(UserAchievement.user_id == user_id)
    
    if is_completed is not None:
        query = query.filter(UserAchievement.is_completed == is_completed)
    
    result = paginate(query.order_by(UserAchievement.unlocked_at.desc()), page, per_page)
    
    return success_response({
        'user_achievements': [ua.to_dict() for ua in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@user_achievements_bp.route('/<int:user_achievement_id>', methods=['GET'])
@jwt_required()
def get_user_achievement(user_achievement_id):
    """Get single user achievement by ID"""
    current_user_id = get_jwt_identity()
    
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return error_response('User achievement not found', 404)
    
    # Check if user is authorized to view this achievement
    if user_achievement.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view this achievement', 403)
    
    return success_response({'user_achievement': user_achievement.to_dict()})

@user_achievements_bp.route('/<int:user_achievement_id>/progress', methods=['PUT'])
@jwt_required()
def update_user_achievement_progress(user_achievement_id):
    """Update user achievement progress"""
    current_user_id = get_jwt_identity()
    
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return error_response('User achievement not found', 404)
    
    # Check if user is authorized to update this achievement
    if user_achievement.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to update this achievement', 403)
    
    data = request.get_json()
    progress = data.get('progress_percentage')
    
    if progress is None:
        return error_response('Progress percentage is required', 400)
    
    try:
        user_achievement.update_progress(progress)
        return success_response({
            'user_achievement': user_achievement.to_dict()
        }, 'Progress updated successfully')
    except Exception as e:
        return error_response(f'Failed to update progress: {str(e)}', 500)

@user_achievements_bp.route('/<int:user_achievement_id>/increment', methods=['POST'])
@jwt_required()
def increment_user_achievement_progress(user_achievement_id):
    """Increment user achievement progress"""
    current_user_id = get_jwt_identity()
    
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return error_response('User achievement not found', 404)
    
    # Check if user is authorized to update this achievement
    if user_achievement.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to update this achievement', 403)
    
    data = request.get_json()
    increment = data.get('increment', 10)
    
    try:
        user_achievement.increment_progress(increment)
        return success_response({
            'user_achievement': user_achievement.to_dict()
        }, 'Progress incremented successfully')
    except Exception as e:
        return error_response(f'Failed to increment progress: {str(e)}', 500)

@user_achievements_bp.route('/my-achievements', methods=['GET'])
@jwt_required()
def get_my_achievements():
    """Get current user's achievements (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_completed = request.args.get('is_completed', type=bool)
    
    query = UserAchievement.query.filter(UserAchievement.user_id == current_user_id)
    
    if is_completed is not None:
        query = query.filter(UserAchievement.is_completed == is_completed)
    
    result = paginate(query.order_by(UserAchievement.unlocked_at.desc()), page, per_page)
    
    return success_response({
        'user_achievements': [ua.to_dict() for ua in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@user_achievements_bp.route('/my-achievements/stats', methods=['GET'])
@jwt_required()
def get_my_achievement_stats():
    """Get current user's achievement statistics"""
    current_user_id = get_jwt_identity()
    
    try:
        total_achievements = UserAchievement.query.filter_by(user_id=current_user_id).count()
        completed_achievements = UserAchievement.query.filter_by(user_id=current_user_id, is_completed=True).count()
        in_progress_achievements = UserAchievement.query.filter_by(user_id=current_user_id, is_completed=False).count()
        
        # Calculate completion percentage
        completion_percentage = (completed_achievements / total_achievements * 100) if total_achievements > 0 else 0
        
        # Get recent achievements
        recent_achievements = UserAchievement.query.filter_by(
            user_id=current_user_id, 
            is_completed=True
        ).order_by(UserAchievement.unlocked_at.desc()).limit(5).all()
        
        stats = {
            'total_achievements': total_achievements,
            'completed_achievements': completed_achievements,
            'in_progress_achievements': in_progress_achievements,
            'completion_percentage': round(completion_percentage, 2),
            'recent_achievements': [ua.to_dict() for ua in recent_achievements]
        }
        
        return success_response({'stats': stats})
    except Exception as e:
        return error_response(f'Failed to get achievement stats: {str(e)}', 500)