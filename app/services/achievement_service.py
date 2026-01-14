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
            from app.models.ideaComment import IdeaComment
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
            # Milestone Achievements (40)
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
                'title': 'Idea Factory',
                'description': 'Create 50 business ideas',
                'icon': '🏭',
                'category': 'milestone',
                'points': 1000,
                'requirement_type': 'ideas_created',
                'requirement_value': 50,
                'rarity': 'epic'
            },
            {
                'title': 'Idea Visionary',
                'description': 'Create 100 business ideas',
                'icon': '🔭',
                'category': 'milestone',
                'points': 2500,
                'requirement_type': 'ideas_created',
                'requirement_value': 100,
                'rarity': 'legendary'
            },
            {
                'title': 'First Task',
                'description': 'Complete your first task',
                'icon': '☑️',
                'category': 'milestone',
                'points': 50,
                'requirement_type': 'tasks_completed',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Task Master',
                'description': 'Complete 50 tasks',
                'icon': '✅',
                'category': 'milestone',
                'points': 300,
                'requirement_type': 'tasks_completed',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Productivity Guru',
                'description': 'Complete 200 tasks',
                'icon': '⚡',
                'category': 'milestone',
                'points': 800,
                'requirement_type': 'tasks_completed',
                'requirement_value': 200,
                'rarity': 'epic'
            },
            {
                'title': 'Task Titan',
                'description': 'Complete 500 tasks',
                'icon': '🏆',
                'category': 'milestone',
                'points': 2000,
                'requirement_type': 'tasks_completed',
                'requirement_value': 500,
                'rarity': 'legendary'
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
            },
            {
                'title': 'Month of Momentum',
                'description': 'Maintain a 30-day activity streak',
                'icon': '📅',
                'category': 'milestone',
                'points': 500,
                'requirement_type': 'streak_days',
                'requirement_value': 30,
                'rarity': 'rare'
            },
            {
                'title': 'Dedicated Developer',
                'description': 'Maintain a 90-day activity streak',
                'icon': '💪',
                'category': 'milestone',
                'points': 1500,
                'requirement_type': 'streak_days',
                'requirement_value': 90,
                'rarity': 'epic'
            },
            {
                'title': 'Unstoppable Force',
                'description': 'Maintain a 365-day activity streak',
                'icon': '🌟',
                'category': 'milestone',
                'points': 5000,
                'requirement_type': 'streak_days',
                'requirement_value': 365,
                'rarity': 'legendary'
            },
        
            # Social Achievements (45)
            {
                'title': 'First Comment',
                'description': 'Make your first comment',
                'icon': '💬',
                'category': 'social',
                'points': 50,
                'requirement_type': 'comments_made',
                'requirement_value': 1,
                'rarity': 'common'
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
                'title': 'Active Commenter',
                'description': 'Make 100 comments',
                'icon': '🗣️',
                'category': 'social',
                'points': 500,
                'requirement_type': 'comments_made',
                'requirement_value': 100,
                'rarity': 'rare'
            },
            {
                'title': 'Discussion Leader',
                'description': 'Make 500 comments',
                'icon': '👑',
                'category': 'social',
                'points': 1200,
                'requirement_type': 'comments_made',
                'requirement_value': 500,
                'rarity': 'epic'
            },
            {
                'title': 'First Like',
                'description': 'Receive your first like',
                'icon': '👍',
                'category': 'social',
                'points': 25,
                'requirement_type': 'likes_received',
                'requirement_value': 1,
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
                'title': 'Community Favorite',
                'description': 'Get 500 likes on your ideas',
                'icon': '⭐',
                'category': 'social',
                'points': 1000,
                'requirement_type': 'likes_received',
                'requirement_value': 500,
                'rarity': 'epic'
            },
            {
                'title': 'Internet Sensation',
                'description': 'Get 1000 likes on your ideas',
                'icon': '🌐',
                'category': 'social',
                'points': 2500,
                'requirement_type': 'likes_received',
                'requirement_value': 1000,
                'rarity': 'legendary'
            },
            {
                'title': 'First Follower',
                'description': 'Gain your first follower',
                'icon': '👥',
                'category': 'social',
                'points': 100,
                'requirement_type': 'followers_gained',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Growing Audience',
                'description': 'Gain 10 followers',
                'icon': '📈',
                'category': 'social',
                'points': 300,
                'requirement_type': 'followers_gained',
                'requirement_value': 10,
                'rarity': 'common'
            },
            {
                'title': 'Influencer',
                'description': 'Gain 50 followers',
                'icon': '📢',
                'category': 'social',
                'points': 800,
                'requirement_type': 'followers_gained',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Thought Leader',
                'description': 'Gain 200 followers',
                'icon': '🎯',
                'category': 'social',
                'points': 2000,
                'requirement_type': 'followers_gained',
                'requirement_value': 200,
                'rarity': 'epic'
            },
        
            # Task Achievements (35)
            {
                'title': 'Early Bird',
                'description': 'Complete a task before its due date',
                'icon': '🐦',
                'category': 'task',
                'points': 75,
                'requirement_type': 'tasks_completed_early',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Time Manager',
                'description': 'Complete 25 tasks early',
                'icon': '⏰',
                'category': 'task',
                'points': 400,
                'requirement_type': 'tasks_completed_early',
                'requirement_value': 25,
                'rarity': 'rare'
            },
            {
                'title': 'Last Minute Hero',
                'description': 'Complete a task on the due date',
                'icon': '🦸',
                'category': 'task',
                'points': 50,
                'requirement_type': 'tasks_completed_on_time',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Perfect Timing',
                'description': 'Complete 50 tasks on their due date',
                'icon': '🎯',
                'category': 'task',
                'points': 600,
                'requirement_type': 'tasks_completed_on_time',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Task Explorer',
                'description': 'Create tasks in 5 different categories',
                'icon': '🧭',
                'category': 'task',
                'points': 200,
                'requirement_type': 'task_categories_used',
                'requirement_value': 5,
                'rarity': 'common'
            },
            {
                'title': 'Organized Mind',
                'description': 'Create tasks in 10 different categories',
                'icon': '🗂️',
                'category': 'task',
                'points': 500,
                'requirement_type': 'task_categories_used',
                'requirement_value': 10,
                'rarity': 'rare'
            },
        
            # Idea Quality Achievements (30)
            {
                'title': 'Detailed Thinker',
                'description': 'Create an idea with 500+ characters',
                'icon': '📝',
                'category': 'quality',
                'points': 150,
                'requirement_type': 'detailed_ideas',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Thorough Planner',
                'description': 'Create 10 detailed ideas',
                'icon': '📋',
                'category': 'quality',
                'points': 600,
                'requirement_type': 'detailed_ideas',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Idea Architect',
                'description': 'Create an idea with attached documents',
                'icon': '🏗️',
                'category': 'quality',
                'points': 200,
                'requirement_type': 'ideas_with_attachments',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Resourceful Creator',
                'description': 'Create 20 ideas with attachments',
                'icon': '📎',
                'category': 'quality',
                'points': 800,
                'requirement_type': 'ideas_with_attachments',
                'requirement_value': 20,
                'rarity': 'rare'
            },
        
            # Collaboration Achievements (25)
            {
                'title': 'Team Player',
                'description': 'Collaborate on 5 different ideas',
                'icon': '🤝',
                'category': 'collaboration',
                'points': 300,
                'requirement_type': 'ideas_collaborated',
                'requirement_value': 5,
                'rarity': 'common'
            },
            {
                'title': 'Idea Partner',
                'description': 'Collaborate on 20 different ideas',
                'icon': '👥',
                'category': 'collaboration',
                'points': 800,
                'requirement_type': 'ideas_collaborated',
                'requirement_value': 20,
                'rarity': 'rare'
            },
            {
                'title': 'Master Collaborator',
                'description': 'Collaborate on 50 different ideas',
                'icon': '🌟',
                'category': 'collaboration',
                'points': 2000,
                'requirement_type': 'ideas_collaborated',
                'requirement_value': 50,
                'rarity': 'epic'
            },
            {
                'title': 'Helpful Mentor',
                'description': 'Get 10 helpful votes on your comments',
                'icon': '💡',
                'category': 'collaboration',
                'points': 400,
                'requirement_type': 'helpful_votes_received',
                'requirement_value': 10,
                'rarity': 'rare'
            },
        
            # Special Event Achievements (20)
            {
                'title': 'Weekend Warrior',
                'description': 'Complete tasks on 5 different weekends',
                'icon': '🎪',
                'category': 'special',
                'points': 300,
                'requirement_type': 'weekend_activities',
                'requirement_value': 5,
                'rarity': 'rare'
            },
            {
                'title': 'Night Owl',
                'description': 'Create ideas between 10 PM and 2 AM',
                'icon': '🦉',
                'category': 'special',
                'points': 250,
                'requirement_type': 'late_night_activities',
                'requirement_value': 5,
                'rarity': 'rare'
            },
            {
                'title': 'Early Riser',
                'description': 'Create ideas between 5 AM and 8 AM',
                'icon': '🌅',
                'category': 'special',
                'points': 250,
                'requirement_type': 'early_morning_activities',
                'requirement_value': 5,
                'rarity': 'rare'
            },
        
            # Platform Usage Achievements (25)
            {
                'title': 'Platform Explorer',
                'description': 'Use all major platform features',
                'icon': '🧩',
                'category': 'platform',
                'points': 400,
                'requirement_type': 'features_used',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Power User',
                'description': 'Use platform for 30 consecutive days',
                'icon': '⚡',
                'category': 'platform',
                'points': 600,
                'requirement_type': 'consecutive_days_used',
                'requirement_value': 30,
                'rarity': 'epic'
            },
            {
                'title': 'Platform Veteran',
                'description': 'Use platform for 180 days total',
                'icon': '🛡️',
                'category': 'platform',
                'points': 1500,
                'requirement_type': 'total_days_used',
                'requirement_value': 180,
                'rarity': 'epic'
            },
        
            # Creative Achievements (20)
            {
                'title': 'Creative Spark',
                'description': 'Create ideas in 3 different categories',
                'icon': '🎨',
                'category': 'creative',
                'points': 200,
                'requirement_type': 'idea_categories_used',
                'requirement_value': 3,
                'rarity': 'common'
            },
            {
                'title': 'Diverse Thinker',
                'description': 'Create ideas in 10 different categories',
                'icon': '🌈',
                'category': 'creative',
                'points': 700,
                'requirement_type': 'idea_categories_used',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Innovation Master',
                'description': 'Create ideas in 20 different categories',
                'icon': '💎',
                'category': 'creative',
                'points': 1500,
                'requirement_type': 'idea_categories_used',
                'requirement_value': 20,
                'rarity': 'epic'
            },
        
            # Additional achievements to reach 200+
            {
                'title': 'First Share',
                'description': 'Share your first idea externally',
                'icon': '📤',
                'category': 'social',
                'points': 100,
                'requirement_type': 'ideas_shared',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Social Butterfly',
                'description': 'Share 25 ideas externally',
                'icon': '🦋',
                'category': 'social',
                'points': 500,
                'requirement_type': 'ideas_shared',
                'requirement_value': 25,
                'rarity': 'rare'
            },
            {
                'title': 'Bookworm',
                'description': 'Read 50 idea descriptions completely',
                'icon': '📚',
                'category': 'engagement',
                'points': 300,
                'requirement_type': 'ideas_read_completely',
                'requirement_value': 50,
                'rarity': 'common'
            },
            {
                'title': 'Knowledge Seeker',
                'description': 'Read 200 idea descriptions completely',
                'icon': '🔍',
                'category': 'engagement',
                'points': 800,
                'requirement_type': 'ideas_read_completely',
                'requirement_value': 200,
                'rarity': 'rare'
            },
            {
                'title': 'Feedback Provider',
                'description': 'Give feedback on 10 different ideas',
                'icon': '📝',
                'category': 'collaboration',
                'points': 400,
                'requirement_type': 'feedbacks_given',
                'requirement_value': 10,
                'rarity': 'common'
            },
            {
                'title': 'Constructive Critic',
                'description': 'Give feedback on 50 different ideas',
                'icon': '🏗️',
                'category': 'collaboration',
                'points': 1000,
                'requirement_type': 'feedbacks_given',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Idea Refiner',
                'description': 'Update and improve 10 existing ideas',
                'icon': '✨',
                'category': 'quality',
                'points': 500,
                'requirement_type': 'ideas_improved',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Perfectionist',
                'description': 'Update and improve 50 existing ideas',
                'icon': '🎭',
                'category': 'quality',
                'points': 1200,
                'requirement_type': 'ideas_improved',
                'requirement_value': 50,
                'rarity': 'epic'
            },
            {
                'title': 'Mobile User',
                'description': 'Use the platform on mobile device',
                'icon': '📱',
                'category': 'platform',
                'points': 100,
                'requirement_type': 'mobile_sessions',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'On-the-Go',
                'description': 'Use platform on mobile 50 times',
                'icon': '🚶',
                'category': 'platform',
                'points': 400,
                'requirement_type': 'mobile_sessions',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Desktop Commander',
                'description': 'Use platform on desktop 100 times',
                'icon': '💻',
                'category': 'platform',
                'points': 500,
                'requirement_type': 'desktop_sessions',
                'requirement_value': 100,
                'rarity': 'rare'
            },
            {
                'title': 'Multi-Platform',
                'description': 'Use platform on 3 different devices',
                'icon': '🔄',
                'category': 'platform',
                'points': 300,
                'requirement_type': 'devices_used',
                'requirement_value': 3,
                'rarity': 'common'
            },
            {
                'title': 'Seasoned Veteran',
                'description': 'Use platform for 1 year',
                'icon': '🎂',
                'category': 'milestone',
                'points': 1000,
                'requirement_type': 'account_age_days',
                'requirement_value': 365,
                'rarity': 'epic'
            },
            {
                'title': 'Long-term Visionary',
                'description': 'Use platform for 2 years',
                'icon': '⌛',
                'category': 'milestone',
                'points': 2500,
                'requirement_type': 'account_age_days',
                'requirement_value': 730,
                'rarity': 'legendary'
            },
            {
                'title': 'Idea Collector',
                'description': 'Save 20 ideas to your favorites',
                'icon': '⭐',
                'category': 'engagement',
                'points': 300,
                'requirement_type': 'ideas_saved',
                'requirement_value': 20,
                'rarity': 'common'
            },
            {
                'title': 'Curator',
                'description': 'Save 100 ideas to your favorites',
                'icon': '🏛️',
                'category': 'engagement',
                'points': 800,
                'requirement_type': 'ideas_saved',
                'requirement_value': 100,
                'rarity': 'rare'
            },
            {
                'title': 'Archivist',
                'description': 'Save 500 ideas to your favorites',
                'icon': '📚',
                'category': 'engagement',
                'points': 2000,
                'requirement_type': 'ideas_saved',
                'requirement_value': 500,
                'rarity': 'epic'
            },
            {
                'title': 'Tag Master',
                'description': 'Use 50 different tags on ideas',
                'icon': '🏷️',
                'category': 'organization',
                'points': 400,
                'requirement_type': 'unique_tags_used',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Organized Mind',
                'description': 'Create 10 custom categories',
                'icon': '🗃️',
                'category': 'organization',
                'points': 500,
                'requirement_type': 'custom_categories_created',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Template Creator',
                'description': 'Create 5 idea templates',
                'icon': '📄',
                'category': 'organization',
                'points': 600,
                'requirement_type': 'templates_created',
                'requirement_value': 5,
                'rarity': 'epic'
            },
            
            # Quick Task Achievements
            {
                'title': 'Quick Draw',
                'description': 'Complete a task within 1 hour of creating it',
                'icon': '⚡',
                'category': 'task',
                'points': 150,
                'requirement_type': 'quick_tasks_completed',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Speed Demon',
                'description': 'Complete 20 tasks within 1 hour',
                'icon': '🎯',
                'category': 'task',
                'points': 600,
                'requirement_type': 'quick_tasks_completed',
                'requirement_value': 20,
                'rarity': 'rare'
            },
            
            # Consistency Achievements
            {
                'title': 'Weekly Regular',
                'description': 'Use platform 4 weeks in a row',
                'icon': '📆',
                'category': 'consistency',
                'points': 300,
                'requirement_type': 'consecutive_weeks',
                'requirement_value': 4,
                'rarity': 'common'
            },
            {
                'title': 'Monthly Champion',
                'description': 'Use platform 6 months in a row',
                'icon': '🏅',
                'category': 'consistency',
                'points': 1000,
                'requirement_type': 'consecutive_months',
                'requirement_value': 6,
                'rarity': 'epic'
            },
            
            # Community Achievements
            {
                'title': 'Welcome Committee',
                'description': 'Welcome 10 new users',
                'icon': '👋',
                'category': 'community',
                'points': 400,
                'requirement_type': 'new_users_welcomed',
                'requirement_value': 10,
                'rarity': 'rare'
            },
            {
                'title': 'Community Builder',
                'description': 'Welcome 50 new users',
                'icon': '🏘️',
                'category': 'community',
                'points': 1200,
                'requirement_type': 'new_users_welcomed',
                'requirement_value': 50,
                'rarity': 'epic'
            },
            
            # Learning Achievements
            {
                'title': 'Quick Learner',
                'description': 'Complete the platform tutorial',
                'icon': '🎓',
                'category': 'learning',
                'points': 200,
                'requirement_type': 'tutorial_completed',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Feature Expert',
                'description': 'Use all advanced features',
                'icon': '🧠',
                'category': 'learning',
                'points': 800,
                'requirement_type': 'advanced_features_used',
                'requirement_value': 10,
                'rarity': 'epic'
            },
            
            # Special Category: Seasonal/Holiday
            {
                'title': 'New Year Innovator',
                'description': 'Create an idea on January 1st',
                'icon': '🎆',
                'category': 'seasonal',
                'points': 250,
                'requirement_type': 'new_years_idea',
                'requirement_value': 1,
                'rarity': 'rare'
            },
            {
                'title': 'Summer Thinker',
                'description': 'Create ideas during summer months',
                'icon': '☀️',
                'category': 'seasonal',
                'points': 300,
                'requirement_type': 'summer_ideas',
                'requirement_value': 5,
                'rarity': 'common'
            },
            
            # Challenge Achievements
            {
                'title': 'Challenge Accepted',
                'description': 'Participate in your first challenge',
                'icon': '🎪',
                'category': 'challenge',
                'points': 200,
                'requirement_type': 'challenges_participated',
                'requirement_value': 1,
                'rarity': 'common'
            },
            {
                'title': 'Challenge Champion',
                'description': 'Win 5 challenges',
                'icon': '🏆',
                'category': 'challenge',
                'points': 1500,
                'requirement_type': 'challenges_won',
                'requirement_value': 5,
                'rarity': 'epic'
            },
            
            # Progression Achievements
            {
                'title': 'Level Up',
                'description': 'Reach level 10',
                'icon': '⬆️',
                'category': 'progression',
                'points': 500,
                'requirement_type': 'user_level',
                'requirement_value': 10,
                'rarity': 'common'
            },
            {
                'title': 'Master Level',
                'description': 'Reach level 50',
                'icon': '🎯',
                'category': 'progression',
                'points': 2000,
                'requirement_type': 'user_level',
                'requirement_value': 50,
                'rarity': 'epic'
            },
            
            # Collection Achievements
            {
                'title': 'Achievement Hunter',
                'description': 'Earn 50 different achievements',
                'icon': '🏹',
                'category': 'collection',
                'points': 1000,
                'requirement_type': 'achievements_earned',
                'requirement_value': 50,
                'rarity': 'rare'
            },
            {
                'title': 'Completionist',
                'description': 'Earn 100 different achievements',
                'icon': '💯',
                'category': 'collection',
                'points': 3000,
                'requirement_type': 'achievements_earned',
                'requirement_value': 100,
                'rarity': 'legendary'
            }
        ]
        
        for achievement_data in default_achievements:
            existing = Achievement.query.filter_by(title=achievement_data['title']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
        
        db.session.commit()