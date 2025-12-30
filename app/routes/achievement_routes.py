from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.achievement import Achievement
from app.models.userAchievement import UserAchievement
from app.models.user import User
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('', methods=['GET'])
@jwt_required()
def get_achievements():
    """Get all achievements with optional user progress"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    category = request.args.get('category', type=str)
    
    # Default to current user if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to view other users' achievements
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users achievements', 403)
    
    query = Achievement.query
    
    if category:
        query = query.filter(Achievement.category == category)
    
    result = paginate(query, page, per_page)
    
    achievements_data = []
    for achievement in result['items']:
        achievements_data.append(achievement.to_dict(user_id))
    
    return success_response({
        'achievements': achievements_data,
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@achievements_bp.route('/<int:achievement_id>', methods=['GET'])
@jwt_required()
def get_achievement(achievement_id):
    """Get single achievement"""
    current_user_id = get_jwt_identity()
    
    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return error_response('Achievement not found', 404)
    
    user_id = request.args.get('user_id', current_user_id)
    
    # Check if user is authorized to view other users' achievement progress
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users achievement progress', 403)
    
    return success_response({
        'achievement': achievement.to_dict(user_id)
    })

@achievements_bp.route('', methods=['POST'])
@jwt_required()
def create_achievement():
    """Create new achievement (admin only)"""
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return error_response('Admin access required to create achievements', 403)
    
    data = request.get_json()
    
    required_fields = ['title', 'description', 'requirement_type', 'requirement_value']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        achievement = Achievement(
            title=data['title'],
            description=data['description'],
            icon=data.get('icon', '🏆'),
            category=data.get('category', 'task'),
            points=data.get('points', 0),
            requirement_type=data['requirement_type'],
            requirement_value=data['requirement_value'],
            badge_color=data.get('badge_color'),
            rarity=data.get('rarity', 'common')
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        return success_response({
            'achievement': achievement.to_dict()
        }, 'Achievement created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create achievement: {str(e)}', 500)

@achievements_bp.route('/<int:achievement_id>', methods=['PUT'])
@jwt_required()
def update_achievement(achievement_id):
    """Update achievement (admin only)"""
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return error_response('Admin access required to update achievements', 403)
    
    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return error_response('Achievement not found', 404)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            achievement.title = data['title']
        if 'description' in data:
            achievement.description = data['description']
        if 'icon' in data:
            achievement.icon = data['icon']
        if 'points' in data:
            achievement.points = data['points']
        if 'requirement_value' in data:
            achievement.requirement_value = data['requirement_value']
        if 'badge_color' in data:
            achievement.badge_color = data['badge_color']
        
        db.session.commit()
        
        return success_response({
            'achievement': achievement.to_dict()
        }, 'Achievement updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update achievement: {str(e)}', 500)

@achievements_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_achievements(user_id):
    """Get all achievements for a specific user"""
    current_user_id = get_jwt_identity()
    
    # Check if user is authorized to view other users' achievements
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users achievements', 403)
    
    achievements = AchievementService.get_user_achievements(user_id)
    
    return success_response({
        'achievements': achievements
    })

@achievements_bp.route('/my-achievements', methods=['GET'])
@jwt_required()
def get_my_achievements():
    """Get current user's achievements (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    achievements = AchievementService.get_user_achievements(current_user_id)
    
    return success_response({
        'achievements': achievements
    })

@achievements_bp.route('/initialize-defaults', methods=['POST'])
@jwt_required()
def initialize_default_achievements():
    """Initialize default achievements (admin only)"""
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return error_response('Admin access required to initialize achievements', 403)
    
    try:
        AchievementService.initialize_default_achievements()
        return success_response(message='Default achievements initialized successfully')
    except Exception as e:
        return error_response(f'Failed to initialize achievements: {str(e)}', 500)

@achievements_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_achievement_categories():
    """Get all achievement categories"""
    categories = db.session.query(Achievement.category).distinct().all()
    category_list = [category[0] for category in categories if category[0]]
    
    return success_response({'categories': category_list})

@achievements_bp.route('/user/<int:user_id>/stats', methods=['GET'])
@jwt_required()
def get_user_achievement_stats(user_id):
    """Get user achievement statistics"""
    current_user_id = get_jwt_identity()
    
    # Check if user is authorized to view other users' achievement stats
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users achievement stats', 403)
    
    try:
        total_achievements = Achievement.query.count()
        user_achievements = UserAchievement.query.filter_by(
            user_id=user_id, 
            is_completed=True
        ).count()
        
        # Calculate completion percentage
        completion_percentage = (user_achievements / total_achievements * 100) if total_achievements > 0 else 0
        
        # Get total points earned
        total_points = db.session.query(db.func.sum(Achievement.points))\
            .join(UserAchievement)\
            .filter(
                UserAchievement.user_id == user_id,
                UserAchievement.is_completed == True
            ).scalar() or 0
        
        stats = {
            'total_achievements': total_achievements,
            'completed_achievements': user_achievements,
            'completion_percentage': round(completion_percentage, 2),
            'total_points_earned': total_points,
            'achievements_remaining': total_achievements - user_achievements
        }
        
        return success_response({'stats': stats})
    except Exception as e:
        return error_response(f'Failed to get achievement stats: {str(e)}', 500)

@achievements_bp.route('/my-stats', methods=['GET'])
@jwt_required()
def get_my_achievement_stats():
    """Get current user's achievement statistics (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    try:
        total_achievements = Achievement.query.count()
        user_achievements = UserAchievement.query.filter_by(
            user_id=current_user_id, 
            is_completed=True
        ).count()
        
        # Calculate completion percentage
        completion_percentage = (user_achievements / total_achievements * 100) if total_achievements > 0 else 0
        
        # Get total points earned
        total_points = db.session.query(db.func.sum(Achievement.points))\
            .join(UserAchievement)\
            .filter(
                UserAchievement.user_id == current_user_id,
                UserAchievement.is_completed == True
            ).scalar() or 0
        
        stats = {
            'total_achievements': total_achievements,
            'completed_achievements': user_achievements,
            'completion_percentage': round(completion_percentage, 2),
            'total_points_earned': total_points,
            'achievements_remaining': total_achievements - user_achievements
        }
        
        return success_response({'stats': stats})
    except Exception as e:
        return error_response(f'Failed to get achievement stats: {str(e)}', 500)