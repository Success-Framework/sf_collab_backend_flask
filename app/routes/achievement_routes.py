from flask import Blueprint, request, jsonify
from app.models.achievement import Achievement
from app.models.userAchievement import UserAchievement
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

achievements_bp = Blueprint('achievements', __name__, url_prefix='/api/achievements')

@achievements_bp.route('', methods=['GET'])
def get_achievements():
    """Get all achievements with optional user progress"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    category = request.args.get('category', type=str)
    
    query = Achievement.query
    
    if category:
        query = query.filter(Achievement.category == category)
    
    result = paginate(query, page, per_page)
    
    achievements_data = []
    for achievement in result['items']:
        if user_id:
            achievements_data.append(achievement.to_dict(user_id))
        else:
            achievements_data.append(achievement.to_dict())
    
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
def get_achievement(achievement_id):
    """Get single achievement"""
    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return error_response('Achievement not found', 404)
    
    user_id = request.args.get('user_id', type=int)
    
    return success_response({
        'achievement': achievement.to_dict(user_id)
    })

@achievements_bp.route('', methods=['POST'])
def create_achievement():
    """Create new achievement (admin only)"""
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
def update_achievement(achievement_id):
    """Update achievement (admin only)"""
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
def get_user_achievements(user_id):
    """Get all achievements for a specific user"""
    achievements = AchievementService.get_user_achievements(user_id)
    
    return success_response({
        'achievements': achievements
    })

@achievements_bp.route('/initialize-defaults', methods=['POST'])
def initialize_default_achievements():
    """Initialize default achievements (admin only)"""
    try:
        AchievementService.initialize_default_achievements()
        return success_response(message='Default achievements initialized successfully')
    except Exception as e:
        return error_response(f'Failed to initialize achievements: {str(e)}', 500)