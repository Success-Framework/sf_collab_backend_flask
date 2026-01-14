from flask import Blueprint, request, jsonify, redirect, url_for
from app.extensions import oauth, db
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from app.config import Config
from app.models.user import User
from app.models.refreshToken import RefreshToken
from app.models.userPermission import UserPermission
from app.models.activity import Activity
from app.utils.helper import utc_now_str
from app.models.waitlist import Waitlist
from app.models.chatConversation import ChatConversation
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from app.services.email_service import EmailService
from app.utils.helper import success_response, error_response
bp = Blueprint('auth', __name__)
from app.utils.email_templates.email_templates import templates
email_service = EmailService()
thank_email_template = templates.get("welcome_email")
def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth.init_app(app)
    if not app.config.get("GOOGLE_CLIENT_ID"):
        raise RuntimeError("GOOGLE_CLIENT_ID is not set")

    if not app.config.get("GOOGLE_CLIENT_SECRET"):
        raise RuntimeError("GOOGLE_CLIENT_SECRET is not set")

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
    user_data = user.to_dict()
    return user_data


# ========================== grant default permissions ============
def grant_default_permissions(user_id):
    """Grant default permissions to a new user (excludes admin and premium features)"""
    from app.models.userPermission import UserPermission
    from datetime import datetime
    
    # Get all permissions except Admin, AI, Media, and Document tools
    from app.models.permission import Permission
    
    # Define excluded categories AND specific permission keys
    excluded_categories = ['Administration', 'AI Tools', 'Media Tools', 'Document Tools']
    
    excluded_permission_keys = [
        'admin',
        'admin_dashboard',
        'user_management',
        'content_moderation',
        'system_settings',
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
    ]
    
    # Get excluded permissions
    try:
        excluded_permissions = Permission.query.filter(
            Permission.category.in_(excluded_categories)
            | Permission.key.in_(excluded_permission_keys)
        ).all()
    except Exception as e:
        print(f"Error querying permissions table: {str(e)}")
        # If permissions table doesn't exist, return 0 (no permissions granted)
        return 0
    
    excluded_permission_ids = [p.id for p in excluded_permissions]
    
    # Get all other permissions (non-admin, non-premium)
    default_permissions = Permission.query.filter(
        ~Permission.id.in_(excluded_permission_ids)
    ).all()
    
    # Grant each permission to the user
    permissions_granted = 0
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
            permissions_granted += 1
    
    if permissions_granted > 0:
        db.session.commit()
    
    # Log the activity
    from app.models.activity import Activity
    Activity.log(
        action="default_permissions_granted",
        user_id=user_id,
        details=f"Granted {permissions_granted} default permissions to new user (excluded admin/premium)"
    )
    
    return permissions_granted
    
# ========================== REGISTER ==========================
@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        # print('Hola')
        referral_code = data.get("referralCode", None)
        # print(f'Referral code received: {referral_code}')
        
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
        if referral_code:
            Waitlist.give_points(referral_code,Waitlist.POINTS_PER_REFERRAL, 'referral' )
        
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
            details=f"User account successfully created at {utc_now_str()}."
        )
        brand_name = os.getenv("BRAND_NAME", "SFCollab")
        # Add user to general chat
        ChatConversation.add_to_general_chat(user)
        try:
            email_service.send_email(user.email, f"Welcome to {brand_name}!",
                                                    thank_email_template(
                                                    data={
                                                        "user": {
                                                        "name": f"{user.first_name} {user.last_name}",
                                                        "email": user.email
                                                        }
                                                    },
                                                    see_email_template=False
                                                ))
        except Exception as email_error:
            print(f"Error sending welcome email: {str(email_error)}")
            pass
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
            return jsonify({'error': 'Invalid credentials', 'message': 'User not found'}), 401
        if user.status == 'banned':
            return jsonify({'error': 'Account is banned. Please contact support.'}), 403
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
        print(f'LLegamos aqui con user_id: {user_id}')
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
    from flask import session
    session["referral_code"] = request.args.get("ref")

    session.permanent = True
    session.modified = True

    redirect_uri = Config.GOOGLE_REDIRECT_URI
    print("🔥 GOOGLE REDIRECT URI:", redirect_uri)
    print(f"🔥 Session before redirect: {dict(session)}")
    print(f"🔥 Cookies: {request.cookies}")
    response = oauth.google.authorize_redirect(redirect_uri)
    print(f"🔥 Session after redirect: {dict(session)}")
    return response


@bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    from flask import session

    session.permanent = True
    session.modified = True

    print(f"🔥 Callback session: {dict(session)}")
    print(f"🔥 Callback cookies: {request.cookies}")
    print(f"🔥 Callback query params: {request.args}")
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return _oauth_error_response('google', 'Failed to get user info')
        
        # Check if user exists
        user = User.query.filter_by(email=user_info['email']).first()
        is_new_user = False
        referral_code = session.pop("referral_code", None)

        

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
            if referral_code:
                Waitlist.give_points(referral_code,Waitlist.POINTS_PER_REFERRAL, 'referral' )
            
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
                brand_name = os.getenv("BRAND_NAME", "SFCollab")
                permissions_count = grant_default_permissions(user.id)
                print(f"Granted {permissions_count} default permissions to OAuth user {user.id}")
                ChatConversation.add_to_general_chat(user)
        
                email_service.send_email(user.email, f"Welcome to {brand_name}!",
                        thank_email_template(
                                data={
                                    "user": {
                                        "name": f"{user.first_name} {user.last_name}",
                                        "email": user.email
                                }
                            },
                            see_email_template=False
                        ))
            except Exception as perm_error:
                print(f"Error granting default permissions to OAuth user: {str(perm_error)}")
            
            Activity.log(
                action="user_registered",
                user_id=user.id,
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
    
    redirect_uri = Config.GITHUB_REDIRECT_URI
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
                brand_name = os.getenv("BRAND_NAME", "SFCollab")
                permissions_count = grant_default_permissions(user.id)
                ChatConversation.add_to_general_chat(user)
        
                email_service.send_email(user.email, f"Welcome to {brand_name}!",
                        thank_email_template(
                                data={
                                    "user": {
                                        "name": f"{user.first_name} {user.last_name}",
                                        "email": user.email
                                }
                            },
                            see_email_template=False
                        ))
                print(f"Granted {permissions_count} default permissions to OAuth user {user.id}")
            except Exception as perm_error:
                print(f"Error granting permissions: {str(perm_error)}")
            
            Activity.log(
                action="user_registered",
                user_id=user.id,
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

@bp.route('/send-verification-code', methods=['POST'])
@jwt_required()
def send_verification_code():
    import random
    from flask_jwt_extended import create_access_token
    from datetime import timedelta
    """Send email verification code (implement with email service)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user.email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=user.email.lower()).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404
        code = random.randint(100000, 999999)
        verification_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=10),
            additional_claims={'code': code}
        )

        
        email_service.send_email_verification_code(user, code)
        print(f"Sent verification code {code} to {user.email}")
        return jsonify({
            'message': 'Verification code sent to email',
            'verification_token': verification_token
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================== VERIFY EMAIL (PLACEHOLDER) ==========================
@bp.route('/verify-code', methods=['POST'])
@jwt_required()
def verify_code():
    claims = get_jwt()
    data = request.get_json()
    parsed_token = claims.get("code")
    submitted_code = data.get("code")

    if str(parsed_token) != str(submitted_code):
        return error_response(data={
            "verified": False
        }, message="Invalid code", status=400)

    return success_response({
        "verified": True
    }, "Code verified")



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
