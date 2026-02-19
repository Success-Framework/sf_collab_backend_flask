from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User

class StreakService:
    @staticmethod
    def update_streak(user_id):
        """
        Updates the user's streak based on their activity.
        Should be called whenever a significant user action occurs (e.g., login, post, etc.)
        """
        user = User.query.get(int(user_id))
        if not user:
            return

        today = datetime.utcnow().date()
        last_activity = user.last_activity_date

        if last_activity == today:
            # Already active today, no change needed
            return user.streak_days

        if last_activity == today - timedelta(days=1):
            # Active yesterday, increment streak
            user.streak_days = (user.streak_days or 0) + 1
        else:
            # Missed a day (or first time), reset streak
            user.streak_days = 1

        user.last_activity_date = today
        user.last_login = datetime.utcnow()
        
        # Check for streak-related achievements
        from app.services.achievement_service import AchievementService
        AchievementService.check_achievements(user.id, 'streak_days')
        
        db.session.commit()
        return user.streak_days

