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
from app.models.userPermission import UserPermission
from app.models.activity import Activity
from app.utils.helper import utc_now_str
        
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

    # GitHub OAuth
    oauth.register(
        name='github',
        client_id=app.config.get('GITHUB_CLIENT_ID'),
        client_secret=app.config.get('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'read:user user:email'}
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
    
    # ========== DASHBOARD METRICS CALCULATION ==========
    
    # Team Performance Metrics
    team_performance_score = 0
    active_members_count = 0
    completed_tasks_count = 0
    
    try:
        # Get team performance from user's startups
        user_startups = user.startups.all()
        if user_startups:
            # Calculate average team performance
            total_performance = 0
            startup_count = 0
            
            for startup in user_startups:
                # Get latest team performance record for each startup
                latest_performance = startup.team_performance_records.order_by(
                    startup.team_performance_records.created_at.desc()
                ).first()
                
                if latest_performance:
                    total_performance += latest_performance.score_percentage
                    active_members_count += latest_performance.active_members
                    completed_tasks_count += latest_performance.tasks_completed
                    startup_count += 1
            
            if startup_count > 0:
                team_performance_score = round(total_performance / startup_count, 1)
    except:
        team_performance_score = 0
    
    # Project Goals Progress
    project_goals_progress = 0
    milestones_completed = 0
    next_goal = "No active goals"
    
    try:
        user_goals = user.project_goals.all()
        if user_goals:
            completed_goals = [goal for goal in user_goals if goal.status == 'completed']
            milestones_completed = len(completed_goals)
            
            # Calculate overall progress
            total_goals = len(user_goals)
            if total_goals > 0:
                project_goals_progress = round((len(completed_goals) / total_goals) * 100, 1)
            
            # Find next upcoming goal
            upcoming_goals = [goal for goal in user_goals if goal.status == 'in_progress']
            if upcoming_goals:
                next_goal = upcoming_goals[0].title
    except:
        project_goals_progress = 0
    
    # Growth Metrics
    growth_percentage = 0
    user_growth = 0
    revenue_growth = 0
    
    try:
        user_growth_metrics = user.growth_metrics.order_by(
            user.growth_metrics.created_at.desc()
        ).limit(2).all()
        
        if len(user_growth_metrics) >= 2:
            # Calculate growth between last two metrics
            current = user_growth_metrics[0]
            previous = user_growth_metrics[1]
            
            if previous.metric_value > 0:
                growth_percentage = round(
                    ((current.metric_value - previous.metric_value) / previous.metric_value) * 100, 
                    1
                )
        
        # Get user growth from statistics
        user_growth = statistics.get('total_ideas', 0) + statistics.get('total_startups', 0)
        
        # Revenue growth
        revenue_growth = user.total_revenue
        
    except:
        growth_percentage = 0
    
    # Achievements
    achievements_count = user.user_achievements.filter_by(is_completed=True).count()
    this_month_achievements = 0
    try:
        from datetime import datetime
        current_month = datetime.utcnow().month
        this_month_achievements = user.user_achievements.filter(
            user.user_achievements.is_completed == True,
            db.extract('month', user.user_achievements.completed_at) == current_month
        ).count()
    except:
        this_month_achievements = 0
    
    permissions=UserPermission.query.filter_by(user_id=int(user.id)).all()
    
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
        
        # ========== DASHBOARD METRICS ==========
        'dashboardMetrics': {
            'teamPerformance': {
                'score': team_performance_score,
                'activeMembers': active_members_count,
                'tasksCompleted': completed_tasks_count,
                'productivityLevel': 'high' if team_performance_score >= 80 else 'medium' if team_performance_score >= 60 else 'low'
            },
            'projectGoals': {
                'progress': project_goals_progress,
                'milestonesCompleted': milestones_completed,
                'nextGoal': next_goal,
                'totalGoals': len(user.project_goals.all()) if hasattr(user, 'project_goals') else 0
            },
            'growthMetrics': {
                'growthPercentage': growth_percentage,
                'userGrowth': user_growth,
                'revenue': revenue_growth,
                'marketShare': statistics.get('engagement_score', 0)
            },
            'achievements': {
                'total': achievements_count,
                'thisMonth': this_month_achievements,
                'nextTarget': achievements_count + 5  # Next target is 5 more achievements
            }
        },
        
        # Relationship DATA (not just counts)
        'relationships': {
            # Core Authentication & Profile
            'notifications': [notification.to_dict() for notification in user.notifications.limit(50).all()],
            
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
            'unread_count':sum(conversation.get_unread_message_count(user.id) for conversation in user.conversations) ,
            
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
        },
        
        'permissions':[perm.to_dict() for perm in permissions]
    }
    
    return user_data


# ========================== grant default permissions ============
def grant_default_permissions(user_id):
    """Grant default permissions to a new user"""
    from app.models.userPermission import UserPermission
    
    # Get all permissions except AI/Media/Document tools
    from app.models.permission import Permission
    excluded_permissions = Permission.query.filter(
        Permission.category.in_(['AI Tools', 'Media Tools', 'Document Tools'])
        | Permission.key.in_([
            'chat_ai_access',
            'chat_ai_qwen', 
            'chat_ai_gemini',
            'tools_image_generate',
            'tools_image_edit',
            'tools_background_remove',
            'tools_anime_convert',
            'tools_pdf_sign',
            'tools_pdf_edit',
            'tools_logo_generate',
            'tools_business_plan'
        ])
    ).all()
    
    excluded_permission_ids = [p.id for p in excluded_permissions]
    
    # Get all other permissions
    default_permissions = Permission.query.filter(
        ~Permission.id.in_(excluded_permission_ids)
    ).all()
    
    # Grant each permission to the user
    for permission in default_permissions:
        # Check if user already has this permission (shouldn't happen for new users)
        existing = UserPermission.query.filter_by(
            user_id=user_id,
            permission_id=permission.id
        ).first()
        
        if not existing:
            user_permission = UserPermission(
                user_id=user_id,
                permission_id=permission.id,
                granted_by=user_id,  # Or use a system admin ID
                starts_at=datetime.utcnow()
            )
            db.session.add(user_permission)
    
    db.session.commit()
    
    # Log the activity
    from app.models.activity import Activity
    Activity.log(
        action="default_permissions_granted",
        user_id=user_id,
        details=f"Granted {len(default_permissions)} default permissions to new user"
    )
    
    return len(default_permissions)
    
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
        
        # GRANT DEFAULT PERMISSIONS HERE
        try:
            permissions_count = grant_default_permissions(user.id)
            print(f"Granted {permissions_count} default permissions to user {user.id}")
        except Exception as perm_error:
            print(f"Error granting default permissions: {str(perm_error)}")
            
        # Generate tokens
        access_token, refresh_token_str = generate_tokens(user.id)
        save_refresh_token(user.id, refresh_token_str)
        
        # user.update_last_activity()
        from app.models.activity import Activity
        from app.utils.helper import utc_now_str
        
        Activity.log(
            action="user_registered",
            user_id=user.id,
            is_new_user=True,
            details=f"User account successfully created at {utc_now_str()}."
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refreshToken': refresh_token_str,
            'user': get_user_response_data(user),
            'permissions_granted': permissions_count if 'permissions_count' in locals() else 0
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
        
        # Log the activity
        from app.models.activity import Activity
        from app.utils.helper import utc_now_str
        
        Activity.log(
            action="default_permissions_granted",
            user_id=user.id,
            details=f"Successful authentication recorded at {utc_now_str()} UTC."
        )
        
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
        user = User.query.filter_by(email=user_info['email']).first()
        is_new_user = False
        
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
            is_new_user = True
            
        # Update last login
        user.last_login = datetime.utcnow()
        user.last_activity_date = datetime.utcnow().date()
        
        # Update profile picture if not set
        if not user.profile_picture and user_info.get('picture'):
            user.profile_picture = user_info.get('picture')
        
        db.session.commit()
        
        # GRANT DEFAULT PERMISSIONS FOR NEW USERS
        if is_new_user:
            try:
                
                permissions_count = grant_default_permissions(user.id)
                print(f"Granted {permissions_count} default permissions to OAuth user {user.id}")
            except Exception as perm_error:
                print(f"Error granting default permissions to OAuth user: {str(perm_error)}")
            
            Activity.log(
                action="user_registered",
                user_id=user.id,
                is_new_user=True,
                details=f"User account successfully created at {utc_now_str()}."
            )
        Activity.log(
            action="default_permissions_granted",
            user_id=user.id,
            details=f"Successful authentication recorded at {utc_now_str()} UTC."
        )
        
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
                        user: {user_json},
                        is_new_user: {str(is_new_user).lower()}
                    }}, '*');
                    window.close();
                </script>
            </html>
        """
        
    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        return _oauth_error_response('google', str(e))

@bp.route('/github/login')
def github_login():
    """Initiate GitHub OAuth flow"""
    redirect_uri = url_for('auth.github_callback', _external=True)
    print("🔥 GITHUB REDIRECT URI:", redirect_uri)
    return oauth.github.authorize_redirect(redirect_uri)

@bp.route('/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        # Get the token properly
        token = oauth.github.authorize_access_token()
        
        if not token:
            return _oauth_error_response('github', 'No token received')
            
        print(f"GitHub Token: {token}")  # Debug log
        
        # Get user info
        resp = oauth.github.get('user', token=token)
        user_info = resp.json()
        print(f"User Info: {user_info}")  # Debug log
        
        # Get email - GitHub sometimes returns email directly in user info
        email_from_profile = user_info.get('email')
        
        # Try to get emails from API
        resp = oauth.github.get('user/emails', token=token)
        emails_response = resp.json()
        print(f"Emails Response: {emails_response}")  # Debug log
        
        primary_email = None
        
        # Handle different response formats
        if email_from_profile:
            # GitHub returns email in user profile if it's public
            primary_email = email_from_profile
        elif isinstance(emails_response, list):
            # Normal case: list of email objects
            for e in emails_response:
                if isinstance(e, dict):
                    if e.get('primary') and e.get('verified'):
                        primary_email = e['email']
                        break
                elif isinstance(e, str):
                    # Handle case where it might be a list of email strings
                    primary_email = e
                    break
        elif isinstance(emails_response, str):
            # Sometimes it might just return a string email
            primary_email = emails_response
        elif isinstance(emails_response, dict) and 'email' in emails_response:
            # Single email object
            primary_email = emails_response.get('email')
        
        if not primary_email:
            # Try alternative approach - use the token to make a direct request
            try:
                import requests
                headers = {
                    'Authorization': f'token {token["access_token"]}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                email_resp = requests.get(
                    'https://api.github.com/user/emails',
                    headers=headers
                )
                if email_resp.status_code == 200:
                    alt_emails = email_resp.json()
                    print(f"Alternative emails response: {alt_emails}")
                    if isinstance(alt_emails, list):
                        for e in alt_emails:
                            if isinstance(e, dict) and e.get('primary') and e.get('verified'):
                                primary_email = e['email']
                                break
            except Exception as email_error:
                print(f"Alternative email fetch error: {email_error}")
        
        if not primary_email:
            # Last resort: use GitHub username to create placeholder
            username = user_info.get('login')
            if username:
                primary_email = f"{username}@github.oauth"
            else:
                return _oauth_error_response('github', 'No email found and could not create placeholder')
        
        # print(f"Selected email: {primary_email}")  # Debug log
        
        # Check if user exists
        user = User.query.filter_by(email=primary_email).first()
        is_new_user=False
        
        if not user:
            # Create new user
            user = User(
                first_name=user_info.get('name', '').split()[0] if user_info.get('name') else '',
                last_name=' '.join(user_info.get('name', '').split()[1:]) if user_info.get('name') else '',
                email=primary_email.lower(),
                password=generate_password_hash(
                    f"oauth_github_{user_info['id']}_{os.urandom(16).hex()}"
                ),
                is_email_verified=('@github.oauth' not in primary_email),  # Only verify if real email
                status='active',
                role='member',
                profile_picture=user_info.get('avatar_url')
            )
            db.session.add(user)
            db.session.commit()

        # Update last login and activity
        user.last_login = datetime.utcnow()
        user.last_activity_date = datetime.utcnow().date()
        db.session.commit()
        is_new_user=True
        
        
        if is_new_user:
            try:
                permissions_count = grant_default_permissions(user.id)
                print(f"Granted {permissions_count} default permissions to OAuth user {user.id}")
            except Exception as perm_error:
                print(f"Error granting permissions: {str(perm_error)}")
            
            Activity.log(
                action="user_registered",
                user_id=user.id,
                is_new_user=True,
                details=f"User account successfully created at {utc_now_str()}."
            )
        Activity.log(
            action="default_permissions_granted",
            user_id=user.id,
            details=f"Successful authentication recorded at {utc_now_str()} UTC."
        )
        
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
                        provider: 'github',
                        access_token: '{access_token}',
                        refreshToken: '{refresh_token_str}',
                        user: {user_json}
                    }}, '*');
                    window.close();
                </script>
            </html>
        """

    except Exception as e:
        print(f"GitHub OAuth error: {str(e)}")
        import traceback
        traceback.print_exc()
        return _oauth_error_response('github', str(e))
        

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
