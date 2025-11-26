from app.models.achievement import Achievement
from app.models.userAchievement import UserAchievement
from app.models.user import User
from app.models.idea import Idea
from app.models.task import Task
from app.extensions import db

class AchievementService:
    
    @staticmethod
    def check_achievements(user_id, action_type, action_data=None):
        """Check and update achievements based on user actions"""
        achievements = Achievement.query.filter_by(requirement_type=action_type).all()
        
        unlocked_achievements = []
        
        for achievement in achievements:
            user_achievement = UserAchievement.query.filter_by(
                user_id=user_id, 
                achievement_id=achievement.id
            ).first()
            
            if not user_achievement:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
            
            if not user_achievement.is_completed:
                progress = AchievementService.calculate_progress(
                    user_id, achievement, action_type, action_data
                )
                
                if progress > user_achievement.progress_percentage:
                    user_achievement.update_progress(progress)
                    
                    if user_achievement.is_completed:
                        unlocked_achievements.append(user_achievement)
        
        db.session.commit()
        return unlocked_achievements
    
    @staticmethod
    def calculate_progress(user_id, achievement, action_type, action_data):
        """Calculate progress for an achievement"""
        if action_type == 'tasks_completed':
            completed_tasks = Task.query.filter_by(
                user_id=user_id, 
                status='completed'
            ).count()
            return min((completed_tasks / achievement.requirement_value) * 100, 100)
        
        elif action_type == 'ideas_created':
            ideas_count = Idea.query.filter_by(creator_id=user_id).count()
            return min((ideas_count / achievement.requirement_value) * 100, 100)
        
        elif action_type == 'comments_made':
            from models.ideaComment import IdeaComment
            comments_count = IdeaComment.query.filter_by(author_id=user_id).count()
            return min((comments_count / achievement.requirement_value) * 100, 100)
        
        elif action_type == 'likes_received':
            # This would require tracking likes on user's content
            ideas = Idea.query.filter_by(creator_id=user_id).all()
            total_likes = sum(idea.likes for idea in ideas)
            return min((total_likes / achievement.requirement_value) * 100, 100)
        
        elif action_type == 'streak_days':
            user = User.query.get(user_id)
            return min((user.streak_days / achievement.requirement_value) * 100, 100)
        
        return 0
    
    @staticmethod
    def get_user_achievements(user_id):
        """Get all achievements with user's progress"""
        achievements = Achievement.query.all()
        result = []
        
        for achievement in achievements:
            user_achievement = UserAchievement.query.filter_by(
                user_id=user_id, 
                achievement_id=achievement.id
            ).first()
            
            achievement_data = achievement.to_dict(user_id)
            
            if user_achievement:
                achievement_data['user_achievement'] = user_achievement.to_dict()
            else:
                achievement_data['user_achievement'] = {
                    'progress_percentage': 0,
                    'is_completed': False
                }
            
            result.append(achievement_data)
        
        return result
    
    @staticmethod
    def initialize_default_achievements():
        """Initialize default achievements in the system"""
        default_achievements = [
            {
                'title': 'First Idea',
                'description': 'Create your first business idea',
                'icon': '💡',
                'category': 'milestone',
                'points': 100,
                'requirement_type': 'ideas_created',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Idea Machine',
                'description': 'Create 10 business ideas',
                'icon': '🚀',
                'category': 'milestone',
                'points': 500,
                'requirement_type': 'ideas_created',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Task Master',
                'description': 'Complete 50 tasks',
                'icon': '✅',
                'category': 'task',
                'points': 300,
                'requirement_type': 'tasks_completed',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Comment Contributor',
                'description': 'Make 25 comments on ideas',
                'icon': '💬',
                'category': 'social',
                'points': 200,
                'requirement_type': 'comments_made',
                'requirement_value': 25,
                'rarity': 'common'
            },
            {
                'title': 'Popular Idea',
                'description': 'Get 100 likes on your ideas',
                'icon': '❤️',
                'category': 'social',
                'points': 400,
                'requirement_type': 'likes_received',
                'requirement_value': 100,
                'rarity': 'epic'
            },
            {
                'title': '7-Day Streak',
                'description': 'Maintain a 7-day activity streak',
                'icon': '🔥',
                'category': 'milestone',
                'points': 150,
                'requirement_type': 'streak_days',
                'requirement_value': 7,
                'rarity': 'common'
            }
        ]
        
        for achievement_data in default_achievements:
            existing = Achievement.query.filter_by(title=achievement_data['title']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
        
        db.session.commit()