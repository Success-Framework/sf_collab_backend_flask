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
    """Get formatted user data for response"""
    # Get computed metrics
    notifications_count = user.notifications.filter_by(is_read=False).count()
    
    # Get active startups count (if you have StartupMember model)
    try:
        from app.models.startUpMember import StartupMember
        active_startups = StartupMember.query.filter_by(
            user_id=user.id,
            is_active=True
        ).count()
    except:
        active_startups = user.active_startups_count
    
    # Get pending tasks count (if you have Task model)
    try:
        from app.models.task import Task
        pending_tasks = Task.query.filter_by(
            user_id=user.id,
            status='in_progress'
        ).count()
    except:
        pending_tasks = 0
    
    user_dict = user.to_dict()
    user_dict.update({
        'notifications_count': notifications_count,
        'pending_tasks_count': pending_tasks,
        'active_startups_count': active_startups
    })
    
    return user_dict


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