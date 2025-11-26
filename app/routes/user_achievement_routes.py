from flask import Blueprint, request, jsonify
from app.models.userAchievement import UserAchievement
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

user_achievements_bp = Blueprint('user_achievements', __name__, url_prefix='/api/user-achievements')

@user_achievements_bp.route('', methods=['GET'])
def get_user_achievements():
    """Get all user achievements with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    is_completed = request.args.get('is_completed', type=bool)
    
    query = UserAchievement.query
    
    if user_id:
        query = query.filter(UserAchievement.user_id == user_id)
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
def get_user_achievement(user_achievement_id):
    """Get single user achievement by ID"""
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return error_response('User achievement not found', 404)
    
    return success_response({'user_achievement': user_achievement.to_dict()})

@user_achievements_bp.route('/<int:user_achievement_id>/progress', methods=['PUT'])
def update_user_achievement_progress(user_achievement_id):
    """Update user achievement progress"""
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return error_response('User achievement not found', 404)
    
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
def increment_user_achievement_progress(user_achievement_id):
    """Increment user achievement progress"""
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return error_response('User achievement not found', 404)
    
    data = request.get_json()
    increment = data.get('increment', 10)
    
    try:
        user_achievement.increment_progress(increment)
        return success_response({
            'user_achievement': user_achievement.to_dict()
        }, 'Progress incremented successfully')
    except Exception as e:
        return error_response(f'Failed to increment progress: {str(e)}', 500)