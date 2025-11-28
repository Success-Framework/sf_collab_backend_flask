from flask import Blueprint, request, jsonify, redirect, url_for
from app.extensions import oauth, db
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity
)
from app.models.user import User
from app.models.refreshToken import RefreshToken
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth.init_app(app)
    
    # Google OAuth
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )


# ========================== HELPER FUNCTIONS ==========================
def generate_tokens(user_id):
    """Generate access and refresh tokens"""
    access_token = create_access_token(
        identity=str(user_id),
        expires_delta=timedelta(hours=6),
        fresh=True
    )
    refresh_token_str = create_refresh_token(
        identity=str(user_id),
        expires_delta=timedelta(days=30)
    )
    return access_token, refresh_token_str


def save_refresh_token(user_id, token):
    """Save refresh token to database"""
    try:
        # Delete old refresh tokens for this user
        RefreshToken.query.filter_by(user_id=user_id).delete()
        
        # Save new refresh token
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token
        )
        db.session.add(refresh_token)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving refresh token: {str(e)}")


def get_user_response_data(user):
    """Get formatted user data for response with complete user model data and relationships"""
    # Get computed metrics
    notifications_count = user.notifications.filter_by(is_read=False).count()
    
    # Get active startups count
    try:
        from app.models.startUpMember import StartupMember
        active_startups = StartupMember.query.filter_by(
            user_id=user.id,
            is_active=True
        ).count()
    except:
        active_startups = user.active_startups_count
    
    # Get pending tasks count
    try:
        from app.models.task import Task
        pending_tasks = Task.query.filter_by(
            user_id=user.id,
            status='in_progress'
        ).count()
    except:
        pending_tasks = 0
    
    # Get comprehensive statistics
    statistics = user.get_statistics()
    
    # Get recent activity
    recent_activity = user.get_recent_activity()
    
    # Build complete user data with ALL fields from the User model including relationship data
    user_data = {
        # Core user information
        'id': user.id,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'isEmailVerified': user.is_email_verified,
        'lastLogin': user.last_login.isoformat() if user.last_login else None,
        'status': user._enum_to_value(user.status),
        'role': user._enum_to_value(user.role),
        
        # XP and engagement
        'xpPoints': user.xp_points,
        'streakDays': user.streak_days,
        'lastActivityDate': user.last_activity_date.isoformat() if user.last_activity_date else None,
        
        # Business metrics
        'totalRevenue': user.total_revenue,
        'satisfactionPercentage': user.satisfaction_percentage,
        'activeStartupsCount': user.active_startups_count,
        
        # Profile information
        'profile': {
            'picture': user.profile_picture,
            'bio': user.profile_bio,
            'company': user.profile_company,
            'socialLinks': user.profile_social_links or {},
            'country': user.profile_country,
            'city': user.profile_city,
            'timezone': user.profile_timezone
        },
        
        # Preferences
        'preferences': {
            'emailNotifications': user.pref_email_notifications,
            'pushNotifications': user.pref_push_notifications,
            'privacy': user._enum_to_value(user.pref_privacy),
            'language': user.pref_language,
            'timezone': user.pref_timezone,
            'theme': user._enum_to_value(user.pref_theme)
        },
        
        # Notification settings
        'notificationSettings': {
            'newComments': user.notif_new_comments,
            'newLikes': user.notif_new_likes,
            'newSuggestions': user.notif_new_suggestions,
            'joinRequests': user.notif_join_requests,
            'approvals': user.notif_approvals,
            'storyViews': user.notif_story_views,
            'postEngagement': user.notif_post_engagement,
            'emailDigest': user._enum_to_value(user.notif_email_digest),
            'quietHours': {
                'enabled': user.notif_quiet_hours_enabled,
                'start': user.notif_quiet_hours_start,
                'end': user.notif_quiet_hours_end
            }
        },
        
        # Timestamps
        'createdAt': user.created_at.isoformat(),
        'updatedAt': user.updated_at.isoformat(),
        
        # Computed fields
        'fullName': user.get_full_name(),
        'timezone': user.get_timezone(),
        
        # Additional computed metrics
        'notificationsCount': notifications_count,
        'pendingTasksCount': pending_tasks,
        'activeStartupsCount': active_startups,
        
        # Comprehensive statistics
        'statistics': statistics,
        
        # Recent activity
        'recentActivity': recent_activity,
        
        # Relationship DATA (not just counts)
        'relationships': {
            # Core Authentication & Profile
            'notifications': [notification.to_dict() for notification in user.notifications.limit(50).all()],
            # 'refreshTokens': [token.to_dict() for token in user.refresh_tokens.limit(20).all()],
            
            # Content Creation
            'ideas': [idea.to_dict() for idea in user.ideas.limit(50).all()],
            'knowledgePosts': [knowledge.to_dict() for knowledge in user.knowledge_posts.limit(50).all()],
            'startups': [startup.to_dict() for startup in user.startups.limit(50).all()],
            'stories': [story.to_dict() for story in user.stories.limit(50).all()],
            'authoredPosts': [post.to_dict() for post in user.authored_posts.limit(50).all()],
            
            # Comments & Engagement
            'ideaComments': [comment.to_dict() for comment in user.idea_comments.limit(50).all()],
            'knowledgeComments': [comment.to_dict() for comment in user.knowledge_comments.limit(50).all()],
            'postComments': [comment.to_dict() for comment in user.post_comments_list.limit(50).all()],
            
            # Likes & Bookmarks
            'postLikes': [like.to_dict() for like in user.post_likes.limit(50).all()],
            'resourceLikes': [like.to_dict() for like in user.resource_likes.limit(50).all()],
            'startupBookmarks': [bookmark.to_dict() for bookmark in user.startup_bookmarks.limit(50).all()],
            'knowledgeBookmarks': [bookmark.to_dict() for bookmark in user.knowledge_bookmarks.limit(50).all()],
            'ideaBookmarks': [bookmark.to_dict() for bookmark in user.idea_bookmarks.limit(50).all()],
            
            # Tasks & Projects
            'ownedTasks': [task.to_dict() for task in user.owned_tasks.limit(50).all()],
            'createdTasks': [task.to_dict() for task in user.created_tasks.limit(50).all()],
            'assignedTasks': [task.to_dict() for task in user.assigned_tasks.limit(50).all()],
            'projectGoals': [goal.to_dict() for goal in user.project_goals.limit(50).all()],
            
            # Team & Startup Relationships
            'startupMemberships': [membership.to_dict() for membership in user.startup_memberships.limit(50).all()],
            'joinRequests': [request.to_dict() for request in user.join_requests.limit(50).all()],
            
            # Achievements & Growth
            'achievements': [achievement.to_dict() for achievement in user.user_achievements.limit(50).all()],
            'growthMetrics': [metric.to_dict() for metric in user.growth_metrics.limit(50).all()],
            
            # Chat & Messaging
            'sentMessages': [message.to_dict() for message in user.sent_messages.limit(50).all()],
            'conversations': [conversation.to_dict() for conversation in user.conversations.limit(50).all()],
            'createdConversations': [conversation.to_dict() for conversation in user.created_conversations.limit(50).all()],
            
            # Views & Analytics
            'resourceViews': [view.to_dict() for view in user.resource_views.limit(50).all()],
            'storyViews': [view.to_dict() for view in user.story_views.limit(50).all()],
            
            # Downloads
            'resourceDownloads': [download.to_dict() for download in user.resource_downloads.limit(50).all()],
            
            # Suggestions
            'suggestions': [suggestion.to_dict() for suggestion in user.suggestions.limit(50).all()],
            
            # Calendar Events
            'calendarEvents': [event.to_dict() for event in user.calendar_events.limit(50).all()],
            
            # Goal Milestones
            'goalMilestones': [milestone.to_dict() for milestone in user.goal_milestones.limit(50).all()]
        },
        
        # Relationship counts for quick overview
        'relationshipCounts': {
            'ideas': user.ideas.count(),
            'knowledgePosts': user.knowledge_posts.count(),
            'startups': user.startups.count(),
            'stories': user.stories.count(),
            'authoredPosts': user.authored_posts.count(),
            'achievements': user.user_achievements.filter_by(is_completed=True).count(),
            'refreshTokens': user.refresh_tokens.count(),
            'sentMessages': user.sent_messages.count(),
            'conversations': user.conversations.count(),
            'growthMetrics': user.growth_metrics.count(),
            'calendarEvents': user.calendar_events.count(),
            'goalMilestones': user.goal_milestones.count()
        }
    }
    
    return user_data
    

# ========================== REGISTER ==========================
@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data.get('email').lower()).first():
            return jsonify({'error': 'User already exists with this email'}), 400
        
        # Create new user
        user = User(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email').lower(),
            password=generate_password_hash(data.get('password')),
            is_email_verified=False,
            status='active',
            role='member'
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token, refresh_token_str = generate_tokens(user.id)
        save_refresh_token(user.id, refresh_token_str)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refreshToken': refresh_token_str,
            'user': get_user_response_data(user)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500


# ========================== LOGIN ==========================
@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email'].lower()).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if user.status.value != 'active':
            return jsonify({'error': 'Account is not active'}), 403
        
        # Update last login and activity date
        user.last_login = datetime.utcnow()
        user.last_activity_date = datetime.utcnow().date()
        db.session.commit()
        
        # Generate tokens
        access_token, refresh_token_str = generate_tokens(user.id)
        save_refresh_token(user.id, refresh_token_str)
        
        return jsonify({
            'success':True,
            'message': 'Login successful',
            'access_token': access_token,
            'refreshToken': refresh_token_str,
            'user': get_user_response_data(user)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500


# ========================== REFRESH TOKEN ==========================
@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Find user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is active
        if user.status.value != 'active':
            return jsonify({'error': 'Account is not active'}), 403
        
        # Generate new access token
        new_access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(hours=6),
            fresh=False
        )
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        print(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500


# ========================== LOGOUT ==========================
@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Delete refresh tokens
        RefreshToken.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


# ========================== GET CURRENT USER ==========================
@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': get_user_response_data(user)
        }), 200
        
    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user data'}), 500


# ========================== CHANGE PASSWORD ==========================
@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not check_password_hash(user.password, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        user.password = generate_password_hash(data['new_password'])
        
        # Delete all refresh tokens (force re-login on all devices)
        RefreshToken.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully. Please login again.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Change password error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500


# ========================== GOOGLE OAUTH ==========================
@bp.route('/google/login')
def google_login():
    """Initiate Google OAuth flow"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    print("🔥 GOOGLE REDIRECT URI:", redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return _oauth_error_response('google', 'Failed to get user info')
        
        # Check if user exists
        user = User.query.filter_by(email=user_info['email'].lower()).first()
        
        if not user:
            # Create new user
            user = User(
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                email=user_info['email'].lower(),
                password=generate_password_hash(
                    f"oauth_google_{user_info['sub']}_{os.urandom(16).hex()}"
                ),
                is_email_verified=True,  # Google emails are verified
                status='active',
                role='member',
                profile_picture=user_info.get('picture')
            )
            db.session.add(user)
            db.session.commit()
        
        # Update last login
        user.last_login = datetime.utcnow()
        user.last_activity_date = datetime.utcnow().date()
        
        # Update profile picture if not set
        if not user.profile_picture and user_info.get('picture'):
            user.profile_picture = user_info.get('picture')
        
        db.session.commit()
        
        # Generate tokens
        access_token, refresh_token_str = generate_tokens(user.id)
        save_refresh_token(user.id, refresh_token_str)
        
        # Return HTML that posts message to parent window
        user_json = jsonify(get_user_response_data(user)).get_data(as_text=True)
        
        return f"""
            <html>
                <script>
                    window.opener.postMessage({{
                        type: 'oauth_success',
                        provider: 'google',
                        access_token: '{access_token}',
                        refreshToken: '{refresh_token_str}',
                        user: {user_json}
                    }}, '*');
                    window.close();
                </script>
            </html>
        """
        
    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        return _oauth_error_response('google', str(e))


def _oauth_error_response(provider, error_message):
    """Helper function to return OAuth error response"""
    return f"""
        <html>
            <script>
                window.opener.postMessage({{
                    type: 'oauth_error',
                    provider: '{provider}',
                    error: '{error_message}'
                }}, '*');
                window.close();
            </script>
        </html>
    """


# ========================== VERIFY EMAIL (PLACEHOLDER) ==========================
@bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email (implement with email service)"""
    try:
        data = request.get_json()
        token = data.get('access_token')
        
        # TODO: Implement email verification logic
        # 1. Verify token
        # 2. Update user.is_email_verified = True
        
        return jsonify({
            'message': 'Email verification endpoint - to be implemented'
        }), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================== REQUEST PASSWORD RESET (PLACEHOLDER) ==========================
@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset (implement with email service)"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email.lower()).first()
        
        # Don't reveal if user exists or not (security)
        # TODO: Implement password reset email logic
        
        return jsonify({
            'message': 'If an account exists with this email, you will receive password reset instructions.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process request'}), 500


# ========================== RESET PASSWORD (PLACEHOLDER) ==========================
@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token (implement with email service)"""
    try:
        data = request.get_json()
        token = data.get('access_token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        # TODO: Implement password reset logic
        # 1. Verify token
        # 2. Update user password
        # 3. Invalidate token
        
        return jsonify({
            'message': 'Password reset endpoint - to be implemented'
        }), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500